import cv2
from ultralytics import YOLO

from app.database.database import SessionLocal
from app.services.monitoring_service import MonitoringService
from app.services.zone_service import ZoneService


class VideoStreamService:

    def __init__(
        self,
        video_source,
        model_path="yolov8n.pt"
    ):
        self.zone_service = ZoneService()
        self.video_source = video_source
        self.model = YOLO(model_path)



    def generate_frames(self):

        cap = cv2.VideoCapture(
            self.video_source
        )

        if not cap.isOpened():
            print(
                f"❌ Could not open video: "
                f"{self.video_source}"
            )
            return

        db = SessionLocal()

        restricted_zone = self.zone_service.get_zone()

        if len(restricted_zone) < 3:
            print("⚠️ Restricted zone is not configured.")
            return

        monitoring_service = MonitoringService(
            model=self.model,
            restricted_zone=restricted_zone,
            db=db
        )

        try:

            while True:

                success, frame = cap.read()

                if not success:
                    break

                annotated_frame = (
                    monitoring_service
                    .process_frame(frame)
                )

                success, buffer = cv2.imencode(
                    ".jpg",
                    annotated_frame
                )

                if not success:
                    continue

                frame_bytes = buffer.tobytes()

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame_bytes
                    + b"\r\n"
                )

        finally:

            db.close()
            cap.release()