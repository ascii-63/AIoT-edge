import cv2
import boto3
import io
import numpy as np

# Initialize S3 client
s3 = boto3.client('s3')

# Read MP4 video using cv2
video_capture = cv2.VideoCapture('video_1mb.mp4')

# Read video frame by frame and store bytes in memory
buffer = io.BytesIO()
while True:
    ret, frame = video_capture.read()
    if not ret:
        break
    # Convert frame to bytes
    _, encoded_frame = cv2.imencode('.jpg', frame)
    print(encoded_frame)
    buffer.write(encoded_frame.tobytes())

# Reset buffer position before uploading
buffer.seek(0)

try:
    client = boto3.client('s3')

    res = client.put_object(
        Bucket="ivsr-aiot",
        Key="videos/sample_video.mp4",
        Body=buffer)
except Exception as e:
    print(f"Error when upload to S3: {e}")

if res == None:
    print(f"Failed")
print("Passed")
