---
title: Communication Links
hide:
  - navigation
  - toc
---

# Communication Links

Back to [flight stack](index.md)

=== "1 · System"

    <div class="cd-diagram" markdown>![System communication links between the UAV, the RC transmitter, the tailnet and the ground station](diagrams/comm_l1_system.svg)</div>

=== "2 · Software modules"

    <div class="cd-diagram" markdown>![Software modules on the flight controller, Jetson and ground station and the links between them](diagrams/comm_l2_modules.svg)</div>

=== "3 · Programs and nodes"

    <div class="cd-diagram" markdown>![Programs, ROS 2 nodes and the data between them across the drone and ground station](diagrams/comm_l3_nodes.svg)</div>

=== "Simulation"

    <div class="cd-diagram" markdown>![Simulation setup with Gazebo, a Gazebo camera, PX4 SITL, the ROS 2 graph and the flight visualizer on one machine](diagrams/comm_sim.svg)</div>

<small>Icons: [Material Symbols](https://fonts.google.com/icons) by Google, used under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).</small>

!!! note "Editing the diagrams"
    The SVGs in `diagrams/` are generated assets. Edit `media/build_comm_diagrams.py` (layout and labels) or the icons in `media/` (see `media/icons/README.md` for their source and licence), then run `python3 media/build_comm_diagrams.py` from the repository root.
