import cv2
import numpy as np

from ctyper import Array, Image, NotFoundError, Number

from .utils import array2image, close_op, open_op, simple_dilate, HulaROI, p2p_distance


class plane_detect_hulaloop:
    def __init__(self, src: Array) -> None:
        """
        detect hula loop in plane scan
        """
        # get the center slice of depth array
        mid: Array = src[33:53]
        # filter the depth value
        mid = np.where(np.logical_and(mid <= 1800, mid >= 300), mid, 0)
        # convert to image in favor of opencv
        self.disp: Image = array2image(mid, 1900)

        # perform open operation, eliminate noise pixel
        mid_image = open_op(self.disp, (3, 3))
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
            if not 1 <= np.var(roi_valid) <= 200:
                continue
            raw_results.append(
                HulaROI(0, 0, x, y, w, h, angle, float(np.average(roi_valid)))
            )

        self.results: list[HulaROI] = []
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
        if 730 <= (
            p2p_distance(
                raw_results[0].x, raw_results[1].x, raw_results[0].y, raw_results[1].y
            )
            <= 930
        ):
            return None
        for result in raw_results:
            self.results.append(result)

    @property
    def valid(self) -> bool:
        """
        return the validity of results
        """
        return len(self.results) == 2

    @property
    def x_and_angle_differ(self) -> tuple[int, int]:
        """
        return the difference of x and angle
        """
        if len(self.results) != 2:
            raise NotFoundError("No result found")
        plane_differ_slope = (self.results[0].y - self.results[1].y) / (
            self.results[0].x - self.results[1].x
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
        if len(self.results) != 2:
            raise NotFoundError("No result found")
        cx = (self.results[0].x + self.results[1].x) / 2
        cy = (self.results[0].y + self.results[1].y) / 2
        return cx, cy

    @property
    def visual_debug(self) -> Image:
        self.disp = cv2.cvtColor(self.disp, cv2.COLOR_GRAY2BGR)
        # if self.results not valid, return the original image
        if len(self.results) != 2:
            return self.disp
        for result in self.results:
            cv2.rectangle(
                self.disp,
                (result.bx, result.by),
                (result.bx + result.bw, result.by + result.bh),
                (0, 255, 0),
                1,
            )
        return self.disp