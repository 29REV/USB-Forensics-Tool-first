#!/usr/bin/env python3
"""Professional USB Forensics GUI - Modern Design with Side Panel

Features:
  - Professional side navigation panel
  - Real-time USB device detection
  - Storage forensics analysis
  - Timeline analysis with chronological events
  - Device details with images and security info
  - Advanced filtering and search
  - Multi-format report export
  - Security advisory checking
  - Device tree view with categorization
"""

import sys
import ctypes
import os

from gui.app import USBForensicsApp


def _enable_high_dpi():
    if sys.platform != 'win32':
        return

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return
    except Exception:
        pass

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == '__main__':
    _enable_high_dpi()

    if sys.platform == 'win32' and not is_admin():
        # Re-run the program with admin rights
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        # Launch using ShellExecuteW with 'runas' verb to trigger UAC
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

    app = USBForensicsApp()
    app.mainloop()
