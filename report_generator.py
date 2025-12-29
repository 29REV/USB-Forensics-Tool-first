"""Generate formatted reports from device summaries (CSV, JSON, XLSX, PDF).

This module provides utilities to export analysis results in multiple formats
with proper validation and error handling. Includes comprehensive export of
device details including storage info, folder structures, deleted files, and
online device information.

Exports:
    write_csv: Export as human-friendly CSV
    write_json: Export as JSON
    write_xlsx: Export as Excel spreadsheet
    write_pdf: Export as PDF document
    write_device_details_report: Export comprehensive device analysis
"""
from typing import List, Dict, Optional
import csv
import os
import traceback
import logging
import json

from analysis import detect_suspicious, enrich_summary

logger = logging.getLogger(__name__)

try:
    import openpyxl
    from openpyxl import Workbook
except Exception:
    openpyxl = None


def write_csv(summaries: List[Dict], path: str, include_metadata: bool = True, suspicious_override: Optional[Dict] = None) -> str:
    """Write device summaries to CSV file.
    
    Creates a human-friendly CSV report with:
    - Optional metadata header
    - Friendly column names
    - Suspicious device flags based on analysis rules
    
    Args:
        summaries: List of device summary dictionaries
        path: Output file path (creates parent dirs if needed)
        include_metadata: Whether to include header metadata
        suspicious_override: Pre-computed suspicious flags (optional)
        
    Returns:
        Path to created file
        
    Raises:
        RuntimeError: If file write fails
    """
    if not isinstance(summaries, list):
        raise ValueError("summaries must be a list")
    
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    # friendly headers - expanded with new device detail fields
    fieldnames = [
        ('Device Name', 'name'),
        ('Device ID', 'device_id'),
        ('Vendor ID (VID)', 'vid'),
        ('Product ID (PID)', 'pid'),
        ('Serial Number', 'serial'),
        ('Drive Letter', 'drive_letter'),
        ('First Seen (UTC)', 'first_seen'),
        ('Last Seen (UTC)', 'last_seen'),
        ('Total Connections', 'total_connections'),
        ('Storage Capacity (GB)', 'storage_capacity_gb'),
        ('Storage Used (GB)', 'storage_used_gb'),
        ('Storage Free (GB)', 'storage_free_gb'),
        ('Storage Usage %', 'storage_usage_pct'),
        ('Total Folders', 'total_folders'),
        ('Max Folder Depth', 'max_folder_depth'),
        ('Deleted Files Found', 'deleted_files_found'),
        ('Deleted Files Recoverable', 'deleted_files_recoverable'),
        ('Manufacturer', 'manufacturer'),
        ('Product (Online)', 'online_product_name'),
        ('Market Status', 'market_status'),
        ('Product Rating', 'product_rating'),
        ('Anomaly Score', 'anomaly_score'),
        ('Suspicious', 'suspicious'),
    ]

    # compute suspicious flags if not passed in
    suspicious_map = {}
    if suspicious_override:
        suspicious_map = suspicious_override
    else:
        findings = detect_suspicious(summaries)
        for s, reason in findings:
            key = s.get('device_id') or s.get('name')
            suspicious_map[key] = reason

    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if include_metadata:
                writer.writerow([f"USB Forensics Report"])
                writer.writerow([f"Generated: {os.path.basename(path)}"]) 
                writer.writerow([""])  # blank line

            # write header row
            writer.writerow([h for h, _ in fieldnames])

            for s in summaries:
                key = s.get('device_id') or s.get('name')
                suspicious = suspicious_map.get(key, '')
                
                # Extract storage analysis
                storage_analysis = s.get('storage_analysis', {})
                folder_analysis = s.get('folder_analysis', {})
                deleted_analysis = s.get('deleted_files_analysis', {})
                reputation_analysis = s.get('reputation_analysis', {})
                
                row = [
                    s.get('name', ''),
                    s.get('device_id', ''),
                    s.get('vid', ''),
                    s.get('pid', ''),
                    s.get('serial', ''),
                    s.get('drive_letter', ''),
                    s.get('first_seen', ''),
                    s.get('last_seen', ''),
                    s.get('total_connections', ''),
                    storage_analysis.get('total_capacity_gb', ''),
                    storage_analysis.get('used_capacity_gb', ''),
                    storage_analysis.get('free_capacity_gb', ''),
                    storage_analysis.get('usage_percentage', ''),
                    folder_analysis.get('total_folders', ''),
                    folder_analysis.get('max_depth', ''),
                    deleted_analysis.get('deleted_count', ''),
                    deleted_analysis.get('recoverable_count', ''),
                    reputation_analysis.get('manufacturer', ''),
                    reputation_analysis.get('product_name', ''),
                    reputation_analysis.get('market_status', ''),
                    reputation_analysis.get('average_rating', ''),
                    s.get('anomaly_score', ''),
                    suspicious,
                ]
                writer.writerow(row)
        
        logger.info(f"Wrote CSV report to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to write CSV: {e}", exc_info=True)
        raise RuntimeError(f"Failed to write CSV: {e}")


