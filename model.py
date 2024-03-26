import cv2
import numpy as np

# Load YOLOv3 model and configure it
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
output_layers = net.getUnconnectedOutLayersNames()
confidence_threshold = 0.5
class_names = []

with open("coco.names", "r") as file:
    for class_name in file:
        class_names.append(class_name.strip())

# Initialize the webcam feed
cap = cv2.VideoCapture(0)

# Define the function for post-processing detections
def post_process(frame, net, output_layers, confidence_threshold, class_names):
    height, width, channels = frame.shape
    scale = 0.00392
    blob = cv2.dnn.blobFromImage(frame, scale, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    boxes = []
    confidences = []
    class_ids = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > confidence_threshold and class_names[class_id] == "person":
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)

    return frame, indices, boxes, confidences, class_ids

# Detect persons in the webcam feed
while True:
    ret, frame = cap.read()
    frame, indices, boxes, confidences, class_ids = post_process(frame, net, output_layers, confidence_threshold, class_names)

    # Draw the bounding boxes and labels
    if len(indices) > 0:
        for i in indices.flatten():
            box = boxes[i]
            x, y, w, h = box

            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Add label
            label = "Person"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("Thief Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()