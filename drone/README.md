# Drone Controller

## Dependenices

To get started, install the dependencies via

```bash
pip install -r drone/requirements.txt
```

## Running the module

Then you can run the drone module standalone via

```bash
python drone/main.py
```

You can also run

```bash
python -m drone.src.main
```

however this way **must** be run in module mode.

## Using the Drone Module

When running standalone, control of the drone is limited to the keyboard only. The keyboard bindings as defined in `/drone/configs/drone.yaml` and are user customisable Note this file will be generated on first start, so if you don't see one, start the app first.
