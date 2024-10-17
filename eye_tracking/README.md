# Eye Tracking Module

## Dependencies

To get started, install the dependencies via

```bash
pip install -r eye_tracking/requirements.txt
```

## Running the module

Then you can run the eye tracking module standalone via

```bash
python eye_tracking/main.py
```

You can also run

```bash
python -m eye_tracking.src.main
```

however, this way **must** be run in module mode.

## Using Eye Tracking

Upon first run, the app will download and save the machine learning model file used in gaze tracking. Once started, you can press 'c' to calibrate and 'g' to begin showing the gaze tracking. Note only the **x** axis will be tracked.

You can also press ';' (semicolon) to toggle the facial landmarks shown as yellow dots over the face.

## Configuration

The following configuration settings are available in the [/eye_tracking/configs/mpiigaze.yaml](/eye_tracking/configs/mpiigaze.yaml)

-   mode: MPIIGaze - the model used for eye tracking
-   device: CPU | GPU - the device used for the machine learning computation
-   model:
    -   resnet_preact: The machine learning
-   face_detector:
    -   mode: mediapipe - the library used for computing facial landmarks
    -   mediapipe_max_num_faces: The max number of faces to track
-   gaze estimator:
    -   checkpoint: Where checkpoint files are stored for the model
    -   camera_params: Path to file where camera params are stored
    -   use_dummy_camera_params: whether to use default params
    -   normalized_camera_params: Path to where distortion corrected camera params are stored
    -   normalized_camera_distance: Approx distance from the camera to the user.
-   gaze_point:
    -   smoothing_frames: How many frames to smooth the eye tracking over
    -   z_projection_multiplier: Multiplier to combine with eye tracking vector when projecting to image plane. Best around 0.9
    -   gaze_vector_y_scale: What to scale the y axis by in eye tracking. As y axis is not tracked, best as a low value (~0.15)
        dot_size: Pixel diameter of dot to display for gaze tracking.
-   demo
    -   use_camera: Should be set to true to use the webcam. If false, will use a image or video from a file. See path params below.
    -   display_on_screen: Should be true to display the eye tracking on screen in realtime.
    -   wait_time: The keyboard delay time in the loop
    -   max_tick_rate: FPS cap. If set to 0, fps is unlimited.
    -   show_fps: Whether to show fps in eye tracking module. Only works in standalone mode
    -   image_path: Path to image to perform eye tracking on.
    -   video_path: Path to video to perform eye tracking on.
    -   output_dir: Output folder to put the eye tracked file if from video.
    -   output_file_extension: File extension for video output. E.g. avi
    -   head_pose_axis_length: Metres to extend head pose visualiser in head pose tracker.
    -   show_bbox: default setting for whether to show bounding box around faces.
    -   show_head_pose: Default setting for whether to show head pose.
    -   show_gaze_vector: Default setting for whether to show gaze vector by default. Calibtration must still be performed first for eye tracking to work.
    -   show_landmarks: Default setting for whether to show landmarks by default
    -   show_normalized_image: Whether to show normalised eye framed box in second window.
    -   show_template model: Whether to show 3D Face model landmarks in visualiser.
    -   upscale_dim: Dimension to upscale video frame to.
    -   hitbox_width_proportion. The proportion of the screen on the left and right to reserve for hitbox (whether user is looking left or right).
-   keyboard_bindings:
    -   bbox: key to toggle bounding box
    -   landmark: key to toggle landmarks
    -   head_pose
    -   normalized_image: Key to toggle normalized_image in the visualiser.
    -   template_model: Key to toggle 3D face model template in the visualiser. Different from landmarks as this is where the model thinks the face is after > 2D > back to 3D projection vs where it actually is in the frame, just in 2D.
    -   gaze_vector: Key to toggle gaze_vector in the visualiser.
    -   calibrate: Key to calibrate eye tracking.
    -   loop_toggle: Key to toggle eye tracking loop. Only really useful in threaded mode to disable eye tracking
