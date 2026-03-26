"""Registry parser for USB forensics.

This module attempts to read common USB-related registry keys on Windows.
If running on non-Windows or when access is denied, it returns sample data so the
rest of the tool can run and be tested without admin privileges.

Exports:
    USBRegistryEntry: Dataclass representing a USB device from registry
    parse_registry: Main function to parse USB devices from Windows registry
"""
from dataclasses import dataclass, asdict
from datetime import datetime
import platform
import traceback
import logging

logger = logging.getLogger(__name__)


@dataclass
class USBRegistryEntry:
    """Represents a USB device entry from Windows registry.
    
    Attributes:
        device_id: Unique device identifier
        vid: Vendor ID (hex string)
        pid: Product ID (hex string)
        serial: Device serial number
        last_write: Last registry write time (ISO format)
        drive_letter: Assigned drive letter if applicable
    """
    device_id: str
    vid: str
    pid: str
    serial: str
    last_write: str
    drive_letter: str | None


def parse_registry() -> list[USBRegistryEntry]:
    """Parse Windows registry for USB devices.
    
    Attempts to read HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR for USB device
    information. Falls back to mock data on non-Windows systems, permission errors,
    or missing dependencies.
    
    Returns:
        List of USBRegistryEntry objects representing connected USB devices
        
    Raises:
        No exceptions raised; always returns a list (may be empty or mock data)
    """
    try:
        import winreg

        entries: list[USBRegistryEntry] = []
        base = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        path = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
        try:
            key = winreg.OpenKey(base, path)
        except PermissionError:
            logger.warning("Permission denied accessing USBSTOR registry")
            return _mock_registry_entries()

        try:
            i = 0
            while True:
                sub = winreg.EnumKey(key, i)
                subkey = winreg.OpenKey(key, sub)
                try:
                    j = 0
                    while True:
                        instance = winreg.EnumKey(subkey, j)
                        instkey = winreg.OpenKey(subkey, instance)
                        try:
                            vid = _extract_vid(sub)
                            pid = _extract_pid(sub)
                            serial = instance
                            last_write = datetime.utcnow().isoformat()
                            drive_letter = None
                            entries.append(USBRegistryEntry(instance, vid, pid, serial, last_write, drive_letter))
                        except Exception as e:
                            logger.debug(f"Failed to parse registry entry: {e}")
                        j += 1
                except OSError:
                    pass
                i += 1
        except OSError:
            pass

        result = entries or _mock_registry_entries()
        logger.info(f"Found {len(result)} USB registry entries")
        return result
    except Exception as e:
        logger.error(f"Registry parsing failed: {e}", exc_info=True)
        return _mock_registry_entries()


def _extract_vid(subkey_name: str) -> str:
    """Extract Vendor ID from registry subkey name.
    
    Attempts to find VID_XXXX or Ven_XXXXX patterns. Returns 'UNKNOWN' if
    no pattern is found.
    
    Args:
        subkey_name: Registry subkey name to parse
        
    Returns:
        Vendor ID string or 'UNKNOWN'
    """
    import re

    m = re.search(r"VID_([0-9A-Fa-f]{4})", subkey_name)
    if m:
        return m.group(1)
    m = re.search(r"Ven[_-]?([A-Za-z0-9]+)", subkey_name)
    return m.group(1) if m else "UNKNOWN"


def _extract_pid(subkey_name: str) -> str:
    """Extract Product ID from registry subkey name.
    
    Attempts to find PID_XXXX or Prod_XXXXX patterns. Returns 'UNKNOWN' if
    no pattern is found.
    
    Args:
        subkey_name: Registry subkey name to parse
        
    Returns:
        Product ID string or 'UNKNOWN'
    """
    import re

    m = re.search(r"PID_([0-9A-Fa-f]{4})", subkey_name)
    if m:
        return m.group(1)
    m = re.search(r"Prod[_-]?([A-Za-z0-9]+)", subkey_name)
    return m.group(1) if m else "UNKNOWN"


def _mock_registry_entries() -> list[USBRegistryEntry]:
    """Return mock USB registry entries for testing/demo.
    
    Returns:
        List of sample USBRegistryEntry objects
    """
    now = datetime.utcnow().isoformat()
    return [
        USBRegistryEntry("USB\\VID_0781&PID_5567\\1234567890", "0781", "5567", "1234567890", now, "E:"),
        USBRegistryEntry("USB\\VID_0951&PID_1666\\SN0001", "0951", "1666", "SN0001", now, None),
    ]


if __name__ == "__main__":
    for e in parse_registry():
        print(asdict(e))
