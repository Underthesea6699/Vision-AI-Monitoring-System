from fastapi import APIRouter
from fastapi.responses import StreamingResponse

import cv2

from app.services.video_stream_service import VideoStreamService


router = APIRouter(
    prefix="/api/video",
    tags=["Video"]
)


VIDEO_PATH = "test_videos/test.mp4"


@router.get("/info")
def video_info():

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        return {
            "error": "Could not open video"
        }

    width = int(
        cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    cap.release()

    return {
        "width": width,
        "height": height,
        "fps": fps
    }


@router.get("/stream")
def video_stream():

    service = VideoStreamService(
        video_source=VIDEO_PATH
    )

    return StreamingResponse(
        service.generate_frames(),
        media_type=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )