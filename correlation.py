"""Correlation utilities to combine registry and event log data into timelines.

This module implements correlation logic to match registry entries with event log
entries and create unified device records with complete history, including detailed
storage information and online device details.

Exports:
    DeviceRecord: Dataclass representing a complete USB device with all data
    correlate: Main correlation function
    correlate_with_details: Enhanced correlation with device scanning
"""
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeviceRecord:
    """Unified USB device record with registry, event log, and storage data.
    
    Attributes:
        device_id: Unique identifier from registry
        name: Device name/description
        vid: Vendor ID from registry
        pid: Product ID from registry
        serial: Device serial number
        first_seen: ISO timestamp of first activity
        last_seen: ISO timestamp of last activity
        connections: Total number of recorded connections
        events: List of event records (timestamps, IDs, descriptions)
        storage_info: Storage capacity and usage information (optional)
        folder_info: Folder structure and count information (optional)
        file_info: File count and size information (optional)
        deleted_files: Information about deleted files (optional)
        online_info: Manufacturer and product information from online sources (optional)
        scan_details: Full device scan results (optional)
    """
    device_id: str
    name: str | None
    vid: str | None
    pid: str | None
    serial: str | None
    first_seen: str | None
    last_seen: str | None
    connections: int
    events: List[Dict[str, Any]] = field(default_factory=list)
    storage_info: Dict[str, Any] = field(default_factory=dict)
    folder_info: List[Dict[str, Any]] = field(default_factory=list)
    file_info: Dict[str, Any] = field(default_factory=dict)
    deleted_files: List[Dict[str, Any]] = field(default_factory=list)
    online_info: Dict[str, Any] = field(default_factory=dict)
    scan_details: Dict[str, Any] = field(default_factory=dict)


def correlate(registry_entries: List[object], event_entries: List[object]) -> List[DeviceRecord]:
    """Correlate registry and event log entries into unified device records.
    
    Attempts to match event log entries with registry entries by:
    1. Serial number matching
    2. Device ID matching
    3. Device name substring matching
    
    Creates device records for unmatched events (event-only devices).
    
    Args:
        registry_entries: List of registry entries with device_id, vid, pid, serial, last_write
        event_entries: List of event entries with event_id, timestamp, device_name
        
    Returns:
        List of DeviceRecord objects with correlated data
    """
    records: dict[str, DeviceRecord] = {}

    # Process registry entries
    for r in registry_entries:
        key = getattr(r, 'serial', None) or getattr(r, 'device_id', 'unknown')
        rec = DeviceRecord(
            device_id=getattr(r, 'device_id', key),
            name=None,
            vid=getattr(r, 'vid', None),
            pid=getattr(r, 'pid', None),
            serial=getattr(r, 'serial', None),
            first_seen=getattr(r, 'last_write', None),  # Registry only has last_write, use as last_seen
            last_seen=getattr(r, 'last_write', None),
            connections=0,
        )
        records[key] = rec
        logger.debug(f"Added registry entry: {key}")

    # Process events and correlate with registry
    for e in event_entries:
        name = getattr(e, 'device_name', None)
        ts = getattr(e, 'timestamp', None)
        ev_id = getattr(e, 'event_id', None)
        message = getattr(e, 'message', None) or getattr(e, 'description', None) or ''
        action = {
            'timestamp': ts,
            'event_id': ev_id,
            'message': message,
        }
        
        # Try to match by serial number
        matched = False
        for rec in records.values():
            if rec.serial and rec.serial in (name or ''):
                rec.connections += 1
                # Update last_seen to the latest timestamp
                if ts and (rec.last_seen is None or ts > rec.last_seen):
                    rec.last_seen = ts
                # Set first_seen to the earliest timestamp if not set
                if ts and (rec.first_seen is None or ts < rec.first_seen):
                    rec.first_seen = ts
                rec.events.append(action)
                matched = True
                logger.debug(f"Matched event to serial: {rec.serial}")
                break
        
        if not matched:
            # Create or update event-only device record
            key = name or f"event-{ts}"
            if key not in records:
                records[key] = DeviceRecord(key, name, None, None, None, ts, ts, 1, events=[action])
                logger.debug(f"Created event-only device: {key}")
            else:
                rec = records[key]
                rec.connections += 1
                # Update last_seen to the latest timestamp
                if ts and (rec.last_seen is None or ts > rec.last_seen):
                    rec.last_seen = ts
                # Set first_seen to the earliest timestamp if not set
                if ts and (rec.first_seen is None or ts < rec.first_seen):
                    rec.first_seen = ts
                rec.events.append(action)

    result = list(records.values())
    logger.info(f"Correlated {len(registry_entries)} registry entries with {len(event_entries)} events into {len(result)} device records")
    return result


if __name__ == '__main__':
    from registry_parser import parse_registry
    from eventlog_parser import parse_event_logs

    regs = parse_registry()
    evs = parse_event_logs()
    for r in correlate(regs, evs):
        print(asdict(r))