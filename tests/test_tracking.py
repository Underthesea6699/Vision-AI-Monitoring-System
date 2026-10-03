import cv2
from ultralytics import YOLO


# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Open recorded video
video_path = "test_videos/test.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Could not open video: {video_path}")
    exit()


while True:
    success, frame = cap.read()

    if not success:
        print("Video finished or frame could not be read.")
        break

    # Run YOLO tracking
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        verbose=False
    )

    result = results[0]

    # Check whether tracking IDs exist
    if result.boxes.id is not None:

        boxes = result.boxes.xyxy.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        track_ids = result.boxes.id.cpu().numpy()

        for box, class_id, confidence, track_id in zip(
            boxes,
            class_ids,
            confidences,
            track_ids
        ):

            x1, y1, x2, y2 = map(int, box)

            class_id = int(class_id)
            track_id = int(track_id)

            class_name = result.names[class_id]

            # Calculate bottom-center point
            center_x = int((x1 + x2) / 2)
            bottom_y = y2

            print(
                f"ID: {track_id} | "
                f"Class: {class_name} | "
                f"Confidence: {confidence:.2f} | "
                f"BBox: ({x1}, {y1}, {x2}, {y2}) | "
                f"Bottom-center: ({center_x}, {bottom_y})"
            )

    # Draw tracking results
    annotated_frame = result.plot()

    # Display video
    cv2.imshow(
        "Vision-AI Object Tracking",
        annotated_frame
    )

    # Press Q to stop
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()

print("Tracking test completed.")
