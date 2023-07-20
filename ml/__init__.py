from pathlib import Path

import cv2
import ncnn
import numpy as np
import onnxruntime as ort

from ctyper import Array, Image, InputSize

from .utils import preprocess_params_gen


class NcnnModel:
    def __init__(
        self,
        filename: str,
        input_size: InputSize,
        num_threads: int = 2,
        use_gpu: bool = False,
        use_big_core: bool = True,
    ) -> None:
        self.bin: Path = Path(filename + ".bin")
        self.param: Path = Path(filename + ".param")
        if input_size.w != input_size.h:
            raise NotImplementedError("currently rect input is not supported")
        self.input_size: InputSize = input_size
        self.num_threads = num_threads
        self.use_gpu = use_gpu
        self.use_big_core = use_big_core
        if not self.bin.exists() or not self.param.exists():
            raise FileNotFoundError("Ncnn model file not found")

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
        # load file
        self.__runner.load_param(str(self.param.absolute()))
        self.__runner.load_model(str(self.bin.absolute()))

    def __preprocess(self, frame: Image) -> ncnn.Mat:
        params = preprocess_params_gen(frame, self.input_size)
        resized_frame: ncnn.Mat = ncnn.Mat.from_pixels_resize(
            frame,
            ncnn.Mat.PixelType.PIXEL_BGR2RGB,  # type: ignore
            params.w0,
            params.h0,
            params.w1,
            params.h1,
        )
        padded_frame: ncnn.Mat = ncnn.copy_make_border(
            resized_frame,
            params.hpad // 2,
            params.hpad - params.hpad // 2,
            params.wpad // 2,
            params.wpad - params.wpad // 2,
            ncnn.BorderType.BORDER_CONSTANT,  # type: ignore
            0.0,
        ).substract_mean_normalize([], [1 / 255.0, 1 / 255.0, 1 / 255.0])
        return padded_frame


class OrtModel:
    def __init__(self, filename: str, input_size: InputSize) -> None:
        self.onnx: Path = Path(filename + ".onnx")
        self.input_size: InputSize = input_size
        if not self.onnx.exists():
            raise FileNotFoundError("Onnx model file not found")

    def load(self):
        """
        Load the model file and set backend
        """
        self.__runner = ort.InferenceSession(str(self.onnx.absolute()))

    def __preprocess(self, frame: Image) -> Array:
        w0: int = frame.shape[1]
        h0: int = frame.shape[0]

        w1: int = w0
        h1: int = w1
        wpad: int = 0
        hpad: int = 0
        scale: float = 1.0
        if w0 > h0:
            scale = float(InputSize.w / w0)
            w1 = InputSize.w
            h1 = int(h0 * scale)
            wpad = 0
            hpad = InputSize.h - h1
        else:
            scale = float(InputSize.h / h0)
            h1 = InputSize.h
            w1 = int(w0 * scale)
            hpad = 0
            wpad = InputSize.w - w1
        interp = cv2.INTER_LINEAR if (scale > 1) else cv2.INTER_AREA
        resized_frame: Image = cv2.resize(frame, (w1, h1), interpolation=interp)
        resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        padded_frame: Image = cv2.copyMakeBorder(
            resized_frame,
            hpad // 2,
            hpad - hpad // 2,
            wpad // 2,
            wpad - wpad // 2,
            cv2.BORDER_CONSTANT,
            0.0,
        )
        tensor: Array = np.array(padded_frame) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0).astype(np.float32)
        return tensor


class Model:
    def __init__(self, filename: str, input_size: InputSize, backend_type: str):
        self.backend_type: str = backend_type
        # (w, h)
        if self.backend_type == "ort":
            self.model = OrtModel(filename, input_size)
        elif self.backend_type == "ncnn":
            self.model = NcnnModel(filename, input_size)
        else:
            raise ValueError("Invalid backend")
        self.model.load()

    def infer(self):
        pass
