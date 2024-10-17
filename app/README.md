# Main GUI

This module contains code for the main GUI. This module serves as the main entry point to the application and can be run via

```bash
python app/src/main.py
```

The app will then load, which may take some time (~10 - 30 seconds). Be patient during this time. If the drone is configured to connect as per the drone's configuration, it will connect and the video feed will be displayed

## Microsoft DebugPy Current Issue

Note due to issue [#1531 on Microsoft DebugPy](https://github.com/microsoft/debugpy/issues/1531) I have written a drop-in replacement to fix a bug. There does exist a PR for this but it hasn't been merged yet.

```python
def has_binding(api):
    # NOTE FIXED LOCALLY ONLY: See https://github.com/microsoft/debugpy/issues/1531
    """Safely check for PyQt4 or PySide, without importing
       submodules

       Parameters
       ----------
       api : str [ 'pyqtv1' | 'pyqt' | 'pyside' | 'pyqtdefault']
            Which module to check for

       Returns
       -------
       True if the relevant module appears to be importable
    """
    module_name_mapping = {
        'pyqtv1': 'PyQt4',
        'pyqt': 'PyQt4',
        'pyside': 'PySide',
        'pyqtdefault': 'PyQt4',
        'pyqt5': 'PyQt5'
    }

    module_name = module_name_mapping.get(api)
    if module_name is None:
        return False

    import importlib.util

    try:
        mod_spec = importlib.util.find_spec(module_name)
        if mod_spec is None:
            return False

        mod = importlib.import_module(module_name)

        submodules = ['QtCore', 'QtGui', 'QtSvg']
        for submodule in submodules:
            submodule_name = f"{module_name}.{submodule}"
            submodule_spec = importlib.util.find_spec(submodule_name)
            if submodule_spec is None:
                return False

        if api == 'pyside':
            if hasattr(mod, '__version__'):
                return check_version(mod.__version__, '1.0.3')
            else:
                return False

        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
```
