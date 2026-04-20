"""Optional Wireshark/tshark integration for USB capture analysis.

This module is intentionally passive: it only inspects saved captures when
explicitly requested by the caller.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import json
import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class TracePacket:
    frame_number: int
    timestamp: str
    epoch: float
    protocols: List[str]
    bus_id: str = ""
    device_address: str = ""
    vendor_id: str = ""
    product_id: str = ""
    transfer_type: str = ""
    endpoint: str = ""
    setup_request: str = ""
    request_type: str = ""
    descriptor_type: str = ""
    interface_class: str = ""
    interface_subclass: str = ""
    interface_protocol: str = ""
    data_length: int = 0
    status: str = ""
    source: str = ""
    destination: str = ""
    payload_preview: str = ""


def _append_value(flat: Dict[str, List[str]], key: str, value: Any) -> None:
    if value is None:
        return
    if isinstance(value, (str, int, float, bool)):
        text = str(value).strip()
        if text:
            flat[key].append(text)


def _flatten_layer(value: Any, flat: Dict[str, List[str]], current_key: str = "") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            next_key = key if not current_key else key if "." in key else f"{current_key}.{key}"
            _flatten_layer(nested, flat, next_key)
        return

    if isinstance(value, list):
        for item in value:
            _flatten_layer(item, flat, current_key)
        return

    if current_key:
        _append_value(flat, current_key, value)


def _first_value(flat: Dict[str, List[str]], *keys: str, default: str = "") -> str:
    for key in keys:
        values = flat.get(key)
        if values:
            for value in values:
                if value:
                    return value
    return default


def _parse_numeric(value: str) -> int:
    if not value:
        return 0
    text = value.strip()
    try:
        if text.lower().startswith("0x"):
            return int(text, 16)
        return int(float(text))
    except Exception:
        return 0


class WiresharkBridge:
    def __init__(self, workspace_root: str, source_dir: str = "wireshark-4.6.4") -> None:
        self.workspace_root = Path(workspace_root)
        self.source_root = self.workspace_root / source_dir

    def inspect_source_tree(self) -> Dict[str, Any]:
        return {
            "source_present": self.source_root.exists(),
            "source_root": str(self.source_root),
            "tshark_source_present": (self.source_root / "tshark.c").exists(),
            "etwdump_source_present": (self.source_root / "extcap" / "etwdump.c").exists(),
        }

    def locate_tshark(self, override_path: Optional[str] = None) -> Optional[str]:
        candidates: List[Path] = []

        if override_path:
            candidates.append(Path(override_path))

        which_path = shutil.which("tshark")
        if which_path:
            candidates.append(Path(which_path))

        source_candidates = [
            self.source_root / "run" / "tshark.exe",
            self.source_root / "run" / "RelWithDebInfo" / "tshark.exe",
            self.source_root / "run" / "Debug" / "tshark.exe",
            self.source_root / "build" / "run" / "tshark.exe",
            self.source_root / "build" / "run" / "RelWithDebInfo" / "tshark.exe",
            self.source_root / "build" / "run" / "Debug" / "tshark.exe",
        ]
        candidates.extend(source_candidates)

        for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
            base_dir = os.environ.get(env_name)
            if base_dir:
                candidates.append(Path(base_dir) / "Wireshark" / "tshark.exe")

        seen: set[str] = set()
        for candidate in candidates:
            candidate_text = str(candidate)
            if candidate_text in seen:
                continue
            seen.add(candidate_text)
            if candidate.exists() and candidate.is_file():
                logger.debug("Using tshark at %s", candidate)
                return candidate_text

        return None

    def locate_wireshark(self, override_path: Optional[str] = None) -> Optional[str]:
        candidates: List[Path] = []

        if override_path:
            candidates.append(Path(override_path))

        which_path = shutil.which("wireshark")
        if which_path:
            candidates.append(Path(which_path))

        source_candidates = [
            self.source_root / "run" / "Wireshark.exe",
            self.source_root / "run" / "RelWithDebInfo" / "Wireshark.exe",
            self.source_root / "run" / "Debug" / "Wireshark.exe",
            self.source_root / "build" / "run" / "Wireshark.exe",
            self.source_root / "build" / "run" / "RelWithDebInfo" / "Wireshark.exe",
            self.source_root / "build" / "run" / "Debug" / "Wireshark.exe",
        ]
        candidates.extend(source_candidates)

        for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
            base_dir = os.environ.get(env_name)
            if base_dir:
                candidates.append(Path(base_dir) / "Wireshark" / "Wireshark.exe")

        seen: set[str] = set()
        for candidate in candidates:
            candidate_text = str(candidate)
            if candidate_text in seen:
                continue
            seen.add(candidate_text)
            if candidate.exists() and candidate.is_file():
                logger.debug("Using Wireshark at %s", candidate)
                return candidate_text

        return None

    def launch_wireshark(self, capture_file: Optional[str] = None, wireshark_override: Optional[str] = None) -> str:
        wireshark_path = self.locate_wireshark(wireshark_override)
        if not wireshark_path:
            raise RuntimeError("Wireshark executable was not found. Install Wireshark or build it from source.")

        command = [wireshark_path]
        if capture_file:
            capture_path = Path(capture_file)
            if capture_path.exists():
                command.append(str(capture_path))

        logger.info("Launching Wireshark: %s", command)
        subprocess.Popen(command, cwd=str(Path(wireshark_path).parent))
        return wireshark_path

    def runtime_info(self, tshark_override: Optional[str] = None) -> Dict[str, Any]:
        source_info = self.inspect_source_tree()
        tshark_path = self.locate_tshark(tshark_override)
        ready = bool(tshark_path)
        message = "tshark is available for capture analysis" if ready else (
            "Wireshark source is present but tshark is not built or installed"
            if source_info["source_present"]
            else "No Wireshark source or tshark binary found"
        )
        return {
            **source_info,
            "tshark_path": tshark_path or "",
            "ready": ready,
            "message": message,
        }

    def load_capture(
        self,
        capture_file: str,
        tshark_override: Optional[str] = None,
        packet_limit: int = 2500,
        display_filter: str = "usb",
    ) -> Tuple[List[TracePacket], Dict[str, Any]]:
        capture_path = Path(capture_file)
        if not capture_path.exists():
            raise FileNotFoundError(f"Capture file not found: {capture_file}")

        suffix = capture_path.suffix.lower()
        if suffix in {".json", ".ndjson"}:
            packets = self._load_packets_from_json_file(capture_path)
            return packets, {
                "capture_file": str(capture_path),
                "capture_source": "json",
                "packet_count": len(packets),
            }

        tshark_path = self.locate_tshark(tshark_override)
        if not tshark_path:
            raise RuntimeError(
                "tshark was not found. Build Wireshark or install Wireshark/tshark, "
                "or provide a tshark JSON export file instead."
            )

        command = [
            tshark_path,
            "-r",
            str(capture_path),
            "-Y",
            display_filter,
            "-T",
            "json",
            "-n",
            "-c",
            str(packet_limit),
        ]

        logger.info("Running tshark for optional USB trace analysis: %s", command)
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "tshark failed")

        packets = self._load_packets_from_json_payload(completed.stdout)
        return packets, {
            "capture_file": str(capture_path),
            "capture_source": "tshark",
            "tshark_path": tshark_path,
            "packet_count": len(packets),
            "display_filter": display_filter,
        }

    def _load_packets_from_json_file(self, capture_path: Path) -> List[TracePacket]:
        content = capture_path.read_text(encoding="utf-8", errors="replace").strip()
        return self._load_packets_from_json_payload(content)

    def _load_packets_from_json_payload(self, content: str) -> List[TracePacket]:
        if not content:
            return []

        content = content.strip()
        if content.startswith("["):
            raw_entries = json.loads(content)
        else:
            raw_entries = []
            for line in content.splitlines():
                line = line.strip()
                if line:
                    raw_entries.append(json.loads(line))

        packets: List[TracePacket] = []
        for entry in raw_entries:
            try:
                packets.append(self._packet_from_entry(entry))
            except Exception as exc:
                logger.debug("Skipping malformed tshark JSON packet: %s", exc)
        return packets

    def _packet_from_entry(self, entry: Dict[str, Any]) -> TracePacket:
        layers = entry.get("_source", {}).get("layers", {})
        flat: Dict[str, List[str]] = defaultdict(list)
        _flatten_layer(layers, flat)

        frame_number = _parse_numeric(_first_value(flat, "frame.number"))
        epoch_text = _first_value(flat, "frame.time_epoch")
        protocols_text = _first_value(flat, "frame.protocols")
        protocols = [item for item in protocols_text.split(":") if item]

        endpoint_number = _first_value(flat, "usb.endpoint_number", "usb.endpoint_address")
        if endpoint_number:
            endpoint = endpoint_number
        else:
            endpoint = _first_value(flat, "usb.endpoint_number.direction")

        return TracePacket(
            frame_number=frame_number,
            timestamp=_first_value(flat, "frame.time", "frame.time_utc"),
            epoch=float(epoch_text) if epoch_text else 0.0,
            protocols=protocols,
            bus_id=_first_value(flat, "usb.bus_id", "usb.busid"),
            device_address=_first_value(flat, "usb.device_address", "usb.device_address32", "usb.addr"),
            vendor_id=_first_value(
                flat,
                "usb.idVendor",
                "usb.idvendor",
                "usbhub.descriptor.idVendor",
                "usb.descriptor.idVendor",
            ),
            product_id=_first_value(
                flat,
                "usb.idProduct",
                "usb.idproduct",
                "usbhub.descriptor.idProduct",
                "usb.descriptor.idProduct",
            ),
            transfer_type=_first_value(flat, "usb.transfer_type", "usb.transfer", "usb.urb_type"),
            endpoint=endpoint,
            setup_request=_first_value(flat, "usb.setup.bRequest", "usb.bRequest", "usb.setup.brequest"),
            request_type=_first_value(flat, "usb.setup.bmRequestType", "usb.bmRequestType"),
            descriptor_type=_first_value(flat, "usb.descriptor_type", "usb.setup.wValue", "usbhub.descriptor.type"),
            interface_class=_first_value(flat, "usb.bInterfaceClass", "usb.interface_class", "usbhid.boot_report_descriptor.descriptor_type"),
            interface_subclass=_first_value(flat, "usb.bInterfaceSubClass", "usb.interface_subclass"),
            interface_protocol=_first_value(flat, "usb.bInterfaceProtocol", "usb.interface_protocol"),
            data_length=_parse_numeric(_first_value(flat, "usb.data_len", "usb.capdata.len", "usb.setup.wLength")),
            status=_first_value(flat, "usb.urb_status", "usb.status", "usb.transfer_status"),
            source=_first_value(flat, "usb.src", "usb.src_device"),
            destination=_first_value(flat, "usb.dst", "usb.dst_device"),
            payload_preview=_first_value(flat, "usb.capdata", "usbhid.data", "usb.data_fragment"),
        )


def packets_to_dicts(packets: Iterable[TracePacket]) -> List[Dict[str, Any]]:
    return [asdict(packet) for packet in packets]