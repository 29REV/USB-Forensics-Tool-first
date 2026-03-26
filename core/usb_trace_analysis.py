"""Heuristics for optional USB behavior analysis from Wireshark/tshark captures."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional
import logging

from core.wireshark_bridge import TracePacket

logger = logging.getLogger(__name__)

REQUEST_NAMES = {
    0x00: "GET_STATUS",
    0x01: "CLEAR_FEATURE",
    0x03: "SET_FEATURE",
    0x05: "SET_ADDRESS",
    0x06: "GET_DESCRIPTOR",
    0x07: "SET_DESCRIPTOR",
    0x08: "GET_CONFIGURATION",
    0x09: "SET_CONFIGURATION",
    0x0A: "GET_INTERFACE",
    0x0B: "SET_INTERFACE",
}

DESCRIPTOR_NAMES = {
    0x01: "Device Descriptor",
    0x02: "Configuration Descriptor",
    0x03: "String Descriptor",
    0x04: "Interface Descriptor",
    0x05: "Endpoint Descriptor",
    0x0F: "BOS Descriptor",
}

INTERFACE_CLASS_NAMES = {
    0x03: "Human Interface Device",
    0x08: "Mass Storage",
    0x09: "Hub",
    0x0A: "CDC Data",
    0x0E: "Video",
    0xE0: "Wireless Controller",
}


def _to_int(value: str) -> int:
    if not value:
        return 0
    text = value.strip()
    try:
        if text.lower().startswith("0x"):
            return int(text, 16)
        return int(float(text))
    except Exception:
        return 0


def _normalize_hex(value: str) -> str:
    if not value:
        return ""
    if value.lower().startswith("0x"):
        return value.lower()
    parsed = _to_int(value)
    if parsed:
        width = 4 if parsed > 0xFF else 2
        return f"0x{parsed:0{width}x}"
    return value.lower()


def _interface_name(packet: TracePacket) -> str:
    class_code = _to_int(packet.interface_class)
    return INTERFACE_CLASS_NAMES.get(class_code, "Unknown") if class_code else "Unknown"


def _request_name(packet: TracePacket) -> str:
    request_code = _to_int(packet.setup_request)
    return REQUEST_NAMES.get(request_code, "")


def _descriptor_name(packet: TracePacket) -> str:
    descriptor_raw = _to_int(packet.descriptor_type)
    if descriptor_raw > 0xFF:
        descriptor_raw = (descriptor_raw >> 8) & 0xFF
    return DESCRIPTOR_NAMES.get(descriptor_raw, "")


def _packet_device_key(packet: TracePacket) -> str:
    if packet.bus_id or packet.device_address:
        return f"bus:{packet.bus_id or '?'}|addr:{packet.device_address or '?'}|vid:{packet.vendor_id or '?'}|pid:{packet.product_id or '?'}"
    if packet.vendor_id or packet.product_id:
        return f"vid:{packet.vendor_id or '?'}|pid:{packet.product_id or '?'}"
    return "global"


def _group_packets(packets: Iterable[TracePacket]) -> Dict[str, List[TracePacket]]:
    grouped: Dict[str, List[TracePacket]] = defaultdict(list)
    for packet in packets:
        grouped[_packet_device_key(packet)].append(packet)
    return grouped


def _device_hint_score(report: Dict[str, Any], device_hint: Optional[Dict[str, Any]]) -> int:
    if not device_hint:
        return 0

    score = 0
    hint_vid = str(device_hint.get("vid") or "").lower()
    hint_pid = str(device_hint.get("pid") or "").lower()
    report_vid = str(report.get("vendor_id") or "").lower()
    report_pid = str(report.get("product_id") or "").lower()
    if hint_vid and hint_vid == report_vid:
        score += 5
    if hint_pid and hint_pid == report_pid:
        score += 5

    hint_name = str(device_hint.get("name") or "").lower()
    classes = " ".join(report.get("interface_classes", []))
    if hint_name and any(token and token in classes.lower() for token in hint_name.split()):
        score += 1
    return score


def _analyze_device_packets(device_key: str, packets: List[TracePacket]) -> Dict[str, Any]:
    sorted_packets = sorted(packets, key=lambda packet: (packet.epoch, packet.frame_number))
    transfers = Counter()
    requests = Counter()
    interface_classes = Counter()
    descriptor_names: List[str] = []
    statuses = Counter()

    vendor_request_count = 0
    error_count = 0
    interrupt_packets = 0
    interrupt_out_packets = 0
    enumeration_steps: List[str] = []

    for packet in sorted_packets:
        transfer = (packet.transfer_type or "unknown").strip() or "unknown"
        transfers[transfer] += 1

        request_name = _request_name(packet)
        if request_name:
            requests[request_name] += 1
            if request_name not in enumeration_steps and request_name in {"GET_DESCRIPTOR", "SET_ADDRESS", "SET_CONFIGURATION", "GET_CONFIGURATION"}:
                enumeration_steps.append(request_name)

        descriptor_name = _descriptor_name(packet)
        if descriptor_name and descriptor_name not in descriptor_names:
            descriptor_names.append(descriptor_name)

        interface_name = _interface_name(packet)
        if interface_name != "Unknown":
            interface_classes[interface_name] += 1

        request_type = _to_int(packet.request_type)
        if request_type & 0x60 == 0x40:
            vendor_request_count += 1

        status_text = (packet.status or "").lower()
        if status_text:
            statuses[status_text] += 1
            if any(token in status_text for token in ("error", "stall", "fail", "timeout")):
                error_count += 1

        transfer_lower = transfer.lower()
        if "interrupt" in transfer_lower:
            interrupt_packets += 1
            endpoint_int = _to_int(packet.endpoint)
            if endpoint_int and not (endpoint_int & 0x80):
                interrupt_out_packets += 1

    enumeration_detected = bool(requests["GET_DESCRIPTOR"] or requests["SET_ADDRESS"] or requests["SET_CONFIGURATION"] or descriptor_names)
    enumeration_cycles = min(requests["SET_CONFIGURATION"], requests["SET_ADDRESS"]) or requests["SET_CONFIGURATION"] or requests["SET_ADDRESS"]
    packet_count = len(sorted_packets)
    error_rate = (error_count / packet_count) if packet_count else 0.0

    suspicious_patterns: List[str] = []
    suspicious_score = 0
    interface_names = sorted(interface_classes)
    has_hid = "Human Interface Device" in interface_names
    has_storage = "Mass Storage" in interface_names
    keyboard_like = has_hid and any(_to_int(packet.interface_protocol) == 0x01 for packet in sorted_packets)

    if has_hid and has_storage:
        suspicious_patterns.append("Composite HID and mass-storage behavior can indicate BadUSB-style device emulation")
        suspicious_score += 35

    if keyboard_like and interrupt_packets >= 15:
        suspicious_patterns.append("Keyboard-like HID traffic appeared with a sustained interrupt pattern after connection")
        suspicious_score += 25

    if interrupt_out_packets >= 10:
        suspicious_patterns.append("Frequent outbound interrupt traffic suggests scripted HID injection or active control traffic")
        suspicious_score += 15

    if vendor_request_count >= 8:
        suspicious_patterns.append("High volume of vendor-specific USB requests observed")
        suspicious_score += 20

    if enumeration_cycles >= 3:
        suspicious_patterns.append("Device appears to re-enumerate repeatedly")
        suspicious_score += 10

    if error_count >= 5 or error_rate >= 0.15:
        suspicious_patterns.append("Trace contains an elevated rate of failed or stalled USB transactions")
        suspicious_score += 10

    suspicious_score = min(100, suspicious_score)

    if suspicious_patterns:
        next_level_summary = f"USB connected + performed suspicious communication pattern: {suspicious_patterns[0]}"
    elif enumeration_detected:
        next_level_summary = (
            f"USB connected + completed observable enumeration handshake with {packet_count} traced USB packets"
        )
    else:
        next_level_summary = "USB trace loaded, but the enumeration handshake was not fully visible in the capture"

    representative = sorted_packets[0] if sorted_packets else None
    return {
        "device_key": device_key,
        "vendor_id": _normalize_hex(representative.vendor_id if representative else ""),
        "product_id": _normalize_hex(representative.product_id if representative else ""),
        "bus_id": representative.bus_id if representative else "",
        "device_address": representative.device_address if representative else "",
        "packet_count": packet_count,
        "first_seen": sorted_packets[0].timestamp if sorted_packets else "",
        "last_seen": sorted_packets[-1].timestamp if sorted_packets else "",
        "enumeration_detected": enumeration_detected,
        "enumeration_steps": enumeration_steps,
        "descriptor_sequence": descriptor_names,
        "interface_classes": interface_names,
        "transfer_breakdown": dict(transfers),
        "control_requests": dict(requests),
        "vendor_request_count": vendor_request_count,
        "error_count": error_count,
        "error_rate": round(error_rate, 3),
        "interrupt_packets": interrupt_packets,
        "interrupt_out_packets": interrupt_out_packets,
        "suspicious_patterns": suspicious_patterns,
        "suspicious_score": suspicious_score,
        "next_level_summary": next_level_summary,
    }


def analyze_usb_trace(packets: Iterable[TracePacket], device_hint: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    packet_list = list(packets)
    grouped_packets = _group_packets(packet_list)
    device_reports = [_analyze_device_packets(key, group) for key, group in grouped_packets.items()]
    device_reports.sort(key=lambda report: (-report.get("suspicious_score", 0), -report.get("packet_count", 0)))

    selected_device = None
    if device_reports:
        selected_device = max(device_reports, key=lambda report: (_device_hint_score(report, device_hint), report.get("suspicious_score", 0), report.get("packet_count", 0)))

    suspicious_devices = [report for report in device_reports if report.get("suspicious_patterns")]
    return {
        "packet_count": len(packet_list),
        "device_count": len(device_reports),
        "devices": device_reports,
        "selected_device": selected_device or {},
        "suspicious_patterns": selected_device.get("suspicious_patterns", []) if selected_device else [],
        "next_level_summary": selected_device.get("next_level_summary", "") if selected_device else "",
        "suspicious_device_count": len(suspicious_devices),
    }


def match_trace_report(device: Dict[str, Any], trace_result: Dict[str, Any]) -> Dict[str, Any]:
    reports = trace_result.get("devices", []) or []
    if not reports:
        return {}

    device_vid = _normalize_hex(str(device.get("vid") or ""))
    device_pid = _normalize_hex(str(device.get("pid") or ""))
    best_report = reports[0]
    best_score = -1
    for report in reports:
        score = 0
        if device_vid and device_vid == str(report.get("vendor_id") or ""):
            score += 5
        if device_pid and device_pid == str(report.get("product_id") or ""):
            score += 5
        if score > best_score:
            best_score = score
            best_report = report
    return best_report if best_score > 0 else (trace_result.get("selected_device") or {})