from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.usb_device_manager import get_all_usb_devices, get_device_summary
from core.analysis import enrich_summary, detect_suspicious
from utils.report_generator import write_csv, write_json, write_xlsx, write_pdf, write_device_details_report


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = PROJECT_ROOT / "report and paper" / "runtime_evidence" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    devices = get_all_usb_devices()
    basic_summaries = [get_device_summary(d) for d in devices]
    enriched = [enrich_summary(s) for s in basic_summaries]

    suspicious = detect_suspicious(enriched)
    suspicious_map = {
        (s.get("device_id") or s.get("name") or f"item_{idx}"): reason
        for idx, (s, reason) in enumerate(suspicious, 1)
    }

    csv_path = out_dir / f"forensics_report_{stamp}.csv"
    json_path = out_dir / f"forensics_report_{stamp}.json"
    xlsx_path = out_dir / f"forensics_report_{stamp}.xlsx"
    pdf_path = out_dir / f"forensics_report_{stamp}.pdf"
    detailed_path = out_dir / f"forensics_detailed_{stamp}.json"

    write_csv(enriched, str(csv_path), suspicious_override=suspicious_map)
    write_json(enriched, str(json_path))
    write_xlsx(enriched, str(xlsx_path))
    write_pdf(enriched, str(pdf_path))
    write_device_details_report(enriched, str(detailed_path))

    evidence = {
        "timestamp_utc": stamp,
        "device_count": len(enriched),
        "suspicious_count": len(suspicious),
        "devices": [
            {
                "name": d.get("name"),
                "manufacturer": d.get("manufacturer"),
                "device_type": d.get("device_type"),
                "vid": d.get("vid"),
                "pid": d.get("pid"),
                "serial": d.get("serial"),
                "anomaly_score": d.get("anomaly_score"),
            }
            for d in enriched
        ],
        "generated_files": {
            "csv": str(csv_path),
            "json": str(json_path),
            "xlsx": str(xlsx_path),
            "pdf": str(pdf_path),
            "detailed_json": str(detailed_path),
        },
    }

    evidence_path = out_dir / "runtime_summary.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    print(f"Runtime evidence directory: {out_dir}")
    print(f"Detected devices: {len(enriched)}")
    print(f"Suspicious devices: {len(suspicious)}")
    print(f"Summary: {evidence_path}")


if __name__ == "__main__":
    main()
