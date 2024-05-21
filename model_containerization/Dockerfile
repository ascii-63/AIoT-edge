FROM nvcr.io/nvidia/deepstream-l4t:6.3-samples

RUN apt update -y
RUN apt upgrade -y

# GStreamer Dependencies
RUN apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev \
    gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl \
    gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio

# Gst RTSP Server
RUN apt install -y libgstrtspserver-1.0-dev gstreamer1.0-rtsp

# Deepstream Dependencies
RUN apt install -y python3-gi python3-dev python3-gst-1.0 python-gi-dev git python-dev \
    python3 python3-pip python3.8-dev cmake g++ build-essential libglib2.0-dev \
    libglib2.0-dev-bin libgstreamer1.0-dev libtool m4 autoconf automake libgirepository1.0-dev libcairo2-dev

# Clone the Deepstream Python Apps Repo into <deepstream>/sources
WORKDIR /opt/nvidia/deepstream/deepstream/sources
RUN git clone --branch v1.1.8 https://github.com/NVIDIA-AI-IOT/deepstream_python_apps.git

# Download and install the Deepstream Python Bindings
RUN mkdir /opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps/bindings/build
WORKDIR /opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps/bindings/build
RUN curl -O -L https://github.com/NVIDIA-AI-IOT/deepstream_python_apps/releases/download/v1.1.8/pyds-1.1.8-py3-none-linux_aarch64.whl
RUN pip install ./pyds-1.1.8-py3-none-linux_aarch64.whl

# Copy model/engine
COPY ./model__engine/Deepstream-Yolo /opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps/apps/model__engine/Deepstream-Yolo
# Copy deepstream app
COPY ./deepstream /opt/nvidia/deepstream/deepstream/sources/deepstream_python_apps/apps/ds_multi-rtsp_amqp

EXPOSE 8554

WORKDIR /opt/nvidia/deepstream/deepstream
RUN ./user_additional_install.sh

RUN apt install python3-gi python3-dev python3-gst-1.0 -y
RUN apt-get install libgstrtspserver-1.0-0 gstreamer1.0-rtsp
RUN apt-get install libgirepository1.0-dev
RUN apt-get install gobject-introspection gir1.2-gst-rtsp-server-1.0
CMD ["/bin/bash"]