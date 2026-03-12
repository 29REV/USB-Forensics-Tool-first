"""Comprehensive USB Device Manager for detecting all USB devices.

This module provides advanced USB device detection capabilities including:
- All USB devices (storage, input, network, etc.)
- Real-time device information via WMI
- Device classification and categorization
- Hardware details and capabilities
"""
import platform
import logging
import subprocess
import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try importing Windows-specific modules
try:
    import win32com.client
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("pywin32 not available - using fallback device detection")


@dataclass
class USBDevice:
    """Comprehensive USB device information."""
    device_id: str
    name: str
    description: str
    manufacturer: str
    device_type: str  # storage, input, network, hub, unknown
    vid: str = ""
    pid: str = ""
    serial: str = ""
    status: str = "OK"
    driver_version: str = ""
    location: str = ""
    speed: str = ""  # USB 1.1, 2.0, 3.0, 3.1, 3.2, 4.0
    power_consumption: str = ""
    capabilities: List[str] = field(default_factory=list)
    hardware_ids: List[str] = field(default_factory=list)
    compatible_ids: List[str] = field(default_factory=list)
    device_class: str = ""
    service: str = ""
    connection_status: str = "Connected"
    last_arrival: Optional[str] = None
    last_removal: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


def classify_device_type(device_info: Dict[str, Any]) -> str:
    """Classify USB device by type based on device info."""
    name = str(device_info.get('name', '')).lower()
    desc = str(device_info.get('description', '')).lower()
    device_class = str(device_info.get('device_class', '')).lower()
    pnp_class = str(device_info.get('pnp_class', '')).lower()
    
    # Storage devices
    if any(x in name or x in desc for x in ['disk', 'storage', 'mass storage', 'usbstor', 'flash', 'thumb']):
        return 'storage'
    if pnp_class == 'diskdrive' or device_class == 'diskdrive':
        return 'storage'
    
    # Input devices
    if any(x in name or x in desc for x in ['mouse', 'keyboard', 'hid', 'input', 'touchpad', 'trackpad']):
        return 'input'
    if pnp_class == 'mouse' or pnp_class == 'keyboard' or pnp_class == 'hid':
        return 'input'
    
    # Network devices
    if any(x in name or x in desc for x in ['network', 'ethernet', 'wifi', 'wireless', 'lan', 'wlan', 'bluetooth']):
        return 'network'
    if pnp_class in ['net', 'network']:
        return 'network'
    
    # Audio/Video
    if any(x in name or x in desc for x in ['audio', 'sound', 'speaker', 'microphone', 'webcam', 'camera', 'video']):
        return 'audio_video'
    if pnp_class in ['media', 'camera', 'sound']:
        return 'audio_video'
    
    # Hubs
    if any(x in name or x in desc for x in ['hub', 'root hub', 'composite']):
        return 'hub'
    if pnp_class == 'usb' and 'hub' in desc:
        return 'hub'
    
    # Printers
    if any(x in name or x in desc for x in ['printer', 'print']):
        return 'printer'
    if pnp_class == 'printer':
        return 'printer'
    
    # Serial/COM devices
    if any(x in name or x in desc for x in ['serial', 'com port', 'uart']):
        return 'serial'
    if pnp_class == 'ports':
        return 'serial'
    
    # Portable devices (phones/tablets over MTP)
    if pnp_class == 'wpd' or 'mtp' in name or 'mtp' in desc or 'portable device' in desc:
        return 'portable'
    
    return 'unknown'


def extract_vid_pid(device_id: str) -> tuple:
    """Extract VID and PID from device ID string."""
    vid, pid = "", ""
    try:
        if 'VID_' in device_id:
            vid_start = device_id.index('VID_') + 4
            vid = device_id[vid_start:vid_start+4]
        if 'PID_' in device_id:
            pid_start = device_id.index('PID_') + 4
            pid = device_id[pid_start:pid_start+4]
    except Exception:
        pass
    return vid, pid


