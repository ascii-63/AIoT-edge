gst-launch-1.0 v4l2src device=/dev/video6 ! videoconvert ! video/x-raw,width=640,height=480,format=I420 ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5000

Channel List:
(Intel(R) RealSense(TM) Depth Ca): channel +2, +4 (depth, RGB)
(1080P Web Camera: 1080P Web Cam): channel +0 (RGB)
(UVC Camera (046d:0825)): channel +0 (RGB)
