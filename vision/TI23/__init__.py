import cv2

from cfg import lower_red1, lower_red2, upper_red1, upper_red2
from ctyper import Array, Image, ObjDetected


def filter_box(raw_results: list[ObjDetected], frame: Image) -> list[ObjDetected]:
    results: list[ObjDetected] = []
    for result in raw_results:
        cx: float = (result.box.x0 + result.box.x1) / 2
        cy: float = (result.box.y0 + result.box.y1) / 2
        w: int = result.box.x1 - result.box.x0
        h: int = result.box.y1 - result.box.y0
        # if it is not a square, skip
        if not abs(w - h) / (w + h) < 0.04:
            # create roi
            roi: Image = cv2.cvtColor(
                frame[
                    int(cy - 0.17 * h) : int(cy + 0.17 * h),
                    int(cx - 0.17 * w) : int(cx + 0.17 * w),
                ],
                cv2.COLOR_BGR2HSV,
            )
            # creat mask
            mask: Array = cv2.inRange(roi, lower_red1, upper_red1) + cv2.inRange(
                roi, lower_red2, upper_red2
            )
            # new score
            result.score = len(mask[mask > 0]) / len(mask)
            result.clsid = 1
        results.append(result)
    return results
