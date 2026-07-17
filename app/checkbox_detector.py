from statistics import median

import cv2

from app.config import MANIFESTATIONS, MARK_THRESHOLD


class CheckboxDetector:
    """Find checklist boxes from the page instead of relying on fixed row offsets."""

    # The pages are normalized to 2200 pixels wide.  Partial final pages can
    # be stretched vertically by perspective normalization, so their boxes
    # may be much taller while retaining the same width.
    MIN_BOX_SIZE = 27
    MAX_BOX_WIDTH = 75
    MAX_BOX_HEIGHT = 220
    COLUMN_TOLERANCE = 45
    ROW_TOLERANCE = 45

    def detect_page(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        boxes = self._find_checkbox_boxes(gray)
        columns = self._find_columns(boxes)
        rows = self._find_rows(boxes, columns)

        if len(columns) != len(MANIFESTATIONS):
            return []

        box_width, box_height = self._typical_box_size(boxes, columns)
        responses = []
        for row_y in rows:
            scores = [
                self._mark_score(gray, column_x, row_y, box_width, box_height)
                for column_x in columns
            ]
            best_score = max(scores)
            # Light, thin ticks in some exported forms occupy much less ink
            # than the darker marks in the original template.
            threshold = 0.05
            responses.append(
                MANIFESTATIONS[scores.index(best_score)]
                if best_score >= threshold
                else None
            )

        return responses

    def _find_checkbox_boxes(self, gray):
        _, binary = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        page_height, page_width = gray.shape
        for contour in contours:
            x, y, width, height = cv2.boundingRect(contour)
            aspect_ratio = width / height

            # Checkbox columns occupy the right half of the table.  This
            # excludes the indicator text, while the dimension/aspect filters
            # exclude letters and table rules.
            small_box = (
                self.MIN_BOX_SIZE <= width <= 40
                and (
                    self.MIN_BOX_SIZE <= height <= 70
                    or 70 <= height <= self.MAX_BOX_HEIGHT
                )
                and 0.12 <= aspect_ratio <= 1.25
            )
            large_box = (
                55 <= width <= self.MAX_BOX_WIDTH
                and 55 <= height <= 120
                and 0.50 <= aspect_ratio <= 1.25
            )
            if (
                x <= page_width * 0.50
                or y <= 0
                or y + height >= page_height
                or not (small_box or large_box)
            ):
                continue

            boxes.append((x + width / 2, y + height / 2, width, height))

        return boxes

    def _find_columns(self, boxes):
        groups = self._cluster([x for x, _, _, _ in boxes], self.COLUMN_TOLERANCE)
        if len(groups) < len(MANIFESTATIONS):
            return []

        # Real checkbox columns repeat for nearly every row; text artifacts do
        # not.  A median is resistant to an occasional mark joined to a border.
        strongest = sorted(groups, key=len, reverse=True)[:len(MANIFESTATIONS)]
        return sorted(median(group) for group in strongest)

    def _find_rows(self, boxes, columns):
        candidate_y = [
            y for x, y, _, _ in boxes
            if any(abs(x - column) <= self.COLUMN_TOLERANCE for column in columns)
        ]
        rows = []

        for group in self._cluster(candidate_y, self.ROW_TOLERANCE):
            row_y = median(group)
            matching_columns = sum(
                any(
                    abs(x - column) <= self.COLUMN_TOLERANCE
                    and abs(y - row_y) <= self.ROW_TOLERANCE
                    for x, y, _, _ in boxes
                )
                for column in columns
            )

            # A checked box can merge with its tick and disappear as a square
            # contour, but the three other boxes remain.  Requiring three
            # columns rejects heading text that happens to look box-shaped.
            if matching_columns >= 3:
                rows.append(row_y)

        # A first page with a title/header can contain box-shaped letter forms
        # above the actual checklist.  Its real small boxes are taller than
        # usual, while continuation pages retain the standard box height.
        typical_height = median(height for _, _, _, height in boxes)
        header_like_boxes = sum(y < 300 for _, y, _, _ in boxes)
        if typical_height > 45 and header_like_boxes > 12:
            rows = [row_y for row_y in rows if row_y >= 300]

        return rows

    def _typical_box_size(self, boxes, columns):
        matching_boxes = [
            (width, height)
            for x, _, width, height in boxes
            if any(abs(x - column) <= self.COLUMN_TOLERANCE for column in columns)
        ]
        return (
            median(width for width, _ in matching_boxes),
            median(height for _, height in matching_boxes),
        )

    @staticmethod
    def _cluster(values, tolerance):
        groups = []
        for value in sorted(values):
            if not groups or value - groups[-1][-1] > tolerance:
                groups.append([value])
            else:
                groups[-1].append(value)
        return groups

    @staticmethod
    def _mark_score(gray, center_x, center_y, box_width, box_height):
        # Use the inside of each box only; the outline itself is not evidence
        # that a checkbox is selected.
        if box_width <= 40:
            half_width = half_height = 16
            inset = 6
        else:
            half_width = round(box_width / 2 + 2)
            half_height = round(box_height / 2 + 2)
            inset = max(4, round(min(box_width, box_height) * 0.18))
        roi = gray[
            int(center_y - half_height):int(center_y + half_height),
            int(center_x - half_width):int(center_x + half_width),
        ]
        roi = roi[inset:-inset, inset:-inset]

        _, binary = cv2.threshold(roi, 180, 255, cv2.THRESH_BINARY_INV)
        return cv2.countNonZero(binary) / binary.size
