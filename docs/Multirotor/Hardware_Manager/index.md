---
title: Hardware Manager
---

## Flashing Jetson Nano Orin

It is easiest to do this on native Ubuntu.

[Follow this guide to install the Nvidia sdkmanager](https://www.jetson-ai-lab.com/initial_setup_jon_sdkm.html)

You may have to use the `flash.sh` script to get the super firmware which enables the MAXN SUPER power profile.

`sudo ./flash jetson-orin-nano-devkit-nvme internal`

It appears that when in recovery mode the carrier board does not spin the fan on the Jetson module, use an external fan to cool the module otherwise it may power off due to overheating.

### Setting Up Jetson

- Disable desktop and misc services [https://www.jetson-ai-lab.com/tips_ram-optimization.html](https://www.jetson-ai-lab.com/tips_ram-optimization.html)
- Change fan curve to cool
- Update system
- Install/setup ROS2
- Install uXRCE-DDS
- Install/setup Tailscale

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
