import cv2


class ImageProcessor:

    def load(self, image_path):

        img = cv2.imread(str(image_path))

        if img is None:
            raise Exception(f"Cannot open {image_path}")

        return img

    def gray(self, img):

        return cv2.cvtColor(
            img,
            cv2.COLOR_BGR2GRAY
        )

    def binary(self, gray):

        return cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

    def preprocess(self, image_path):

        img = self.load(image_path)

        gray = self.gray(img)

        binary = self.binary(gray)

        return img, gray, binary