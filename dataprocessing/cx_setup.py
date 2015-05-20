from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["re", "atexit", "sip", "lxml._elementpath", "lxml.etree", "PyQt5.QtCore"],
                    excludes = [],
                    icon = "icon.ico")

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('start.py', base=base, targetName = 'Matrikels.exe')
]

setup(name='Matrikels',
      version = '0.7',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
