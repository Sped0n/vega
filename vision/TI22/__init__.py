import cv2
import numpy as np

from ctyper import Array, Image, MatNotValid, NotFoundError, Number

from .utils import HulaROI, array2image, close_op, open_op, p2p_distance, simple_dilate


class plane_detect_hulaloop:
    def __init__(
        self, src: Array, diameter_range: tuple[int, int] = (700, 1000)
    ) -> None:
        """
        detect hula loop in plane scan
        """
        try:
            assert src.shape == (92, 160)
        except AssertionError:
            raise MatNotValid("Input array shape is not (92, 160)")
        # get the center slice of depth array
        mid: Array = src[33:53]
        # filter the depth value
        mid = np.where(np.logical_and(mid <= 1800, mid >= 300), mid, 0)
        # convert to image in favor of opencv
        self.__disp: Image = array2image(mid, 1900)

        # perform open operation, eliminate noise pixel
        mid_image = open_op(self.__disp, (3, 3))
        # perform close operation with vertical kernel, fill the vertical gap
        mid_image = open_op(mid_image, (1, 10))
        # perform close operation with horizontal kernel, fill the horizontal gap
        mid_image = close_op(mid_image, (5, 1))

        # perform dilate on objects, enlarge potential objects
        mid_image = simple_dilate(mid_image, (2, 3), 3)

        # pad the top and bottom of image, make contour detection easier
        mid_image = np.vstack(
            [
                np.zeros((5, mid_image.shape[1]), np.uint8),
                mid_image,
                np.zeros((5, mid_image.shape[1]), np.uint8),
            ]
        )

        # find contours
        raw_cnts, _ = cv2.findContours(
            mid_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        raw_results: list[HulaROI] = []

        self.res_valid: bool = False

        for cnt in raw_cnts:
            x, y, w, h = cv2.boundingRect(cnt)
            # filter based on contour area
            if not 130 <= cv2.contourArea(cnt) <= 350:
                continue
            # filter based on contour aspect ratio
            if not h / w > 1.2:
                continue
            roi_rec = mid[y : y + h, x : x + w]
            cx = int(x + w // 2)
            """
            for angle, left is negative, right is positive
                        0
                        |
                    -   |   +
                        |
                    L   |   R
             -90 _______________ 90
            """
            angle = (cx - 80) / 160 * 86
            roi_valid = np.sort(roi_rec[roi_rec > 0])
            # remove the maximum and minimum values
            roi_valid = roi_valid[
                int(len(roi_valid) * 0.15) : int(len(roi_valid) * 0.85)
            ]
            # filter based on roi variance
            if not 1 <= np.var(roi_valid) <= 200:  # type: ignore
                continue
            raw_results.append(
                HulaROI(0, 0, x, y, w, h, angle, float(np.average(roi_valid)))  # type: ignore  # noqa: E501
            )

        self.__results: list[HulaROI] = []
        # over 2 results, abandon
        if len(raw_results) != 2:
            return None
        # reorganize the results
        for result in raw_results:
            # Normal coordinate system, x positive half axis to the right,
            # y positive half axis to the top
            result.y = result.distance * np.cos((result.angle / 180) * np.pi)
            result.x = result.distance * np.sin((result.angle / 180) * np.pi)

        # or if we have 2 results, but the distance between them is too large, abandon
        if min(diameter_range) <= (
            p2p_distance(
                raw_results[0].x, raw_results[1].x, raw_results[0].y, raw_results[1].y
            )
            <= max(diameter_range)
        ):
            return None
        self.res_valid = True
        for result in raw_results:
            self.__results.append(result)

    @property
    def x_and_angle_differ(self) -> tuple[int, int]:
        """
        return the difference of x and angle
        """
        if self.res_valid is False:
            raise NotFoundError("No result found")
        plane_differ_slope = (self.__results[0].y - self.__results[1].y) / (
            self.__results[0].x - self.__results[1].x
        )
        cx, cy = self.cx_and_cy
        x_differ = int(cx + plane_differ_slope * cy)
        yaw_differ = int(np.arctan(-1 / plane_differ_slope) * 180 / np.pi)
        if yaw_differ < 0:
            yaw_differ = -90 - yaw_differ
        else:
            yaw_differ = 90 - yaw_differ
        return x_differ, yaw_differ

    @property
    def cx_and_cy(self) -> tuple[Number, Number]:
        if self.res_valid is False:
            raise NotFoundError("No result found")
        cx = (self.__results[0].x + self.__results[1].x) / 2
        cy = (self.__results[0].y + self.__results[1].y) / 2
        return cx, cy

    @property
    def visual_debug(self) -> Image:
        self.__disp = cv2.cvtColor(self.__disp, cv2.COLOR_GRAY2BGR)
        # if self.results not valid, return the original image
        if self.res_valid is False:
            return self.__disp
        for result in self.__results:
            cv2.rectangle(
                self.__disp,
                (result.bx, min(result.by - 5, 158)),
                (result.bx + result.bw, min(result.by + result.bh - 5, 158)),
                (0, 255, 0),
                1,
            )
        return self.__disp
