import cv2
import numpy as np


class CheckboxDetector:

    def darkness(self, roi):

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY
        )

        binary = cv2.threshold(
            gray,
            180,
            255,
            cv2.THRESH_BINARY_INV
        )[1]

        pixels = cv2.countNonZero(binary)

        area = roi.shape[0] * roi.shape[1]

        return pixels / area
    
    def detect_row(self, image, boxes):

        scores = []

        for box in boxes:

            roi = image[
                box.y:box.y + box.height,
                box.x:box.x + box.width
            ]

            score = self.darkness(roi)

            scores.append(score)

        best = max(scores)

        if best < 0.08:
            return None

        return scores.index(best)
    
    def detect_page(self, image, grid):

        result = [0, 0, 0, 0, 0]

        for row in range(42):

            boxes = []

            for box in grid:

                if box.row == row + 1:
                    boxes.append(box)

            answer = self.detect_row(image, boxes)

            if answer is not None:
                result[answer] += 1

        return result