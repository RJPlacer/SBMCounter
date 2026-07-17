import cv2

for box in boxes:

    cv2.rectangle(
        image,
        (box.x, box.y),
        (box.x + box.width,
         box.y + box.height),
        (0,255,0),
        2
    )

cv2.imwrite("overlay.png", image)