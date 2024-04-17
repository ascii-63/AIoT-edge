import cv2
from datetime import datetime, timedelta

RTSP_URL = 'rtsp://192.168.0.202:8554/ds-test'
is_first_frame = True
start_time = None

cap = cv2.VideoCapture(
    RTSP_URL
)

while (cap.isOpened()):
    ret, frame = cap.read()

    if ret:
        if is_first_frame:
            is_first_frame = False
            start_time = datetime.now()
            print(f"\n********** START **********\n")

        title = 'Frame'
        cv2.imshow(winname=title, mat=frame)

        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        print(
            f"Frame with timestamp: {start_time + timedelta(milliseconds=int(timestamp_ms))}")
        print(f"Current timestamp: {datetime.now()}\n")

    # Press 'q' to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
