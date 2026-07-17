import cv2

points = []

def mouse(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:

        points.append((x, y))

        print(points)

image = cv2.imread("normalized_page_1.png")

cv2.namedWindow("Calibration")
cv2.setMouseCallback("Calibration", mouse)

while True:

    cv2.imshow("Calibration", image)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()