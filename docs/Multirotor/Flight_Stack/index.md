---
title: Flight Stack
---

[https://github.com/UTAT-UAS/no_crash](https://github.com/UTAT-UAS/no_crash)

Documentation accurate as of 2026-10-27.

## Codebase Overview

`flight_core_cpp` is the only node that publishes PX4 inputs (`/fmu/in/*`). Clients such as mission scripts and the flight visualizer bridge go through `flight_core`'s services and must hold the control lease to control the vehicle. Clients must read vehicle state directly from PX4's `/fmu/out/*` topics.

```mermaid
flowchart TB
    subgraph PX4["PX4 Flight Controller"]
        px4[PX4 Autopilot]
    end

    agent[MicroXRCEAgent]

    subgraph ROS["ROS 2 (uas_ws, on the Jetson)"]
        core["flight_core_cpp<br/>(flight_core)"]
        mission["Mission scripts<br/>(Drone client)"]
        bridge["flight_visualizer_bridge<br/>(Drone client)"]
    end

    subgraph GCS["Ground Station"]
        backend["Flight visualizer backend<br/>(FastAPI)"]
        frontend["Flight visualizer frontend<br/>(Svelte dashboard)"]
    end

    px4 <-- uXRCE-DDS --> agent
    agent -- "/fmu/out/*" --> core
    agent -- "/fmu/out/*" --> mission
    agent -- "/fmu/out/*" --> bridge
    core -- "/fmu/in/*" --> agent

    mission -- "/flight_core/in/* services" --> core
    bridge -- "/flight_core/in/* services" --> core
    core -- "/flight_core/out/core_state" --> mission
    core -- "/flight_core/out/core_state" --> bridge

    bridge <-- "Socket (4G link)" --> backend
    backend <-- "WebSocket /ws" --> frontend
```

### Flight Visualizer

The flight visualizer lets an operator watch and command the drone from a browser.

```mermaid
sequenceDiagram
    participant B as Browser (Svelte)
    participant BE as Backend (FastAPI)
    participant BR as flight_visualizer_bridge
    participant FC as flight_core_cpp

    BE->>BR: TCP connect (reconnects on drop)
    loop rate_hz (default 5 Hz)
        BR->>BE: {"type": "state", ...}
        BE->>B: state (WebSocket broadcast)
    end
    B->>BE: command, e.g. goto [x, y, z]
    BE->>BR: {"type": "command", "id", "name", "args"}
    BR->>FC: /flight_core/in/* service call
    BR->>BE: {"type": "result", "id", "ok", "error"}
    BE->>B: result
```

- The **bridge** runs on the drone. It is also a `Drone` client named `flight_visualizer_bridge`, so commands that move the vehicle need it to hold the control lease (use `reacquire` after a bridge restart).
- The **backend** connects out to the bridge (`BRIDGE_HOST`, `BRIDGE_PORT`), so the ground station must be able to reach the drone over the 4G link. Carrier NAT usually means a VPN is needed.
- The **frontend** connects to the backend's `/ws` WebSocket. `GET /api/state` on the backend returns the link status and latest state for debugging.

## Communication Links

```mermaid
flowchart LR
    jetson["Jetson Orin Nano<br/>(companion computer)"]
    uav["UAV<br/>(PX4 flight controller)"]
    rc["RC Transmitter"]
    gcs["Ground Control Station"]

    jetson <-- "MAVLink" --> uav
    jetson <-- "uXRCE-DDS" --> uav
    rc <-- "ELRS" --> uav
    uav <-- "RFD telemetry radio" --> gcs
    jetson <-- "4G cellular data" --> gcs
```

| Link        | Endpoints    | Used for                                                         |
| ----------- | ------------ | ---------------------------------------------------------------- |
| MAVLink     | Jetson ↔ UAV | MAVLink messages between the companion computer and PX4          |
| uXRCE-DDS   | Jetson ↔ UAV | PX4 uORB topics bridged to ROS 2 (`/fmu/in/*`, `/fmu/out/*`)     |
| ELRS        | RC ↔ UAV     | Manual control and mode switching                                |
| RFD         | UAV ↔ GCS    | Telemetry radio link to the ground station                       |
| 4G cellular | Jetson ↔ GCS | Flight visualizer bridge traffic and remote access to the Jetson |
