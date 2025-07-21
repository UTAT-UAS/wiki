---
title: About
---

[New here? See the tutorials to get started](./Tutorials/index.md)

UAS Software documentation for multirotor specific repositories.

## Overview

Currently the following projects exist:

- [Computer Vision](./Computer_Vision/index.md)
- [Flight Stack](./Flight_Stack/index.md)
- [Flight Visualizer](./Flight_Visualizer/index.md)
- [Hardware Manager](./Hardware_Manager/index.md)

At a high level they can be viewed like this:

```mermaid
graph LR
  Z{{Flight Computer}} <==>|uXRCE-DDS| A
  A{{Companion Computer}} <==>|ROS2| B{{ROS2 Network}};
  B <==>|ROS2| C[Flight Stack];
  B <==>|ROS2| D[Flight Visualizer];
  B <==>|ROS2| E[Computer Vision];
  B <==>|ROS2| F[Hardware Manager];
  F <==>|Linux| G{{Peripherals}};
  C .->|API| F;
  D .->|API| F;
  E .->|API| F;
```