def extract_serial_from_device_id(device_id: str) -> str:
    """Extract serial number from DeviceID string.
    
    For storage devices: USB\VID_XXXX&PID_XXXX\SERIALNUMBER
    For other devices: May be in different format or not available
    
    Args:
        device_id: Device ID string from WMI
        
    Returns:
        Serial number string or empty string if not found
    """
    if not device_id:
        return ""
    
    try:
        # Pattern 1: USB\VID_XXXX&PID_XXXX\SERIAL (most common for storage)
        # Split by backslash to get components
        parts = device_id.split('\\')
        
        if len(parts) >= 3:
            # Third part after VID&PID could be serial
            serial_part = parts[2]
            
            # Check if it looks like an instance ID (contains &) or a serial
            if '&' in serial_part:
                # Instance ID format - serial may be embedded or need registry lookup
                # Sometimes serial is in format: X&XXXXXXXX&X&X where middle part is encoded
                return ""
            elif len(serial_part) > 4:
                # Likely a serial number if it's long enough and no special chars
                # Filter out common instance ID patterns
                if not serial_part.startswith(('6&', '5&', '4&')) and '&' not in serial_part:
                    return serial_part
            elif len(serial_part) > 0:
                # Short serial numbers (some devices have short serials)
                return serial_part
        
        # Pattern 2: Check for serial in middle components
        # Some DeviceIDs have format: USB\VID_XXXX&PID_XXXX\XXXX\SERIAL
        if len(parts) >= 4:
            potential_serial = parts[3]
            if len(potential_serial) > 4 and '&' not in potential_serial:
                return potential_serial
                
    except Exception as e:
        logger.debug(f"Error extracting serial from DeviceID: {e}")
    
    return ""


def get_serial_from_registry(vid: str, pid: str, device_id: str, device_type: str = "") -> str:
    """Try to get serial number from Windows registry.
    
    For storage devices, check USBSTOR registry keys.
    For other devices, check USB registry keys.
    
    Args:
        vid: Vendor ID
        pid: Product ID  
        device_id: Full device ID
        device_type: Device type (storage, input, etc.)
        
    Returns:
        Serial number or empty string
    """
    if not vid or not pid:
        return ""
    
    try:
        import winreg
        
        # Try USBSTOR first (storage devices)
        if device_type == 'storage':
            try:
                base = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
                usbstor_path = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"
                usbstor_key = winreg.OpenKey(base, usbstor_path)
                
                # Look for VID_PID pattern
                vid_pid_pattern = f"VID_{vid.upper()}&PID_{pid.upper()}"
                
                try:
                    i = 0
                    while True:
                        subkey_name = winreg.EnumKey(usbstor_key, i)
                        if vid_pid_pattern in subkey_name.upper():
                            # Open the subkey and check instances
                            subkey = winreg.OpenKey(usbstor_key, subkey_name)
                            try:
                                j = 0
                                while True:
                                    instance = winreg.EnumKey(subkey, j)
                                    # Instance name is often the serial number for storage devices
                                    if len(instance) > 4 and '&' not in instance:
                                        # Additional check: make sure this matches our device
                                        if instance in device_id or device_id.endswith(instance):
                                            return instance
                                    j += 1
                            except OSError:
                                pass
                            finally:
                                winreg.CloseKey(subkey)
                        i += 1
                except OSError:
                    pass
                finally:
                    winreg.CloseKey(usbstor_key)
            except (PermissionError, FileNotFoundError, OSError) as e:
                logger.debug(f"Could not access USBSTOR registry: {e}")
        
        # Try general USB registry for all device types
        try:
            base = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
            usb_path = r"SYSTEM\CurrentControlSet\Enum\USB"
            usb_key = winreg.OpenKey(base, usb_path)
            
            vid_pid_pattern = f"VID_{vid.upper()}&PID_{pid.upper()}"
            
            try:
                i = 0
                while True:
                    subkey_name = winreg.EnumKey(usb_key, i)
                    if vid_pid_pattern in subkey_name.upper():
                        subkey = winreg.OpenKey(usb_key, subkey_name)
                        try:
                            j = 0
                            while True:
                                instance = winreg.EnumKey(subkey, j)
                                
                                # Check if this instance matches our device
                                # DeviceID often ends with instance or contains it
                                if instance in device_id or device_id.endswith(instance):
                                    # Try to get serial from registry value first
                                    try:
                                        instkey = winreg.OpenKey(subkey, instance)
                                        try:
                                            serial, _ = winreg.QueryValueEx(instkey, "SerialNumber")
                                            if serial and len(str(serial)) > 0:
                                                winreg.CloseKey(instkey)
                                                return str(serial)
                                        except (OSError, FileNotFoundError):
                                            pass
                                        
                                        # Also check for ParentIdPrefix which sometimes contains serial info
                                        try:
                                            parent_id, _ = winreg.QueryValueEx(instkey, "ParentIdPrefix")
                                            if parent_id and len(str(parent_id)) > 4:
                                                # Sometimes serial is in parent ID prefix
                                                serial_candidate = str(parent_id)
                                                if '&' not in serial_candidate:
                                                    winreg.CloseKey(instkey)
                                                    return serial_candidate
                                        except (OSError, FileNotFoundError):
                                            pass
                                        
                                        winreg.CloseKey(instkey)
                                        
                                        # If no SerialNumber value, instance name might be serial
                                        # But only if it looks like a serial (not instance ID with &)
                                        if '&' not in instance and len(instance) > 4:
                                            return instance
                                    except (OSError, FileNotFoundError):
                                        # If we can't open instance key, instance name might still be serial
                                        if '&' not in instance and len(instance) > 4:
                                            return instance
                                j += 1
                        except OSError:
                            pass
                        finally:
                            winreg.CloseKey(subkey)
                    i += 1
            except OSError:
                pass
            finally:
                winreg.CloseKey(usb_key)
        except (PermissionError, FileNotFoundError, OSError) as e:
            logger.debug(f"Could not access USB registry: {e}")
            
    except Exception as e:
        logger.debug(f"Error getting serial from registry: {e}")
    
    return ""