def write_pdf(summaries: List[Dict], path: str) -> str:
    """Write device summaries to PDF file.
    
    Creates a simple PDF report listing all devices with key information.
    
    Args:
        summaries: List of device summary dictionaries
        path: Output file path
        
    Returns:
        Path to created file
        
    Raises:
        RuntimeError: If reportlab is not installed or write fails
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        logger.error("reportlab not installed - cannot generate PDF")
        raise RuntimeError('reportlab not installed. Install with: pip install reportlab')

    if not isinstance(summaries, list):
        raise ValueError("summaries must be a list")

    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    
    try:
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter
        y = height - 40
        c.setFont('Helvetica-Bold', 12)
        c.drawString(40, y, 'USB Forensics Report')
        y -= 30
        c.setFont('Helvetica', 9)
        
        for s in summaries:
            line = f"{s.get('name') or s.get('device_id')} | VID:{s.get('vid')} PID:{s.get('pid')} Serial:{s.get('serial')} First:{s.get('first_seen')} Last:{s.get('last_seen')} Count:{s.get('total_connections')}"
            c.drawString(40, y, line[:120])
            y -= 14
            if y < 60:
                c.showPage()
                y = height - 40
        
        c.save()
        logger.info(f"Wrote PDF report to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to write PDF: {e}", exc_info=True)
        raise RuntimeError(f"Failed to write PDF: {e}")


def write_json(summaries: List[Dict], path: str) -> str:
    """Write device summaries to JSON file.
    
    Args:
        summaries: List of device summary dictionaries
        path: Output file path
        
    Returns:
        Path to created file
        
    Raises:
        RuntimeError: If write fails
    """
    if not isinstance(summaries, list):
        raise ValueError("summaries must be a list")
    
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, default=str, indent=2)
        logger.info(f"Wrote JSON report to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to write JSON: {e}", exc_info=True)
        raise RuntimeError(f"Failed to write JSON: {e}")


def write_xlsx(summaries: List[Dict], path: str) -> str:
    """Write device summaries to Excel spreadsheet.
    
    Args:
        summaries: List of device summary dictionaries
        path: Output file path
        
    Returns:
        Path to created file
        
    Raises:
        RuntimeError: If openpyxl not installed or write fails
    """
    if openpyxl is None:
        logger.error("openpyxl not installed - cannot generate XLSX")
        raise RuntimeError('openpyxl not installed. Install with: pip install openpyxl')
    
    if not isinstance(summaries, list):
        raise ValueError("summaries must be a list")
    
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    
    try:
        wb = Workbook()
        ws = wb.active
        ws.title = "USB Devices"
        
        # headers
        headers = ['Device Name', 'Device ID', 'Vendor ID (VID)', 'Product ID (PID)', 'Serial Number', 'Drive Letter', 'First Seen (UTC)', 'Last Seen (UTC)', 'Total Connections', 'Suspicious']
        ws.append(headers)
        
        # compute suspicious flags
        suspicious_map = {}
        findings = detect_suspicious(summaries)
        for s, reason in findings:
            key = s.get('device_id') or s.get('name')
            suspicious_map[key] = reason
        
        # add data rows
        for s in summaries:
            key = s.get('device_id') or s.get('name')
            row = [
                s.get('name', ''),
                s.get('device_id', ''),
                s.get('vid', ''),
                s.get('pid', ''),
                s.get('serial', ''),
                s.get('drive_letter', ''),
                s.get('first_seen', ''),
                s.get('last_seen', ''),
                s.get('total_connections', ''),
                suspicious_map.get(key, ''),
            ]
            ws.append(row)
        
        wb.save(path)
        logger.info(f"Wrote XLSX report to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to write XLSX: {e}", exc_info=True)
        raise RuntimeError(f"Failed to write XLSX: {e}")


def write_device_details_report(summaries: List[Dict], path: str) -> str:
    """Write comprehensive device analysis report to JSON.

    Generates a detailed report including:
    - Storage analysis (capacity, usage, fragmentation)
    - Folder structure analysis (depths, sizes, changes)
    - Deleted files analysis (recovery info)
    - Device reputation (online information)
    - Anomaly scoring and suspicious flags

    Args:
        summaries: List of device summary dictionaries
        path: Output file path for JSON report

    Returns:
        Path to created file

    Raises:
        RuntimeError: If write fails
    """
    if not isinstance(summaries, list):
        raise ValueError("summaries must be a list")

    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)

    try:
        # Enrich all summaries with detailed analysis
        enriched = []
        for s in summaries:
            enriched.append(enrich_summary(s))

        # Write comprehensive report
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(enriched, f, default=str, indent=2)

        logger.info(f"Wrote device details report to {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to write device details report: {e}", exc_info=True)
        raise RuntimeError(f"Failed to write device details report: {e}")


if __name__ == '__main__':
    print('report generator loaded')
