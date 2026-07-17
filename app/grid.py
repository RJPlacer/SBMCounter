from dataclasses import dataclass

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

    # ----- IMPORTANT -----
    # These values will be calibrated using ONE sample PDF.
    # After calibration they will work for all schools.
    START_X = 1760
    START_Y = 525

    ROW_HEIGHT = 61

    COLUMN_GAP = 66

    BOX_SIZE = 28

    def build(self):

        boxes = []

        for row in range(42):

            y = self.START_Y + row * self.ROW_HEIGHT

            for col in range(5):

                x = self.START_X + col * self.COLUMN_GAP

                boxes.append(
                    Checkbox(
                        row=row + 1,
                        column=col + 1,
                        x=x,
                        y=y,
                        width=self.BOX_SIZE,
                        height=self.BOX_SIZE
                    )
                )

        return boxes