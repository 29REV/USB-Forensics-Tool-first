"""
USB Forensics Tool - Extension Modules Package

This package contains modular extension modules that extend the functionality
of the base USB Forensics Tool without modifying the original source code.

Extension Architecture:
- /extensions/bridge.py - Inter-Process Interface (IPI) for communication
- /extensions/recall_provider.py - Windows 11 Recall forensic data extraction
- /extensions/firmware_validator.py - BadUSB detection and risk assessment
- /extensions/ai_reporter.py - LLM-based narrative report generation

All extensions communicate through the JSON-based bridge interface.
Base tool remains completely untouched.
"""

__version__ = "1.0.0"
__author__ = "USB Forensics Team"

# Import main interface for easy access
try:
    from .bridge import BaseToolExtensionInterface, IPIBridge
    __all__ = ['BaseToolExtensionInterface', 'IPIBridge']
except ImportError:
    __all__ = []

print("✓ Extensions package loaded successfully")
