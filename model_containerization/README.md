# Model Containerization

## Steps to config for each model:
1. Copy Model/Engine/Onnx file to model__engine directory
2. Modify the deepstream/config.py file
3. Modify the Dockerfile

## Build image:
```bash
docker build
```

## Run image:
```bash
docker run -it --rm --net=host --runtime nvidia \
-w /opt/nvidia/deepstream/deepstream-6.3/sources/deepstream_python_apps/apps/ds_multi-rtsp_amqp \
-v /tmp/.X11-unix/:/tmp/.X11-unix ds-yolo-v8:v1.0

sudo python3 main.py [uri] [uri1] [uri2]...
```