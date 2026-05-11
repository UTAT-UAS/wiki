---
title: Hardware Manager
---

## Flashing Jetson Nano Orin

It is easiest to do this on native Ubuntu.

[Follow this guide to install the Nvidia sdkmanager](https://www.jetson-ai-lab.com/initial_setup_jon_sdkm.html)

You will have to create and login with a Nvidia developers account, then follow the instructions in the installer. Make sure to install with CUDA.

It appears that when in recovery mode the carrier board does not spin the fan on the Jetson module, use an external fan to cool the module otherwise it may power off due to overheating. The fan will spin once the OS installation has reached a certain point.

### Setting Up Jetson

- Disable desktop and misc services [https://www.jetson-ai-lab.com/tips_ram-optimization.html](https://www.jetson-ai-lab.com/tips_ram-optimization.html)
- Change fan curve to cool
- Update system
- Install/setup ROS2
- Install uXRCE-DDS
- Install/setup Tailscale

Sometimes CUDA doesn't get installed?

```
sudo apt install cuda-toolkit-12-6
```

Install custom gstreamer to `/build` or somewhere and point `GST_PLUGIN_PATH` or else library issues!

`jtop` is a `top` inspired tui for viewing current jetson information.

Also note that `jetson_clocks` is a thing.

### Installing PyTorch

Working method for Jetpack 6.2 and CUDA 12.6:

```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/arm64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cusparselt-cuda-12
sudo apt-get -y install cudss
sudo apt-get install -y python3-pip libopenblas-dev libcusparselt-dev
sudo apt-get install -y cuda-cupti-12-6
python3 -m pip install torch==2.8.0 torchvision==0.23.0 --index-url=https://pypi.jetson-ai-lab.io/jp6/cu126
```

### Installing onnxruntime-gpu

[https://docs.ultralytics.com/guides/nvidia-jetson/#install-ultralytics-package_1](https://docs.ultralytics.com/guides/nvidia-jetson/#install-ultralytics-package_1)

Don't forget to install `tensorrt` through `apt`` and not `pip` (otherwise make sure you completely purge `tensorrt` related packages from site packages). You will get incompatibility issues if you install through `pip`.

### Building OpenCV

Build an optimized OpenCV binary (with gstreamer support), modified from [here.](https://github.com/Qengineering/Install-OpenCV-Jetson-Nano/blob/main/OpenCV-4-12-0.sh)

```sh
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
  -D EIGEN_INCLUDE_PATH=/usr/include/eigen3 \
  -D WITH_OPENCL=OFF \
  -D CUDA_ARCH_BIN=${ARCH} \
  -D CUDA_ARCH_PTX=${PTX} \
  -D WITH_CUDA=ON \
  -D WITH_CUDNN=ON \
  -D WITH_CUBLAS=ON \
  -D ENABLE_FAST_MATH=ON \
  -D CUDA_FAST_MATH=ON \
  -D OPENCV_DNN_CUDA=OFF \
  -D WITH_QT=OFF \
  -D WITH_OPENMP=ON \
  -D BUILD_TIFF=ON \
  -D WITH_FFMPEG=ON \
  -D WITH_GSTREAMER=ON \
  -D WITH_TBB=ON \
  -D BUILD_TBB=ON \
  -D BUILD_TESTS=OFF \
  -D WITH_EIGEN=ON \
  -D WITH_V4L=ON \
  -D WITH_LIBV4L=ON \
  -D WITH_PROTOBUF=ON \
  -D OPENCV_ENABLE_NONFREE=ON \
  -D INSTALL_C_EXAMPLES=OFF \
  -D INSTALL_PYTHON_EXAMPLES=OFF \
  -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-packages \
  -D BUILD_opencv_python2=OFF \
  -D BUILD_opencv_python3=ON \
  -D PYTHON_VERSION=310 \
  -D PYTHON3_EXECUTABLE=$(which python3) \
  -D OPENCV_GENERATE_PKGCONFIG=ON \
  -D BUILD_EXAMPLES=OFF \
  -D CMAKE_CXX_FLAGS="-march=native -mtune=native" \
  -D CMAKE_C_FLAGS="-march=native -mtune=native" ..
```

### Sources

- [https://developer.nvidia.com/cusparselt-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network](https://developer.nvidia.com/cusparselt-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network)
- [https://developer.nvidia.com/cudss-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network](https://developer.nvidia.com/cudss-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network)
- [https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html)
- [https://ninjalabo.ai/blogs/jetson_pytorch.html](https://ninjalabo.ai/blogs/jetson_pytorch.html)
- [https://github.com/pytorch/pytorch/blob/main/.ci/docker/common/install_cusparselt.sh](https://github.com/pytorch/pytorch/blob/main/.ci/docker/common/install_cusparselt.sh)

### Serial SSH

```sh
ssh <user>@192.168.55.1
```

### Flashing from Docker Container

Potentially useful tips:

- This must be done on a Linux machine (WSL2 might work according to the internet).
- Add "nfs" to your supported file systems and kernel modules
- Install udev in the container
- `QEMU` with `aarch64-linux` support must be installed on the host machine. On `NixOS` install `QEMU` system wide and add `"aarch64-linux"` to `boot.binfmt.emulatedSystems`. [https://wiki.nixos.org/wiki/QEMU](https://wiki.nixos.org/wiki/QEMU)
- Run `sudo update-binfmts --enable qemu-aarch64` in the container before launching the `sdkmanager`, you might have to install `qemu-user-static` before you run this (or after sdkmanger fails?).

Useful forum links:

- [https://www.jetson-ai-lab.com/initial_setup_jon_sdkm.html](https://www.jetson-ai-lab.com/initial_setup_jon_sdkm.html)
- [https://forums.developer.nvidia.com/t/orin-nano-installation-fails-chroot-failed-to-run-command-dpkg-exec-format-error/263215/6](https://forums.developer.nvidia.com/t/orin-nano-installation-fails-chroot-failed-to-run-command-dpkg-exec-format-error/263215/6)

## Other Packages

### MicroROS

You must have the build workspace completely isolated. (Remove any sourcing of workspaces from `~/.bashrc`)

