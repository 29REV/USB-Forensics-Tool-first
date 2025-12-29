"""Analyze correlated device records for counts and suspicious patterns.

This module provides utilities for summarizing device data, detecting anomalies,
and enriching device records with detailed storage and online information.

Exports:
    summarize: Convert device objects to summary dicts
    enrich_summary: Add detailed device information  
    detect_suspicious: Flag suspicious devices based on heuristics
    anomaly_score: Compute numeric anomaly scores (0-100)
    analyze_storage_patterns: Analyze storage usage and capacity
    analyze_folder_structure: Analyze folder hierarchy and sizes
    analyze_deleted_files: Analyze deleted file traces and recovery
    analyze_device_reputation: Analyze online device information
"""
from dataclasses import asdict
from typing import List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def summarize(devices: List[object]) -> List[dict]:
    """Produce a summary list of dicts with key fields for reporting.
    
    Converts device objects into dictionary format suitable for display
    and export in reports.
    
    Args:
        devices: List of DeviceRecord objects or similar
        
    Returns:
        List of dictionaries containing key device information
    """
    out = []
    for d in devices:
        rec = {
            'device_id': getattr(d, 'device_id', None),
            'name': getattr(d, 'name', None),
            'vid': getattr(d, 'vid', None),
            'pid': getattr(d, 'pid', None),
            'serial': getattr(d, 'serial', None),
            'first_seen': getattr(d, 'first_seen', None),
            'last_seen': getattr(d, 'last_seen', None),
            'total_connections': getattr(d, 'connections', 0),
            'events': getattr(d, 'events', []),
        }
        out.append(rec)
    logger.debug(f"Summarized {len(out)} device records")
    return out


def detect_suspicious(summaries: List[dict]) -> List[Tuple[dict, str]]:
    """Flag suspicious items based on heuristic rules.
    
    Detection rules:
    - Device with missing serial but multiple connections
    - Device with very frequent connections (>10)
    - Device with high anomaly score (>70)

    Args:
        summaries: List of device summary dictionaries
        
    Returns:
        List of tuples (device_summary, reason_string) for suspicious devices
    """
    findings = []
    for s in summaries:
        reasons = []
        connections = int(s.get('total_connections', 0) or 0)
        serial = s.get('serial')
        
        if not serial and connections > 3:
            reasons.append('No serial number but multiple connections')
        if connections > 10:
            reasons.append('Unusually frequent connections (>10)')
        if s.get('anomaly_score', 0) > 70:
            reasons.append(f"High anomaly score ({s.get('anomaly_score')})")
        
        if reasons:
            findings.append((s, '; '.join(reasons)))
            logger.info(f"Suspicious device detected: {s.get('device_id')} - {'; '.join(reasons)}")
    
    return findings


def compute_anomaly_score(device: Dict[str, Any]) -> float:
    """Compute numeric anomaly score for a device record (0-100).

    Factors analyzed:
    - Number of registry entries (higher = more interaction)
    - Event log entries (higher = more activity)
    - Deleted files present (indicates previous data)
    - Storage usage patterns (full device = suspicious)
    - Missing serial number

    Args:
        device: Device dictionary or record

    Returns:
        Float score between 0 (normal) and 100 (highly anomalous)
    """
    score = 0.0
    
    # Missing serial is suspicious
    if not device.get('serial'):
        score += 25
    
    # Registry entries anomaly
    reg_entries = int(device.get('registry_entries', 0) or 0)
    if reg_entries > 100:
        score += min(25, (reg_entries - 100) / 10)
    
    # Event log entries anomaly
    event_entries = int(device.get('event_entries', 0) or 0)
    if event_entries > 50:
        score += min(20, (event_entries - 50) / 5)
    
    # Deleted files anomaly
    deleted_files = device.get('deleted_files', []) or []
    if deleted_files:
        score += min(20, len(deleted_files) * 2)
    
    # Storage usage anomaly
    storage_info = device.get('storage_info', {}) or {}
    if storage_info and isinstance(storage_info, dict):
        usage_pct = storage_info.get('percentage_used', 0)
        if usage_pct > 90:
            score += 15
        elif usage_pct > 75:
            score += 10
    
    # Connection frequency
    connections = int(device.get('connections', 0) or 0)
    if connections > 10:
        score += min(15, connections)
    
    return min(100.0, score)


