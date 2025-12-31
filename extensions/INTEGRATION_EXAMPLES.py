#!/usr/bin/env python3
"""
Simple Integration Example - How to Use Extensions in Your Base Tool

This example shows the simplest way to add extension functionality
to your existing USB Forensics Tool without any modifications.

Copy any of these examples into your base tool modules and they'll work immediately!
"""

# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: Simple Recall Query (5 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_1_query_recall():
    """Simplest possible Recall query."""
    from extensions.bridge import BaseToolExtensionInterface
    
    ext = BaseToolExtensionInterface()
    result = ext.query_recall("2024-12-29 10:00:00", "2024-12-29 18:00:00")
    print(f"Found {result.get('summary', {}).get('total_snapshots', 0)} snapshots")


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: BadUSB Risk Check (5 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_2_check_firmware():
    """Quick BadUSB risk assessment."""
    from extensions.bridge import BaseToolExtensionInterface
    
    ext = BaseToolExtensionInterface()
    risk = ext.get_badusb_risk_score("0x1234", "0x5678")
    print(f"Risk Score: {risk:.2f} {'⚠️ DANGEROUS' if risk > 0.7 else '✓ Safe'}")


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: Generate Report (5 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_3_generate_report():
    """Generate narrative from logs."""
    from extensions.bridge import BaseToolExtensionInterface
    
    logs = ["Device connected", "Files copied", "Device ejected"]
    ext = BaseToolExtensionInterface()
    report = ext.generate_narrative_report(logs)
    print(report)


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: Add to Analysis Pipeline (10 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_4_analysis_pipeline(device, start_time, end_time):
    """Enhance device analysis with extensions."""
    from extensions.bridge import BaseToolExtensionInterface
    
    ext = BaseToolExtensionInterface()
    
    # Get firmware risk
    firmware_risk = ext.validate_firmware(device.vendor_id, device.product_id)
    
    # Get Recall activity
    recall_data = ext.query_recall(start_time, end_time, device.serial_number)
    
    # Combined analysis
    return {
        'device': device.name,
        'firmware_risk': firmware_risk.get('risk_score', 0),
        'activity_snapshots': recall_data.get('summary', {}).get('total_snapshots', 0),
        'is_suspicious': firmware_risk.get('risk_score', 0) > 0.5
    }


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: GUI Integration (15 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_5_gui_integration():
    """Add extension tab to GUI."""
    import tkinter as tk
    from tkinter import ttk
    from extensions.bridge import BaseToolExtensionInterface
    
    root = tk.Tk()
    root.title("Extensions Demo")
    
    ext = BaseToolExtensionInterface()
    
    def query_button():
        result = ext.query_recall("2024-12-29 10:00:00", "2024-12-29 18:00:00")
        output.delete(1.0, tk.END)
        output.insert(tk.END, f"Snapshots: {result.get('summary', {}).get('total_snapshots', 0)}")
    
    ttk.Button(root, text="Query Recall", command=query_button).pack(pady=10)
    output = tk.Text(root, height=10, width=50)
    output.pack(padx=10, pady=10)
    
    root.mainloop()


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 6: Incident Response (20 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_6_incident_response(device):
    """Automated incident response using extensions."""
    from extensions.bridge import BaseToolExtensionInterface
    from datetime import datetime, timedelta
    
    ext = BaseToolExtensionInterface()
    
    print(f"Investigating device: {device.name}")
    
    # Check firmware
    firmware = ext.validate_firmware(device.vendor_id, device.product_id)
    print(f"  Firmware Risk: {firmware['risk_level']}")
    
    if firmware['risk_score'] > 0.7:
        print("  ⚠️  CRITICAL - Isolating device immediately")
        return
    
    # Check activity
    end = datetime.now()
    start = end - timedelta(hours=24)
    
    recall = ext.query_recall(start.isoformat(), end.isoformat())
    print(f"  Activity: {recall['summary']['total_snapshots']} snapshots recorded")
    
    # Generate report
    report = ext.generate_narrative_report(device.logs if hasattr(device, 'logs') else [])
    print(f"  Report generated ({len(report)} characters)")


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 7: Automated Investigation (25 lines)
# ═════════════════════════════════════════════════════════════════════════════

class ForensicInvestigator:
    """Automated forensic investigation using extensions."""
    
    def __init__(self):
        from extensions.bridge import BaseToolExtensionInterface
        self.ext = BaseToolExtensionInterface()
    
    def investigate(self, device, start_time, end_time):
        """Full automated investigation."""
        
        results = {
            'device_name': device.name,
            'investigation_period': f"{start_time} to {end_time}",
            'findings': []
        }
        
        # Check 1: Firmware
        firmware = self.ext.validate_firmware(device.vendor_id, device.product_id)
        results['firmware_risk'] = firmware['risk_score']
        if firmware['risk_score'] > 0.5:
            results['findings'].append(f"⚠️  BadUSB Risk: {firmware['risk_level']}")
        
        # Check 2: Activity
        recall = self.ext.query_recall(start_time, end_time)
        results['activity'] = recall.get('summary', {})
        if recall['summary']['total_snapshots'] > 50:
            results['findings'].append(f"⚠️  High activity: {recall['summary']['total_snapshots']} snapshots")
        
        # Check 3: OCR text for keywords
        for text_entry in recall.get('ocr_text', []):
            if any(kw in text_entry.get('text', '').lower() for kw in ['password', 'secret', 'admin']):
                results['findings'].append(f"⚠️  Sensitive data detected: {text_entry['text'][:50]}")
        
        # Generate report
        results['report'] = self.ext.generate_narrative_report(
            [f['description'] for f in results['findings']]
        )
        
        return results


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 8: Batch Device Analysis (20 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_8_batch_analysis(devices):
    """Analyze multiple devices with extensions."""
    from extensions.bridge import BaseToolExtensionInterface
    
    ext = BaseToolExtensionInterface()
    results = []
    
    for device in devices:
        print(f"Analyzing {device.name}...")
        
        # Quick risk assessment
        risk = ext.get_badusb_risk_score(device.vendor_id, device.product_id)
        
        # Quick activity check
        recall = ext.query_recall("2024-12-29 00:00:00", "2024-12-29 23:59:59")
        
        results.append({
            'device': device.name,
            'risk_score': risk,
            'snapshots': recall.get('summary', {}).get('total_snapshots', 0),
            'suspicious': risk > 0.5
        })
    
    # Summary report
    print(f"\n=== ANALYSIS SUMMARY ===")
    suspicious = [r for r in results if r['suspicious']]
    print(f"Devices analyzed: {len(results)}")
    print(f"Suspicious devices: {len(suspicious)}")
    
    return results


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 9: Real-time Monitoring (15 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_9_monitor_devices(devices_to_monitor):
    """Real-time monitoring with extensions."""
    from extensions.bridge import BaseToolExtensionInterface
    from datetime import datetime, timedelta
    import time
    
    ext = BaseToolExtensionInterface()
    alerts = []
    
    for device in devices_to_monitor:
        # Check recent activity
        end = datetime.now()
        start = end - timedelta(minutes=5)
        
        recall = ext.query_recall(start.isoformat(), end.isoformat())
        activity = recall.get('summary', {}).get('total_snapshots', 0)
        
        if activity > 20:  # Threshold
            alert = f"⚠️  High activity on {device.name}: {activity} snapshots in 5 min"
            alerts.append(alert)
            print(alert)
    
    return alerts


# ═════════════════════════════════════════════════════════════════════════════
# EXAMPLE 10: Export Professional Report (20 lines)
# ═════════════════════════════════════════════════════════════════════════════

def example_10_export_report(analysis_data):
    """Export professional forensic report."""
    from extensions.bridge import BaseToolExtensionInterface
    import json
    
    ext = BaseToolExtensionInterface()
    
    # Generate narratives
    narrative = ext.generate_narrative_report(
        analysis_data.get('logs', []),
        analysis_data
    )
    
    summary = ext.generate_executive_summary(analysis_data)
    
    # Create professional report
    report = {
        'investigation_date': analysis_data.get('timestamp'),
        'executive_summary': summary,
        'detailed_narrative': narrative,
        'raw_analysis': analysis_data,
        'exported_by': 'USB Forensics Tool v3.0 Professional'
    }
    
    # Save to file
    with open('forensic_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("✓ Report saved to forensic_report.json")
    return report


# ═════════════════════════════════════════════════════════════════════════════
# Quick Reference
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  USB Forensics Tool - Extension Integration Examples                ║
    ║                                                                       ║
    ║  Copy any example into your code to use extensions!                  ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    
    10 EXAMPLES PROVIDED:
    
    1. example_1_query_recall()              - 5 lines
       Simple Recall database query
    
    2. example_2_check_firmware()            - 5 lines
       Quick BadUSB risk assessment
    
    3. example_3_generate_report()           - 5 lines
       Generate narrative from logs
    
    4. example_4_analysis_pipeline()         - 10 lines
       Enhance device analysis
    
    5. example_5_gui_integration()           - 15 lines
       Add extension UI to GUI
    
    6. example_6_incident_response()         - 20 lines
       Automated incident handling
    
    7. ForensicInvestigator                  - 25 lines
       Full investigation framework
    
    8. example_8_batch_analysis()            - 20 lines
       Analyze multiple devices
    
    9. example_9_monitor_devices()           - 15 lines
       Real-time monitoring
    
    10. example_10_export_report()           - 20 lines
        Professional report export
    
    QUICK START (3 lines):
    
    >>> from extensions.bridge import BaseToolExtensionInterface
    >>> ext = BaseToolExtensionInterface()
    >>> result = ext.query_recall("2024-12-29 10:00:00", "2024-12-29 18:00:00")
    
    That's it! No modifications to base tool needed.
    """)
