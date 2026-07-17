import cv2
import numpy as np


def preprocess(image_path):
    img = cv2.imread(image_path)

    if img is None:
        raise Exception("Cannot open image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    binary = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    return img, gray, binary


def detect_table(binary):

    horizontal = binary.copy()
    vertical = binary.copy()

    h_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (80, 1)
    )

    horizontal = cv2.erode(horizontal, h_kernel)
    horizontal = cv2.dilate(horizontal, h_kernel)

    v_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (1, 80)
    )

    vertical = cv2.erode(vertical, v_kernel)
    vertical = cv2.dilate(vertical, v_kernel)

    table = cv2.add(horizontal, vertical)

    return table

def get_table_bbox(table_image):
    """
    Find the largest table on the page.
    Returns (x, y, w, h)
    """

    contours, _ = cv2.findContours(
        table_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest = None
    largest_area = 0

    for cnt in contours:

        x, y, w, h = cv2.boundingRect(cnt)

        area = w * h

        if area > largest_area:
            largest_area = area
            largest = (x, y, w, h)

    return largest

def detect_rows(table_image):
    """
    Detect horizontal lines (rows) in the table.
    """

    horizontal = table_image.copy()

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (120, 1)
    )

    horizontal = cv2.erode(horizontal, kernel)
    horizontal = cv2.dilate(horizontal, kernel)

    contours, _ = cv2.findContours(
        horizontal,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    rows = []

    for cnt in contours:

        x, y, w, h = cv2.boundingRect(cnt)

        if w > 500:
            rows.append((x, y, w, h))

    rows.sort(key=lambda r: r[1])

    return rows