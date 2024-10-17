# Eye Gaze and Voice Aware Drone Controller

## Developers

-   Hugo Burton
-   Nicholas Roughley
-   Jasmine Hong
-   Andrew Earl
-   Cooper Blackburn
-   Hayden Reynolds

Completed as project for DECO3801 at the University of Queensland, St Lucia, Australia.

**Semester:** 2, 2024

[Repo Link](https://github.com/hugs7/DECO3801)

[Project Description](https://studio3build.uqcloud.net/project/07T)

## Motivation

Traditional drone control methods rely on physical controllers, a mobile device, or perhaps a VR headset. While these methods are very precise, they bring a steep learning curve and can take time to master. They can also limit the pilot's ability to multitask or focus on other important tasks for a given application involving drones.

This project seeks to simplify the task of piloting a drone using gaze tracking and voice control to provide a hands-free control environment. Not only does this enable beginners to more easily fly a drone, but it also would allow more focus on the task at hand which could be critical in certain applications.

## Introduction

The initial project brief laid out a plan to control a simulated drone using a combination of gaze tracking, voice commands and a large language model (LLM). Early in the design process, our team extended this concept to real drones in the physical world. At a high level our project implements the ability to control a drone using gaze tracking and voice commands all from a laptop. Powered by a machine learning model and some vector calculus, the webcam feed from the user's laptop is used to estimate the user's gaze on the screen. Depending upon where the user is looking, a rotate input will be relayed to the drone's controller, and in turn to the drone. The voice controller adds the ability for the drone to takeoff, land, and move in any direction. Put together these two

## Project Hierarchy

The project repository is split into five main sections summarised below:

-   `./app/`: Contains code for the parent thread which handles the orchestration of each of the other modules. Also handles the GUI for the application.
-   `./common/`: Common code shared between two or more of the other modules.
-   `./drone/`: Controller which interfaces with the physical drone.
-   `./eye_tracking/`: Estimates the user's gaze and feeds data to the drone controller.
-   `./voice_control/`: Accepts voice commands from the user, sends them to a custom OpenAI model for processing and feeds the encoded command to the drone controller.

Modules `drone`, `eye_tracking`, and `voice_control` can indeed run independently. See individual documentation linked below or how to run in this way.

### Eye (Gaze) Tracking

See also [the eye tracking documentation](./eye_tracking/README.md)

### Voice Control

See also [the voice control documentation](./voice_control/README.md)

### Drone Controller

See also [the drone controller documentation](./drone/README.md)

---

## Getting Started

Before running the project, ensure you have all the necessary dependencies installed via

```bash
pip install -r requirements.txt
```

Each module has its own `requirements.txt` file, however, a global copy is kept in the root for ease of installation.

An additional dependency, FFMpeg, is required for audio playback in the voice control module. Note: this is **NOT** a Python package, and has a custom install procedure. Please refer to the [voice control documentation](./voice_control/README.md) for installation instructions.

### Running the application

To run the project, use the following Python script

```bash
python ./app/src/main.py
```

For running each module independently, see the relevant documentation linked above, [here](README.md#project-hierarchy).

# Using the App

On application startup, the necessary dependencies and custom modules will be initialised. During this time you will see a loading GUI screen. As per the drone configuration file, if set to Tello mode, the application will attempt to connect to the Tello drone's WiFi network automatically.

If successful, you will see the live video feed from the drone, as well as your webcam at the bottom

## Eye (Gaze) Tracking

With the default keyboard bindings, ';' (semicolon) can be used to toggle the facial landmarks. If you are able to see your facial landmarks, look straight at the camera and press 'c' to calibrate the eye tracking, then 'g' to enable the gaze overlay.

Additionally, 'b' and 'h' can be used to toggle the facial bounding box and head pose indicator respectively, though these are not required for normal operation.

## Voice Control

With the drone connected, you can say the wake command as defined in the drone's configuration file. By default this is "Ok Drone", and when recognised, the app will play a wake tone indicating it is listening to your next command. You can then say a command for the drone to interpret such as _"Takeoff then rotate right 90 degrees"_. The command will be accepted as indicated by a higher pitched tone, at which time your command will be interpreted using artificial intelligence, then sent to the drone to perform the actions requested. This process runs in a loop meaning you can say the voice activation command, as the app is always listening while the drone is connected.

To toggle the voice control feature, the period (.) key can be used, while retaining other drone control functionality.

# Drone Control

In addition to eye tracking and voice commands, the drone can also be controlled via keyboard inputs, with keybindings defined in the drone's configuration file at [./drone/configs/drone.yaml](./drone/configs/drone.yaml) under **controller > keyboard_bindings**.

## Configuration

TODO

## Debugging

As some modules can be run independently, they can also be debugged independently.

To add more here after merging [#33](https://github.com/hugs7/DECO3801/pull/34).