def get_usb_speed(device_info: Dict[str, Any]) -> str:
    """Determine USB speed from device info."""
    # Try to detect from device properties
    desc = str(device_info.get('description', '')).lower()
    
    if 'usb 3.2' in desc or 'superspeed+' in desc:
        return 'USB 3.2 (20 Gbps)'
    if 'usb 3.1' in desc or 'superspeed+' in desc:
        return 'USB 3.1 (10 Gbps)'
    if 'usb 3.0' in desc or 'superspeed' in desc:
        return 'USB 3.0 (5 Gbps)'
    if 'usb 2.0' in desc or 'high-speed' in desc or 'hi-speed' in desc:
        return 'USB 2.0 (480 Mbps)'
    if 'usb 1.1' in desc or 'full-speed' in desc:
        return 'USB 1.1 (12 Mbps)'
    if 'usb 1.0' in desc or 'low-speed' in desc:
        return 'USB 1.0 (1.5 Mbps)'
    
    return 'Unknown'


def get_all_usb_devices_wmi() -> List[USBDevice]:
    """Get all USB devices using WMI (Windows only)."""
    if not WMI_AVAILABLE:
        logger.warning("WMI not available - returning mock data")
        return get_mock_usb_devices()
    
    devices = []
    
    try:
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        
        # Query PnP devices including USB and Portable (WPD/MTP) devices
        query = (
            "SELECT * FROM Win32_PnPEntity WHERE "
            "DeviceID LIKE '%USB%' OR "
            "PNPDeviceID LIKE '%USB%' OR "
            "PNPDeviceID LIKE 'USBSTOR%' OR "
            "PNPDeviceID LIKE 'SWD\\\\WPDBUSENUM%' OR "
            "PNPClass = 'WPD' OR "
            "Service LIKE '%USB%' OR "
            "Service LIKE '%Wpd%'"
        )
        usb_devices = service.ExecQuery(query)
        
        for device in usb_devices:
            try:
                device_id = str(device.DeviceID) if device.DeviceID else ""
                name = str(device.Name) if device.Name else "Unknown Device"
                description = str(device.Description) if device.Description else name
                manufacturer = str(device.Manufacturer) if device.Manufacturer else "Unknown"
                status = str(device.Status) if device.Status else "Unknown"
                pnp_class = str(device.PNPClass) if device.PNPClass else ""
                service = str(device.Service) if device.Service else ""
                
                vid, pid = extract_vid_pid(device_id)
                
                device_info = {
                    'name': name,
                    'description': description,
                    'device_class': pnp_class,
                    'pnp_class': pnp_class
                }
                
                device_type = classify_device_type(device_info)
                speed = get_usb_speed(device_info)
                
                # Extract serial number - try multiple methods
                serial = extract_serial_from_device_id(device_id)
                if not serial:
                    # Try registry lookup (requires registry access, may fail without admin)
                    serial = get_serial_from_registry(vid, pid, device_id, device_type)
                
                # If still no serial, try to get from WMI DeviceID property directly
                if not serial:
                    try:
                        # Some devices expose serial in the PNPDeviceID or other properties
                        if hasattr(device, 'PNPDeviceID'):
                            pnp_id = str(device.PNPDeviceID)
                            serial = extract_serial_from_device_id(pnp_id)
                    except Exception:
                        pass
                
                # Clean up serial - remove any invalid characters
                if serial:
                    # Remove common unwanted patterns
                    serial = serial.strip()
                    # Some serials have trailing/leading slashes or backslashes
                    serial = serial.strip('\\/')
                
                # Get hardware IDs if available
                hardware_ids = []
                try:
                    if device.HardwareID:
                        hardware_ids = [str(id) for id in device.HardwareID]
                except Exception:
                    pass
                
                # Get compatible IDs if available
                compatible_ids = []
                try:
                    if device.CompatibleID:
                        compatible_ids = [str(id) for id in device.CompatibleID]
                except Exception:
                    pass
                
                usb_device = USBDevice(
                    device_id=device_id,
                    name=name,
                    description=description,
                    manufacturer=manufacturer,
                    device_type=device_type,
                    vid=vid,
                    pid=pid,
                    serial=serial if serial else "",  # Set serial number
                    status=status,
                    speed=speed,
                    device_class=pnp_class,
                    service=service,
                    hardware_ids=hardware_ids,
                    compatible_ids=compatible_ids,
                    connection_status="Connected"
                )
                
                devices.append(usb_device)
                
            except Exception as e:
                logger.error(f"Error processing device: {e}")
                continue
        
        logger.info(f"Found {len(devices)} USB devices via WMI")
        
    except Exception as e:
        logger.error(f"WMI query failed: {e}")
        return get_mock_usb_devices()
    
    return devices


