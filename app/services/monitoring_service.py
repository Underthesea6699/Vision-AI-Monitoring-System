import cv2
import numpy as np

from app.vision.violation_engine import ViolationEngine
from app.services.evidence_service import EvidenceService
from app.services.incident_service import IncidentService


class MonitoringService:

    def __init__(
        self,
        model,
        restricted_zone,
        db,
        snapshot_dir="snapshots"
    ):
        self.model = model
        self.restricted_zone = restricted_zone
        self.db = db

        self.violation_engine = ViolationEngine(
            confidence_threshold=0.50,
            required_inside_frames=3
        )

        self.evidence_service = EvidenceService(
            snapshot_dir=snapshot_dir
        )

    def get_bottom_center(self, box):
        x1, y1, x2, y2 = box

        return (
            int((x1 + x2) / 2),
            int(y2)
        )

    def is_inside_zone(self, point):

        contour = np.array(
            self.restricted_zone,
            dtype=np.int32
        )

        result = cv2.pointPolygonTest(
            contour,
            (
                float(point[0]),
                float(point[1])
            ),
            False
        )

        return result >= 0

    def process_frame(self, frame):

        results = self.model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False
        )

        result = results[0]

        annotated_frame = frame.copy()

        # Draw restricted zone
        polygon = np.array(
            self.restricted_zone,
            dtype=np.int32
        )

        cv2.polylines(
            annotated_frame,
            [polygon],
            True,
            (255, 0, 0),
            2
        )

        if result.boxes is None:
            return annotated_frame

        boxes = result.boxes

        for i in range(len(boxes)):

            class_id = int(
                boxes.cls[i].item()
            )

            class_name = self.model.names[
                class_id
            ]

            # Only persons
            if class_name != "person":
                continue

            confidence = float(
                boxes.conf[i].item()
            )

            if boxes.id is None:
                continue

            track_id = int(
                boxes.id[i].item()
            )

            x1, y1, x2, y2 = map(
                int,
                boxes.xyxy[i].tolist()
            )

            person_point = self.get_bottom_center(
                (x1, y1, x2, y2)
            )

            inside_zone = self.is_inside_zone(
                person_point
            )

            violation = (
                self.violation_engine
                .check_restricted_zone(
                    track_id=track_id,
                    confidence=confidence,
                    inside_zone=inside_zone
                )
            )

            # Green = outside
            # Red = inside
            point_color = (
                (0, 0, 255)
                if inside_zone
                else (0, 255, 0)
            )

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )

            cv2.putText(
                annotated_frame,
                f"ID: {track_id}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )

            cv2.circle(
                annotated_frame,
                person_point,
                6,
                point_color,
                -1
            )

            # Confirmed violation
            if violation:

                print(
                    "\n🚨 "
                    "RESTRICTED-ZONE "
                    "VIOLATION CONFIRMED!"
                )

                print(
                    f"Person ID: {track_id}"
                )

                print(
                    f"Confidence: "
                    f"{confidence:.2f}"
                )

                evidence = (
                    self.evidence_service
                    .save_violation_evidence(
                        original_frame=frame,
                        annotated_frame=
                            annotated_frame,
                        violation=violation
                    )
                )

                if evidence:

                    incident = (
                        IncidentService
                        .create_incident(
                            db=self.db,
                            violation_type=
                                violation[
                                    "violation_type"
                                ],
                            person_track_id=
                                track_id,
                            confidence=
                                confidence,
                            snapshot_path=
                                evidence[
                                    "original_path"
                                ],
                            annotated_snapshot_path=
                                evidence[
                                    "annotated_path"
                                ]
                        )
                    )

                    print(
                        f"💾 Incident saved: "
                        f"{incident.id}"
                    )

        return annotated_frame