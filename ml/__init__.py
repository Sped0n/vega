import os
from pathlib import Path

import cv2
import ncnn
import numpy as np
import onnxruntime as ort

from ctyper import (
    Array,
    Image,
    InferExtractError,
    InputSize,
    MLPreprocessParams,
    ObjDetected,
)

from .utils import post_process, preprocess_params_gen


class _NcnnModel:
    def __init__(
        self,
        filename: str,
        input_size: InputSize,
        num_threads: int = 2,
        use_gpu: bool = False,
        use_big_core: bool = True,
        light_mode: bool = True,
    ) -> None:
        self.reinit_with(
            filename,
            input_size,
            num_threads,
            use_gpu,
            use_big_core,
            light_mode,
        )

    def reinit_with(
        self,
        filename: str,
        input_size: InputSize,
        num_threads: int = 2,
        use_gpu: bool = False,
        use_big_core: bool = True,
        light_mode: bool = True,
    ) -> None:
        try:
            if self.loaded is True:
                self.clear()
        except AttributeError as e:
            assert "has no attribute 'loaded'" in str(e)
        self.bin: Path = Path(os.path.splitext(filename)[0] + ".bin")
        self.param: Path = Path(os.path.splitext(filename)[0] + ".param")
        if input_size.w != input_size.h:
            raise NotImplementedError("currently rect input is not supported")
        self.input_size: InputSize = input_size
        self.num_threads = num_threads
        self.use_gpu = use_gpu
        self.use_big_core = use_big_core
        self.light_mode = light_mode
        if not self.bin.exists() or not self.param.exists():
            raise FileNotFoundError("Ncnn model file not found")
        self.loaded: bool = False

    def load(self):
        """
        Load the model file and set backend
        """
        # Arm big little
        governor_mode: int = 2 if self.use_big_core else 1
        ncnn.set_cpu_powersave(governor_mode)
        # initialize runner
        self.__runner = ncnn.Net()
        # set opts
        self.__runner.opt.num_threads = self.num_threads
        self.__runner.opt.use_vulkan_compute = self.use_gpu
        self.__runner.opt.lightmode = self.light_mode
        # load file
        self.__runner.load_param(str(self.param.absolute()))
        self.__runner.load_model(str(self.bin.absolute()))
        self.loaded = True

    def __preprocess(self, frame: Image) -> ncnn.Mat:
        self.pps_params: MLPreprocessParams = preprocess_params_gen(
            frame, self.input_size
        )
        resized_frame: ncnn.Mat = ncnn.Mat.from_pixels_resize(
            frame,
            ncnn.Mat.PixelType.PIXEL_BGR2RGB,  # type: ignore
            self.pps_params.w0,
            self.pps_params.h0,
            self.pps_params.w1,
            self.pps_params.h1,
        )
        padded_frame: ncnn.Mat = ncnn.copy_make_border(
            resized_frame,
            self.pps_params.dh,
            self.pps_params.hpad - self.pps_params.dh,
            self.pps_params.dw,
            self.pps_params.wpad - self.pps_params.dw,
            ncnn.BorderType.BORDER_CONSTANT,  # type: ignore
            0.0,
        )
        padded_frame.substract_mean_normalize([], [1 / 255.0, 1 / 255.0, 1 / 255.0])
        return padded_frame

    def infer(
        self, frame: Image, conf_thres: float = 0.25, nms_thres: float = 0.65
    ) -> list[ObjDetected]:
        """
        run inference on the given frame
        """
        assert self.__runner is not None
        ex: ncnn.Extractor = self.__runner.create_extractor()
        mat_in = self.__preprocess(frame)
        ex.input("images", mat_in)  # type: ignore
        ret1, mat_out1 = ex.extract("output0")  # stride 8
        if ret1 != 0:
            raise InferExtractError("ncnn extract output0 with something wrong!")
        ret2, mat_out2 = ex.extract("output1")  # stride 16
        if ret2 != 0:
            raise InferExtractError("extract output1 with something wrong!")
        ret3, mat_out3 = ex.extract("output2")  # stride 32
        if ret3 != 0:
            raise InferExtractError("extract output2 with something wrong!")
        outputs = (np.array(mat_out1), np.array(mat_out2), np.array(mat_out3))
        results = post_process(outputs, self.pps_params, conf_thres, nms_thres)
        return results

    def clear(self) -> None:
        """
        clear the model
        """
        self.__runner.clear()
        del self.__runner
        self.loaded = False


class _OrtModel:
    def __init__(self, filename: str, input_size: InputSize) -> None:
        self.reinit_with(filename, input_size)

    def reinit_with(self, filename: str, input_size: InputSize) -> None:
        try:
            if self.loaded is True:
                self.clear()
        except AttributeError as e:
            assert "has no attribute 'loaded'" in str(e)
        self.onnx: Path = Path(os.path.splitext(filename)[0] + ".onnx")
        self.input_size: InputSize = input_size
        if not self.onnx.exists():
            raise FileNotFoundError("Onnx model file not found")
        self.loaded: bool = False

    def load(self) -> None:
        """
        load the model file and set backend
        """
        self.__runner = ort.InferenceSession(str(self.onnx.absolute()))
        self.loaded = True

    def __preprocess(self, frame: Image) -> Array:
        self.pps_params: MLPreprocessParams = preprocess_params_gen(
            frame, self.input_size
        )
        interp = cv2.INTER_LINEAR if (self.pps_params.scale > 1) else cv2.INTER_AREA
        resized_frame: Image = cv2.resize(
            frame, (self.pps_params.w1, self.pps_params.h1), interpolation=interp
        )
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        padded_frame: Image = cv2.copyMakeBorder(
            resized_frame,
            self.pps_params.dh,
            self.pps_params.hpad - self.pps_params.dh,
            self.pps_params.dw,
            self.pps_params.wpad - self.pps_params.dw,
            cv2.BORDER_CONSTANT,
            0.0,
        )
        tensor: Array = np.array(padded_frame) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0).astype(np.float32)
        return tensor

    def infer(
        self, frame: Image, conf_thres: float = 0.25, nms_thres: float = 0.65
    ) -> list[ObjDetected]:
        """
        run inference on the given frame
        """
        assert self.loaded is True
        tensor_in: Array = self.__preprocess(frame)
        mat1, mat2, mat3 = self.__runner.run(
            ["output0", "output1", "output2"], {"images": tensor_in}
        )
        outputs = (np.array(mat1), np.array(mat2), np.array(mat3))
        results = post_process(outputs, self.pps_params, conf_thres, nms_thres)
        return results

    def clear(self) -> None:
        """
        clear the model
        """
        del self.__runner
        self.loaded = False


class Model:
    def __init__(self, filename: str, input_size: InputSize, backend_type: str) -> None:
        self.backend_type: str = backend_type
        # (w, h)
        if self.backend_type == "ort":
            self.model = _OrtModel(filename, input_size)
        elif self.backend_type == "ncnn":
            self.model = _NcnnModel(filename, input_size)
        else:
            raise ValueError("Invalid backend")
        self.model.load()

    def infer(
        self, frame: Image, conf_thres: float = 0.25, nms_thres: float = 0.65
    ) -> list[ObjDetected]:
        return self.model.infer(frame, conf_thres, nms_thres)

    def clear(self) -> None:
        self.model.clear()

    def reinit(self, filename: str, input_size: InputSize) -> None:
        self.model.reinit_with(filename, input_size)
        self.model.load()
