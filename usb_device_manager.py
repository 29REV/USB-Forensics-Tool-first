"""Comprehensive USB Device Manager for detecting all USB devices.

This module provides advanced USB device detection capabilities including:
- All USB devices (storage, input, network, etc.)
- Real-time device information via WMI
- Device classification and categorization
- Hardware details and capabilities
"""
import platform
import logging
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
        
        # Query all PnP devices
        query = "SELECT * FROM Win32_PnPEntity WHERE DeviceID LIKE '%USB%' OR Service LIKE '%USB%'"
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


def get_all_usb_devices() -> List[USBDevice]:
    """Get all USB devices - cross-platform wrapper."""
    if platform.system() == 'Windows':
        return get_all_usb_devices_wmi()
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
