#!/usr/bin/env python3
"""USB Forensics Tool - Professional Edition

A comprehensive USB device analysis platform with Wireshark-level detail.

Developed by:
  - Srirevanth A
  - Naghul Pranav C B
  - Deeekshitha

Version: 2.0
Release: December 2025
"""

import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point - show splash screen then launch GUI."""
    try:
        # Import and show splash screen
        logger.info("Loading splash screen...")
        from splash import show_splash
        show_splash()
        
        # Launch main GUI
        logger.info("Launching professional GUI...")
        from gui_enhanced import USBForensicsApp
        
        app = USBForensicsApp()
        logger.info("GUI initialized successfully")
        app.mainloop()
        logger.info("Application closed normally")
        
    except ImportError as e:
        logger.error(f"Import error: {e}", exc_info=True)
        print(f"ERROR: Failed to import required modules: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
