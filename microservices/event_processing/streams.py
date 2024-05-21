import sys
import os
import cv2
import numpy as np

import config
import parsers

rtsp_url = parsers.envGetRtspUrl(config.ENV_FILE_PATH)
stream_capture = cv2.VideoCapture(rtsp_url)


def imageCapture_toBytes() -> bytes:
    """Capture the image from RTSP stream, return in `bytes`"""

    if not stream_capture.isOpened():
        print(f"[ERROR] Stream is not openable: {rtsp_url}\n")
        return None

    ret, frame = stream_capture.read()
    if not ret:
        print(">_ Return False")
        return None

    frame_data = cv2.imencode('.jpg', frame)[1].tobytes()

    return frame_data


def videoCapture_toBytesList() -> list:
    """Capture video from RTSP stream, return in `list` of `bytes` with each elements is a frame"""

    if not stream_capture.isOpened():
        print(f"[ERROR] Stream is not openable: {rtsp_url}\n")
        return None

    fps = int(stream_capture.get(cv2.CAP_PROP_FPS))
    num_frames_to_capture = config.VIDEO_LENGTH_SEC*fps

    frames_list = []

    frame_count = 0
    while (frame_count < num_frames_to_capture):
        ret, frame = stream_capture.read()
        if not ret:
            continue

        frame_data = cv2.imencode('.jpg', frame)[1].tobytes()
        frames_list.append(frame_data)

        frame_count += 1

    if (len(frames_list) < config.ACCEPTABLE_FPS*config.VIDEO_LENGTH_SEC):
        return None

    return frames_list


def videoCapture_toFile(_timestamp: str) -> str:
    """Capture video from RTSP stream, write it to file"""

    output_file = str(config.TEMP_VIDEO_DIR + '/' +
                      _timestamp + config.VIDEO_EXTENTION)

    if not stream_capture.isOpened():
        print(f"[ERROR] Stream is not openable: {rtsp_url}\n")
        return None

    fps = int(stream_capture.get(cv2.CAP_PROP_FPS))
    num_frames_to_capture = config.VIDEO_LENGTH_SEC*fps

    width = int(stream_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(stream_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    frame_count = 0
    while (frame_count < num_frames_to_capture):
        ret, frame = stream_capture.read()
        if not ret:
            return None

        video_writer.write(frame)
        frame_count += 1

    video_writer.release()

    return output_file
