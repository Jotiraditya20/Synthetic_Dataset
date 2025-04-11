import cv2
import os

# Paths
image_path = "atraining/valid/images/3_png.rf.890cb57e2af214728fba250092441eb1.jpg"
label_path = "atraining/valid/labels/3_png.rf.890cb57e2af214728fba250092441eb1.txt"
class_names = ['graph', 'image', 'text', 'x_axis', 'y_axis']
#image_path = "atraining/train/images/train/page_1.jpg"
#label_path = "atraining/train/labels/train/page_1.txt"

# Load image
img = cv2.imread(image_path)
h, w = img.shape[:2]

# Read labels
with open(label_path, "r") as f:
    lines = f.readlines()

for line in lines:
    parts = line.strip().split()
    cls_id = int(parts[0])
    x_center, y_center, box_w, box_h = map(float, parts[1:])

    # Convert YOLO format to pixel coords
    x1 = int((x_center - box_w / 2) * w)
    y1 = int((y_center - box_h / 2) * h)
    x2 = int((x_center + box_w / 2) * w)
    y2 = int((y_center + box_h / 2) * h)

    # Draw box and label
    color = (0, 255, 0)
    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
    cv2.putText(img, class_names[cls_id], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

# Save or display the result
#cv2.imwrite("labeled_page_4.jpg", img)
# or to display:
cv2.imshow("Labeled", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
