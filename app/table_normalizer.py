import cv2
import numpy as np


class TableNormalizer:

    WIDTH = 2200
    HEIGHT = 3200

    def normalize(self, image, binary):

        contour = self._largest_contour(binary)

        if contour is None:
            raise Exception("Table not found")

        corners = self._find_corners(contour)

        warped = self._warp(image, corners)

        warped = cv2.resize(
            warped,
            (self.WIDTH, self.HEIGHT)
        )

        return warped

    def _largest_contour(self, binary):

        contours, _ = cv2.findContours(
            binary,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        largest = None
        area = 0

        for cnt in contours:

            a = cv2.contourArea(cnt)

            if a > area:
                area = a
                largest = cnt

        return largest

    def _find_corners(self, contour):

        epsilon = 0.02 * cv2.arcLength(contour, True)

        approx = cv2.approxPolyDP(
            contour,
            epsilon,
            True
        )

        if len(approx) != 4:
            x, y, w, h = cv2.boundingRect(contour)

            return np.array([
                [x, y],
                [x + w, y],
                [x + w, y + h],
                [x, y + h]
            ], dtype=np.float32)

        pts = approx.reshape(4, 2)

        return self._order(pts)

    def _order(self, pts):

        rect = np.zeros((4, 2), dtype=np.float32)

        s = pts.sum(axis=1)

        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        d = np.diff(pts, axis=1)

        rect[1] = pts[np.argmin(d)]
        rect[3] = pts[np.argmax(d)]

        return rect

    def _warp(self, image, pts):

        dst = np.array([
            [0, 0],
            [self.WIDTH, 0],
            [self.WIDTH, self.HEIGHT],
            [0, self.HEIGHT]
        ], dtype=np.float32)

        matrix = cv2.getPerspectiveTransform(
            pts,
            dst
        )

        return cv2.warpPerspective(
            image,
            matrix,
            (self.WIDTH, self.HEIGHT)
        )