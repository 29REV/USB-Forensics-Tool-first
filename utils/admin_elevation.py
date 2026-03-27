"""Helpers to prompt for and request Windows administrator elevation."""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Optional


def is_running_as_admin() -> bool:
    """Return True if current process has administrator privileges on Windows."""
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> bool:
    """Relaunch current Python process with elevation prompt and return success."""
    if os.name != "nt":
        return False

    python_executable = sys.executable
    params = subprocess.list2cmdline(sys.argv)
    result = ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        python_executable,
        params,
        None,
        1,
    )
    return int(result) > 32


def prompt_run_as_administrator(parent: Optional[tk.Misc] = None, reason: str = "Some forensic features require admin rights.") -> bool:
    """Show a prompt and relaunch elevated if accepted."""
    if os.name != "nt":
        messagebox.showinfo("Administrator", "Administrator elevation is available only on Windows.", parent=parent)
        return False

    if is_running_as_admin():
        messagebox.showinfo("Administrator", "Application is already running as administrator.", parent=parent)
        return False

    approved = messagebox.askyesno(
        "Run as administrator",
        f"{reason}\n\nDo you want to restart the app with administrator privileges?",
        parent=parent,
    )
    if not approved:
        return False

    if relaunch_as_admin():
        os._exit(0)

    messagebox.showerror(
        "Run as administrator",
        "Could not relaunch with administrator privileges.",
        parent=parent,
    )
    return False
