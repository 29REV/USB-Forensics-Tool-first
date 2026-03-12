from usb_device_manager import get_all_usb_devices

devices = get_all_usb_devices()
print(f"Total devices returned: {len(devices)}\n")
for i,d in enumerate(devices,1):
    print(f"[{i}] device_id: {repr(d.device_id)}")
    print(f"    name: {repr(d.name)}")
    print(f"    manufacturer: {repr(d.manufacturer)}")
    print(f"    vid: {repr(d.vid)} pid: {repr(d.pid)}")
    print(f"    serial: {repr(d.serial)}")
    print(f"    hardware_ids: {repr(getattr(d,'hardware_ids', None))}")
    print(f"    compatible_ids: {repr(getattr(d,'compatible_ids', None))}")
    print()