def get_all_usb_devices_powershell() -> List[USBDevice]:
    """Fallback USB/WPD device detection via PowerShell (Windows only)."""
    devices: List[USBDevice] = []
    
    ps_script = (
        "$devices = Get-PnpDevice -PresentOnly | "
        "Where-Object { "
        "$_.InstanceId -like 'USB*' -or "
        "$_.InstanceId -like 'USBSTOR*' -or "
        "$_.InstanceId -like 'SWD\\\\WPDBUSENUM*' -or "
        "$_.Class -eq 'WPD' -or "
        "$_.Service -like '*Wpd*' -or "
        "$_.Service -like '*USB*' "
        "} | Select-Object InstanceId, FriendlyName, Class, Manufacturer, Status, Service, Description; "
        "$devices | ConvertTo-Json -Compress"
    )
    
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0 or not result.stdout.strip():
            logger.warning(f"PowerShell device query failed: {result.stderr.strip()}")
            return devices
        
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
        
        for item in data:
            try:
                device_id = str(item.get("InstanceId") or "")
                name = str(item.get("FriendlyName") or "Unknown Device")
                description = str(item.get("Description") or name)
                manufacturer = str(item.get("Manufacturer") or "Unknown")
                status = str(item.get("Status") or "Unknown")
                pnp_class = str(item.get("Class") or "")
                service = str(item.get("Service") or "")
                
                vid, pid = extract_vid_pid(device_id)
                
                device_info = {
                    'name': name,
                    'description': description,
                    'device_class': pnp_class,
                    'pnp_class': pnp_class
                }
                
                device_type = classify_device_type(device_info)
                speed = get_usb_speed(device_info)
                serial = extract_serial_from_device_id(device_id)
                
                usb_device = USBDevice(
                    device_id=device_id,
                    name=name,
                    description=description,
                    manufacturer=manufacturer,
                    device_type=device_type,
                    vid=vid,
                    pid=pid,
                    serial=serial if serial else "",
                    status=status,
                    speed=speed,
                    device_class=pnp_class,
                    service=service,
                    connection_status="Connected"
                )
                
                devices.append(usb_device)
            except Exception as e:
                logger.error(f"Error processing PowerShell device: {e}")
                continue
    except Exception as e:
        logger.error(f"PowerShell device detection failed: {e}")
    
    logger.info(f"Found {len(devices)} USB devices via PowerShell")
    return devices


