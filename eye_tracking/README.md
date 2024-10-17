# Eye Tracking Module

## Dependencies

To get started, install the dependencies via

```bash
python eye_tracking/requirements.txt
```

Then you can run the eye tracking module standalone via

```bash
python eye_tracking/main
```

You can also run

```bash
python -m eye_tracking.src.main
```

however, this way **must** be run in module mode.

Upon first run, the app will download and save the machine learning model file used in gaze tracking. Once started, you can press 'c' to calibrate and 'g' to begin showing the gaze tracking. Note only the **x** axis will be tracked.

You can also press ';' (semicolon) to toggle the facial landmarks shown as yellow dots over the face.
