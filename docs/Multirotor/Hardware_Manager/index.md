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

### Installing PyTorch

This is probably how you do it (Jetpack 6.2, CUDA 12.6)

```
sudo apt-get update
sudo apt-get install -y python3-pip libopenblas-dev libcusparselt-dev
```

Install:

- [https://developer.nvidia.com/cusparselt-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network](https://developer.nvidia.com/cusparselt-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network)
_ [https://developer.nvidia.com/cudss-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network](https://developer.nvidia.com/cudss-downloads?target_os=Linux&target_arch=aarch64-jetson&Compilation=Native&Distribution=Ubuntu&target_version=22.04&target_type=deb_network)

```
sudo apt-get install -y cuda-cupti-12-6
```

```
python3 -m pip install torch==2.8.0 torchvision==0.23.0 --index-url=https://pypi.jetson-ai-lab.io/jp6/cu126
```

### Other Links

[https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html](https://docs.nvidia.com/deeplearning/frameworks/install-pytorch-jetson-platform/index.html)
[https://ninjalabo.ai/blogs/jetson_pytorch.html](https://ninjalabo.ai/blogs/jetson_pytorch.html)

Can also install cusparselt like this?

[https://github.com/pytorch/pytorch/blob/main/.ci/docker/common/install_cusparselt.sh](https://github.com/pytorch/pytorch/blob/main/.ci/docker/common/install_cusparselt.sh)

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