def get_all_usb_devices() -> List[USBDevice]:
    """Get all USB devices - cross-platform wrapper."""
    def _key(dev: USBDevice) -> str:
        """Create a normalized key for deduplication.

        Priority:
        1. Serial (when available) + VID:PID
        2. Hardware IDs + VID:PID
        3. Normalized VID:PID + instance suffix (if parseable)
        4. Fallback to name+manufacturer+device_type
        """
        try:
            vid = (dev.vid or "").strip().lower()
            pid = (dev.pid or "").strip().lower()
            serial = (dev.serial or "").strip().lower()

            if serial:
                # Deduplicate primarily by serial only; allow merging across sources
                return f"serial:{serial}"

            if dev.hardware_ids:
                hids = ",".join(sorted(h.strip().lower() for h in dev.hardware_ids if h))
                if hids:
                    return f"hid:{vid}:{pid}:{hids}"

            devid = (dev.device_id or "").strip().lower()
            if devid:
                # Try to extract vid/pid block
                m = re.search(r"(vid_[0-9a-f]{4}[^\\]*pid_[0-9a-f]{4})", devid)
                if m:
                    base = m.group(1)
                    # Use trailing instance component if it looks like a serial (no &)
                    parts = devid.split('\\')
                    if len(parts) >= 3:
                        tail = parts[-1]
                        tail_clean = tail.split('&')[0] if '&' in tail else tail
                        tail_clean = tail_clean.strip()
                        if tail_clean:
                            return f"dev:{base}:{tail_clean}"
                    return f"dev:{base}"

            # Fallback
            return "|".join([
                (dev.name or "").strip().lower(),
                (dev.manufacturer or "").strip().lower(),
                (dev.device_type or "").strip().lower(),
            ])
        except Exception:
            return (dev.device_id or "").strip().lower() or f"{dev.name}:{dev.manufacturer}:{dev.device_type}"

    if platform.system() == 'Windows':
        devices = get_all_usb_devices_wmi() if WMI_AVAILABLE else []
        if not devices:
            devices = get_all_usb_devices_powershell()
        if not devices:
            return get_mock_usb_devices()

        # Merge devices by key; when duplicates found, prefer non-empty fields
        merged: Dict[str, USBDevice] = {}
        for d in devices:
            key = _key(d)
            if key in merged:
                existing = merged[key]
                # Merge simple scalar fields if missing in existing
                for attr in ['device_id','name','description','manufacturer','device_type','vid','pid','serial','status','driver_version','location','speed','power_consumption','device_class','service','connection_status']:
                    val = getattr(existing, attr, None)
                    newval = getattr(d, attr, None)
                    if (not val or val == '') and newval:
                        setattr(existing, attr, newval)
                # Merge lists
                for list_attr in ['capabilities','hardware_ids','compatible_ids']:
                    ev = getattr(existing, list_attr, []) or []
                    nv = getattr(d, list_attr, []) or []
                    combined = ev[:]
                    for item in nv:
                        if item and item not in combined:
                            combined.append(item)
                    setattr(existing, list_attr, combined)
            else:
                merged[key] = d

        return list(merged.values())
    else:
        logger.warning("Non-Windows platform - returning mock data")
        return get_mock_usb_devices()