def analyze_storage_patterns(device: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze storage usage patterns of a device.

    Examines:
    - Total capacity and usage
    - Percentage utilization
    - Fragmentation indicators
    - Unusual storage configurations

    Args:
        device: Device dictionary or record

    Returns:
        Dict with keys:
            - total_capacity_gb: Total storage in GB
            - used_capacity_gb: Used storage in GB
            - free_capacity_gb: Free storage in GB
            - usage_percentage: Percentage used
            - is_full: Boolean if >90% full
            - fragmentation_risk: Low/Medium/High based on usage
    """
    storage_info = device.get('storage_info', {}) or {}
    
    result = {
        "total_capacity_gb": 0.0,
        "used_capacity_gb": 0.0,
        "free_capacity_gb": 0.0,
        "usage_percentage": 0.0,
        "is_full": False,
        "fragmentation_risk": "Low"
    }
    
    if storage_info and isinstance(storage_info, dict):
        total = storage_info.get("total_size", 0)
        used = storage_info.get("used_size", 0)
        free = storage_info.get("free_size", 0)
        pct = storage_info.get("percentage_used", 0)
        
        result["total_capacity_gb"] = round(total / (1024**3), 2) if total > 0 else 0.0
        result["used_capacity_gb"] = round(used / (1024**3), 2) if used > 0 else 0.0
        result["free_capacity_gb"] = round(free / (1024**3), 2) if free > 0 else 0.0
        result["usage_percentage"] = pct
        result["is_full"] = pct > 90
        
        # Fragmentation risk based on usage
        if pct > 85:
            result["fragmentation_risk"] = "High"
        elif pct > 70:
            result["fragmentation_risk"] = "Medium"
        else:
            result["fragmentation_risk"] = "Low"
    
    return result


def analyze_folder_structure(device: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze folder structure and hierarchy of a device.

    Examines:
    - Total folder count
    - Maximum nesting depth
    - Largest folders by size
    - Folder count history

    Args:
        device: Device dictionary or record

    Returns:
        Dict with keys:
            - total_folders: Total number of folders
            - max_depth: Maximum folder nesting depth
            - largest_folders: List of (folder_path, size_mb) tuples
            - previous_folder_count: Historical folder count
            - folders_added: Estimated folders added since last scan
            - folders_deleted: Estimated folders deleted since last scan
    """
    folder_info = device.get('folder_info', []) or []
    folder_history = device.get('folder_history', {}) or {}
    
    result = {
        "total_folders": len(folder_info),
        "max_depth": 0,
        "largest_folders": [],
        "previous_folder_count": 0,
        "folders_added": 0,
        "folders_deleted": 0
    }
    
    if folder_info and isinstance(folder_info, list):
        # Find max depth
        max_depth = max(
            [f.get("depth", 0) for f in folder_info if isinstance(f, dict)],
            default=0
        )
        result["max_depth"] = max_depth
        
        # Get largest folders
        sorted_folders = sorted(
            [f for f in folder_info if isinstance(f, dict)],
            key=lambda f: f.get("total_size", 0),
            reverse=True
        )[:5]
        
        result["largest_folders"] = [
            (f.get("name", ""), round(f.get("total_size", 0) / (1024**2), 2))
            for f in sorted_folders
        ]
    
    # Folder history analysis
    if folder_history and isinstance(folder_history, dict):
        prev_count = folder_history.get("previous_count", 0)
        result["previous_folder_count"] = prev_count
        result["folders_added"] = max(0, result["total_folders"] - prev_count)
        result["folders_deleted"] = max(0, prev_count - result["total_folders"])
    
    return result


def analyze_deleted_files(device: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze deleted files and recovery traces on a device.

    Examines:
    - Total deleted files detected
    - Estimated total size of deleted files
    - Recovery probability per file
    - Deletion timeline

    Args:
        device: Device dictionary or record

    Returns:
        Dict with keys:
            - deleted_count: Number of deleted files detected
            - total_deleted_size_mb: Total size of deleted files
            - recoverable_count: Files likely recoverable
            - high_confidence_count: Deletions with high confidence
            - deletion_timeline: Estimated deletion timespan
    """
    deleted_files = device.get('deleted_files', []) or []
    
    result = {
        "deleted_count": len(deleted_files),
        "total_deleted_size_mb": 0.0,
        "recoverable_count": 0,
        "high_confidence_count": 0,
        "deletion_timeline": "Unknown"
    }
    
    if deleted_files and isinstance(deleted_files, list):
        total_size = 0
        recoverable = 0
        high_confidence = 0
        
        for deleted in deleted_files:
            if isinstance(deleted, dict):
                size = deleted.get("estimated_size", 0)
                total_size += size
                
                confidence = deleted.get("confidence", 0)
                if confidence > 70:
                    recoverable += 1
                if confidence > 85:
                    high_confidence += 1
        
        result["total_deleted_size_mb"] = round(total_size / (1024**2), 2)
        result["recoverable_count"] = recoverable
        result["high_confidence_count"] = high_confidence
        
        # Estimate deletion timeline
        if deleted_files:
            result["deletion_timeline"] = f"~{len(deleted_files)} files detected"
    
    return result


def analyze_device_reputation(device: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze online device reputation and information.

    Examines:
    - Manufacturer information
    - Product specifications
    - Security vulnerabilities
    - Market status and alternatives

    Args:
        device: Device dictionary or record

    Returns:
        Dict with keys:
            - manufacturer: Manufacturer name
            - product_name: Product name
            - product_category: Device category
            - market_status: Active/Legacy/Discontinued
            - average_rating: Product rating 0-5
            - known_vulnerabilities: Number of known issues
            - has_alternatives: Whether alternatives exist
    """
    online_info = device.get('online_info', {}) or {}
    
    result = {
        "manufacturer": "Unknown",
        "product_name": "Unknown",
        "product_category": "USB Device",
        "market_status": "Unknown",
        "average_rating": 0.0,
        "known_vulnerabilities": 0,
        "has_alternatives": False
    }
    
    if online_info and isinstance(online_info, dict):
        # Manufacturer info
        manufacturer = online_info.get("manufacturer", {})
        if isinstance(manufacturer, dict):
            result["manufacturer"] = manufacturer.get("name", "Unknown")
        
        # Product info
        product = online_info.get("product", {})
        if isinstance(product, dict):
            result["product_name"] = product.get("name", "Unknown")
        
        # Security info
        security = online_info.get("security_info", {})
        if isinstance(security, dict):
            result["known_vulnerabilities"] = len(security.get("vulnerabilities", []))
        
        # Market and rating info
        result["market_status"] = online_info.get("market_status", "Unknown")
        result["average_rating"] = online_info.get("average_rating", 0.0)
        result["has_alternatives"] = bool(online_info.get("alternatives", []))
    
    return result


def enrich_summary(device: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich a device summary with detailed analysis.

    Combines basic device info with storage, folder, deleted file,
    and reputation analysis.

    Args:
        device: Device dictionary or record

    Returns:
        Dict with comprehensive device analysis
    """
    logger.debug(f"Enriching summary for device {device.get('device_id')}")
    
    # Create enriched summary
    summary = dict(device) if isinstance(device, dict) else asdict(device)
    
    # Add detailed analyses
    summary["storage_analysis"] = analyze_storage_patterns(device)
    summary["folder_analysis"] = analyze_folder_structure(device)
    summary["deleted_files_analysis"] = analyze_deleted_files(device)
    summary["reputation_analysis"] = analyze_device_reputation(device)
    summary["anomaly_score"] = compute_anomaly_score(device)
    
    logger.debug(f"Enrichment complete - anomaly score: {summary['anomaly_score']}")
    
    return summary


def anomaly_score(summaries: List[dict]) -> List[tuple]:
    """Compute numeric anomaly score for each device (0-100).
    
    Scoring combines multiple heuristics for backward compatibility.
    Uses compute_anomaly_score for individual scoring.
    
    Args:
        summaries: List of device summary dictionaries
        
    Returns:
        List of tuples (device_summary, anomaly_score) where score is 0-100
    """
    out = []
    for s in summaries:
        score = compute_anomaly_score(s)
        out.append((s, score))
    
    logger.debug(f"Computed anomaly scores for {len(out)} devices")
    return out


if __name__ == '__main__':
    print('analysis module loaded')
