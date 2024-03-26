from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Load YOLOv3 model and configure it
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
output_layers = net.getUnconnectedOutLayersNames()
confidence_threshold = 0.5
class_names = []

with open("coco.names", "r") as file:
    for class_name in file:
        class_names.append(class_name.strip())

@app.route('/')
def index():
    return render_template('index.html')

# Define the function for post-processing detections
def post_process(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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
                x = int(center_x -   w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, 0.4)

    return indices, boxes, confidences

@app.route('/video_feed', methods=['POST'])
def video_feed():
    data_url = request.data.decode('utf-8')
    header, encoded = data_url.split(",", 1)
    image_data = base64.b64decode(encoded)
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    print("Received frame from webcam:", frame.shape)  # Debug statement

    indices, boxes, confidences = post_process(frame)

    print("Detected objects:", indices)  # Debug statement

    # Process indices, boxes, and confidences
    # Construct JSON response with predictions
    predictions = {"indices": indices.tolist(), "boxes": boxes, "confidences": confidences}

    return jsonify(predictions)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)