def get_mock_usb_devices() -> List[USBDevice]:
    """Generate mock USB devices for testing/demo."""
    return [
        USBDevice(
            device_id="USB\\VID_0781&PID_5567\\4C530001234567890123",
            name="SanDisk Cruzer Blade USB Device",
            description="USB Mass Storage Device",
            manufacturer="SanDisk",
            device_type="storage",
            vid="0781",
            pid="5567",
            serial="4C530001234567890123",
            status="OK",
            speed="USB 2.0 (480 Mbps)",
            device_class="DiskDrive",
            connection_status="Connected"
        ),
        USBDevice(
            device_id="USB\\VID_046D&PID_C52B\\6&2E9A8B8C&0&2",
            name="Logitech USB Optical Mouse",
            description="HID-compliant mouse",
            manufacturer="Logitech",
            device_type="input",
            vid="046D",
            pid="C52B",
            status="OK",
            speed="USB 2.0 (480 Mbps)",
            device_class="Mouse",
            connection_status="Connected"
        ),
        USBDevice(
            device_id="USB\\VID_413C&PID_2113\\6&2E9A8B8C&0&3",
            name="Dell USB Keyboard",
            description="HID Keyboard Device",
            manufacturer="Dell",
            device_type="input",
            vid="413C",
            pid="2113",
            status="OK",
            speed="USB 2.0 (480 Mbps)",
            device_class="Keyboard",
            connection_status="Connected"
        ),
        USBDevice(
            device_id="USB\\VID_8087&PID_0A2B\\5&2AB8E787&0&1",
            name="Intel(R) Wireless Bluetooth(R)",
            description="Bluetooth Device",
            manufacturer="Intel",
            device_type="network",
            vid="8087",
            pid="0A2B",
            status="OK",
            speed="USB 2.0 (480 Mbps)",
            device_class="Bluetooth",
            connection_status="Connected"
        ),
        USBDevice(
            device_id="USB\\ROOT_HUB30\\4&36F72C7F&0&0",
            name="USB Root Hub (USB 3.0)",
            description="Generic USB Hub",
            manufacturer="Microsoft",
            device_type="hub",
            status="OK",
            speed="USB 3.0 (5 Gbps)",
            device_class="USB",
            connection_status="Connected"
        )
    ]


def get_device_summary(device: USBDevice) -> Dict[str, Any]:
    """Get summary dict from USBDevice for display."""
    return {
        'device_id': device.device_id,
        'name': device.name,
        'description': device.description,
        'manufacturer': device.manufacturer,
        'device_type': device.device_type,
        'vid': device.vid,
        'pid': device.pid,
        'serial': device.serial,
        'status': device.status,
        'speed': device.speed,
        'device_class': device.device_class,
        'connection_status': device.connection_status,
        'hardware_ids': device.hardware_ids,
        'compatible_ids': device.compatible_ids,
        'service': device.service
    }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    print("Scanning for USB devices...\n")
    devices = get_all_usb_devices()
    print(f"Found {len(devices)} USB devices:\n")
    
    for device in devices:
        print(f"Name: {device.name}")
        print(f"Type: {device.device_type}")
        print(f"Manufacturer: {device.manufacturer}")
        print(f"VID:PID: {device.vid}:{device.pid}")
        print(f"Speed: {device.speed}")
        print(f"Status: {device.status}")
        print("-" * 60)
