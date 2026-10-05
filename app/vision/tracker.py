from ultralytics import YOLO


class PersonTracker:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def track(self, frame):
        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        return results