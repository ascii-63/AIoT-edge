# RT-DETR Paddle usage

**NOTE**: https://github.com/lyuwenyu/RT-DETR/tree/main/rtdetr_paddle version.

* [Convert model](#convert-model)
* [Compile the lib](#compile-the-lib)
* [Edit the config_infer_primary_rtdetr file](#edit-the-config_infer_primary_rtdetr-file)
* [Edit the deepstream_app_config file](#edit-the-deepstream_app_config-file)
* [Testing the model](#testing-the-model)

##

### Convert model

#### 1. Download the PaddleDetection repo and install the requirements

https://github.com/PaddlePaddle/PaddleDetection/blob/release/2.7/docs/tutorials/INSTALL.md

```
git clone https://github.com/lyuwenyu/RT-DETR.git
cd RT-DETR/rtdetr_paddle
pip3 install -r requirements.txt
pip3 install onnx onnxsim onnxruntime paddle2onnx
```

**NOTE**: It is recommended to use Python virtualenv.

#### 2. Copy conversor

Copy the `export_rtdetr_paddle.py` file from `DeepStream-Yolo/utils` directory to the `RT-DETR/rtdetr_paddle` folder.

#### 3. Download the model

Download the `pdparams` file from [RT-DETR Paddle](https://github.com/lyuwenyu/RT-DETR/tree/main/rtdetr_paddle) releases (example for RT-DETR-R50)

```
wget https://bj.bcebos.com/v1/paddledet/models/rtdetr_r50vd_6x_coco.pdparams
```

**NOTE**: You can use your custom model.

#### 4. Convert model

Generate the ONNX model file (example for RT-DETR-R50)

```
python3 export_rtdetr_paddle.py -w rtdetr_r50vd_6x_coco.pdparams -c configs/rtdetr/rtdetr_r50vd_6x_coco.yml --dynamic
```

**NOTE**: To simplify the ONNX model (DeepStream >= 6.0)

```
--simplify
```

**NOTE**: To use dynamic batch-size (DeepStream >= 6.1)

```
--dynamic
```

**NOTE**: To use static batch-size (example for batch-size = 4)

```
--batch 4
```

**NOTE**: If you are using the DeepStream 5.1, remove the `--dynamic` arg and use opset 12 or lower. The default opset is 16.

```
--opset 12
```

#### 5. Copy generated files

Copy the generated ONNX model file and labels.txt file (if generated) to the `DeepStream-Yolo` folder.

##

### Compile the lib

Open the `DeepStream-Yolo` folder and compile the lib

* DeepStream 6.3 on x86 platform

  ```
  CUDA_VER=12.1 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.2 on x86 platform

  ```
  CUDA_VER=11.8 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.1.1 on x86 platform

  ```
  CUDA_VER=11.7 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.1 on x86 platform

  ```
  CUDA_VER=11.6 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.0.1 / 6.0 on x86 platform

  ```
  CUDA_VER=11.4 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 5.1 on x86 platform

  ```
  CUDA_VER=11.1 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.3 / 6.2 / 6.1.1 / 6.1 on Jetson platform

  ```
  CUDA_VER=11.4 make -C nvdsinfer_custom_impl_Yolo
  ```

* DeepStream 6.0.1 / 6.0 / 5.1 on Jetson platform

  ```
  CUDA_VER=10.2 make -C nvdsinfer_custom_impl_Yolo
  ```

##

### Edit the config_infer_primary_rtdetr file

Edit the `config_infer_primary_rtdetr.txt` file according to your model (example for RT-DETR-R50 with 80 classes)

```
[property]
...
onnx-file=rtdetr_r50vd_6x_coco.onnx
...
num-detected-classes=80
...
parse-bbox-func-name=NvDsInferParseYolo
...
```

**NOTE**: The **RT-DETR** do not resize the input with padding. To get better accuracy, use

```
[property]
...
maintain-aspect-ratio=0
...
```

##

### Edit the deepstream_app_config file

```
...
[primary-gie]
...
config-file=config_infer_primary_rtdetr.txt
```

##

### Testing the model

```
deepstream-app -c deepstream_app_config.txt
```

**NOTE**: The TensorRT engine file may take a very long time to generate (sometimes more than 10 minutes).

**NOTE**: For more information about custom models configuration (`batch-size`, `network-mode`, etc), please check the [`docs/customModels.md`](customModels.md) file.
