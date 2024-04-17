import cv2

RTSP_URL = 'rtsp://admin:ivsr2019@192.168.0.100'

cap = cv2.VideoCapture(
    RTSP_URL
)

while (cap.isOpened()):
    ret, frame = cap.read()

    if ret:
        timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
        # title = 'Frame: ' + str(timestamp_ms)
        title = 'Frame'
        cv2.imshow(winname=title, mat=frame)
        print(f"Frame with timestamp: {timestamp_ms}")

    # Press 'q' to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
