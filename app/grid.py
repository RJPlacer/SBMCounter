from dataclasses import dataclass

from app.config import COLUMN_COUNT, ROW_COUNT


@dataclass
class Checkbox:
    row: int
    column: int
    x: int
    y: int
    width: int
    height: int


class CheckboxGrid:

    # Standardized normalized image size
    IMAGE_WIDTH = 2200
    IMAGE_HEIGHT = 3200

    # Calibration values
    START_X = 1760
    START_Y = 525

    ROW_HEIGHT = 61
    COLUMN_GAP = 66

    BOX_SIZE = 28

    TOTAL_ROWS = ROW_COUNT
    TOTAL_COLUMNS = COLUMN_COUNT

    def build(self):

        boxes = []

        for row in range(self.TOTAL_ROWS):

            y = self.START_Y + row * self.ROW_HEIGHT

            for col in range(self.TOTAL_COLUMNS):

                x = self.START_X + col * self.COLUMN_GAP

                boxes.append(
                    Checkbox(
                        row=row + 1,
                        column=col + 1,
                        x=x,
                        y=y,
                        width=self.BOX_SIZE,
                        height=self.BOX_SIZE,
                    )
                )

        return boxes
