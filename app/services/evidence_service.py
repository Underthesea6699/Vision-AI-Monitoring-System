from datetime import datetime
from pathlib import Path

import cv2


class EvidenceService:
    """
    Handles saving evidence images for confirmed violations.
    """

    def __init__(self, snapshot_dir="snapshots"):
        self.snapshot_dir = Path(snapshot_dir)

        # Create the snapshot directory if it does not exist
        self.snapshot_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_violation_evidence(
        self,
        original_frame,
        annotated_frame,
        violation
    ):
        """
        Save both original and annotated images
        for a confirmed violation.
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        person_id = violation["track_id"]

        base_name = (
            f"restricted_zone_"
            f"person_{person_id}_"
            f"{timestamp}"
        )

        original_path = (
            self.snapshot_dir /
            f"{base_name}_original.jpg"
        )

        annotated_path = (
            self.snapshot_dir /
            f"{base_name}_annotated.jpg"
        )

        # Save original frame
        original_saved = cv2.imwrite(
            str(original_path),
            original_frame
        )

        # Save annotated frame
        annotated_saved = cv2.imwrite(
            str(annotated_path),
            annotated_frame
        )

        if original_saved and annotated_saved:

            print("\n📸 Evidence saved!")

            print(
                f"Original: {original_path}"
            )

            print(
                f"Annotated: {annotated_path}"
            )

            return {
                "original_path": str(original_path),
                "annotated_path": str(annotated_path)
            }

        print("\n❌ Failed to save evidence.")

        return None