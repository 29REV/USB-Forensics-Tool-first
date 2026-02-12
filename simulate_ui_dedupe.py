from usb_device_manager import get_all_usb_devices
import re

def ui_key(d):
    vid = (d.vid or "").strip().lower()
    pid = (d.pid or "").strip().lower()
    serial = (d.serial or "").strip().lower()
    if serial:
        manu = (d.manufacturer or "").strip().lower()
        return f"serial:{serial}:{manu}"
    if getattr(d, 'hardware_ids', None):
        hids = ",".join(sorted(h.strip().lower() for h in d.hardware_ids if h))
        if hids:
            return f"hid:{vid}:{pid}:{hids}"
    devid = (d.device_id or "").strip().lower()
    if devid:
        m = re.search(r"(vid_[0-9a-f]{4}[^\\]*pid_[0-9a-f]{4})", devid)
        if m:
            base = m.group(1)
            parts = devid.split('\\')
            if len(parts) >= 3:
                tail = parts[-1]
                tail_clean = tail.split('&')[0] if '&' in tail else tail
                tail_clean = tail_clean.strip()
                if tail_clean:
                    return f"dev:{base}:{tail_clean}"
            return f"dev:{base}"
    return "|".join([
        (d.name or "").strip().lower(),
        (d.manufacturer or "").strip().lower(),
        (d.device_type or "").strip().lower(),
    ])


def simulate():
    devices = get_all_usb_devices()
    print(f"devices count: {len(devices)}")
    deduped = []
    seen = set()
    for d in devices:
        k = ui_key(d)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(d)
    print(f"deduped count: {len(deduped)}")
    # Now simulate row-level dedupe
    seen_rows = set()
    rows = []
    for i, device in enumerate(deduped,1):
        if device.serial:
            serial_display = device.serial
        elif device.device_type in ('hub', 'unknown'):
            serial_display = "N/A"
        else:
            serial_display = "Unknown"
        row_values = (
            device.device_type or 'Unknown',
            device.manufacturer or 'Unknown',
            device.name or 'Unknown',
            serial_display,
            'Connected' if device.connection_status=='Connected' else 'Disconnected'
        )
        row_key = tuple(str(v).strip().lower() for v in row_values)
        if row_key in seen_rows:
            continue
        seen_rows.add(row_key)
        rows.append(row_values)
    print(f"rows count after row-level dedupe: {len(rows)}")
    for r in rows:
        print(r)

if __name__=='__main__':
    simulate()
