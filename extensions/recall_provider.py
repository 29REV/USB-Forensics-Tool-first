#!/usr/bin/env python3
"""
Windows 11 Recall Provider - Forensic Data Extraction

Retrieves and analyzes Windows 11 Recall database for forensic investigation.
Extracts OCR text, snapshots, and timeline data associated with USB activity.

No modifications to base tool required. Standalone extension module.
"""

import sqlite3
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import base64

logger = logging.getLogger(__name__)


class RecallProvider:
    """
    Windows 11 Recall database provider for forensic analysis.
    
    Recall stores snapshots and OCR text at:
    C:\\Users\\<username>\\AppData\\Local\\CoreAIPlatform.CoreAI\\UKP
    
    Primary database: ukg.db (Recall Knowledge Graph)
    Text database: ocr.db (OCR Index)
    """
    
    # Standard Windows 11 Recall database paths
    RECALL_PATHS = [
        "C:\\Users\\{user}\\AppData\\Local\\CoreAIPlatform.CoreAI\\UKP",
        "C:\\Users\\{user}\\AppData\\Local\\Microsoft\\Windows\\AppRepository"
    ]
    
    RECALL_DATABASES = {
        'ukg': 'ukg.db',           # Knowledge graph
        'ocr': 'ocr.db',           # OCR index
        'screenshot': 'screenshot.db'  # Screenshot index
    }
    
    def __init__(self):
        """Initialize Recall Provider."""
        self.recall_root = self._locate_recall_database()
        self.user = os.getenv('USERNAME', 'Unknown')
        logger.info(f"RecallProvider initialized for user: {self.user}")
        logger.info(f"Recall database path: {self.recall_root}")
    
    def _locate_recall_database(self) -> Optional[str]:
        """
        Locate Windows 11 Recall database.
        
        Returns:
            Path to Recall database directory or None if not found
        """
        username = os.getenv('USERNAME')
        
        for path_template in self.RECALL_PATHS:
            path = path_template.replace('{user}', username)
            
            if os.path.exists(path):
                logger.info(f"Found Recall database at: {path}")
                return path
        
        logger.warning("Windows 11 Recall database not found")
        return None
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming IPI message from bridge.
        
        Args:
            message: IPI message with action and data
            
        Returns:
            Response dictionary
        """
        action = message.get('action', 'unknown')
        data = message.get('data', {})
        
        try:
            if action == 'query_recall':
                return self.query_recall(
                    start_time=data.get('start_time'),
                    end_time=data.get('end_time'),
                    device_serial=data.get('device_serial')
                )
            
            elif action == 'get_snapshots':
                return self.get_snapshots(
                    start_time=data.get('start_time'),
                    end_time=data.get('end_time')
                )
            
            elif action == 'get_ocr_text':
                return self.get_ocr_text(
                    start_time=data.get('start_time'),
                    end_time=data.get('end_time')
                )
            
            elif action == 'timeline_analysis':
                return self.timeline_analysis(
                    start_time=data.get('start_time'),
                    end_time=data.get('end_time'),
                    device_serial=data.get('device_serial')
                )
            
            else:
                return self._error(f"Unknown action: {action}")
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._error(str(e))
    
    def _error(self, message: str) -> Dict[str, Any]:
        """Create error response."""
        return {
            'status': 'error',
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_connection(self, db_type: str = 'ukg') -> Optional[sqlite3.Connection]:
        """
        Get SQLite connection to Recall database.
        
        Args:
            db_type: Type of database ('ukg', 'ocr', 'screenshot')
            
        Returns:
            SQLite connection or None
        """
        if not self.recall_root:
            logger.error("Recall database not found")
            return None
        
        db_filename = self.RECALL_DATABASES.get(db_type)
        if not db_filename:
            logger.error(f"Unknown database type: {db_type}")
            return None
        
        db_path = os.path.join(self.recall_root, db_filename)
        
        if not os.path.exists(db_path):
            logger.warning(f"Database not found: {db_path}")
            return None
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
        
        except Exception as e:
            logger.error(f"Cannot connect to database {db_path}: {e}")
            return None
    
    def query_recall(self, start_time: str, end_time: str, device_serial: str = None) -> Dict[str, Any]:
        """
        Main query function for Recall data extraction.
        
        Args:
            start_time: ISO format or 'YYYY-MM-DD HH:MM:SS'
            end_time: ISO format or 'YYYY-MM-DD HH:MM:SS'
            device_serial: Optional device filter
            
        Returns:
            Comprehensive recall data
        """
        try:
            # Convert timestamps
            start_ts = self._parse_timestamp(start_time)
            end_ts = self._parse_timestamp(end_time)
            
            if not start_ts or not end_ts:
                return self._error("Invalid timestamp format")
            
            results = {
                'status': 'success',
                'query_time': datetime.now().isoformat(),
                'time_range': {
                    'start': start_time,
                    'end': end_time,
                    'start_timestamp': start_ts,
                    'end_timestamp': end_ts
                },
                'device_serial': device_serial,
                'snapshots': [],
                'ocr_text': [],
                'timeline': [],
                'summary': {}
            }
            
            # Get snapshots for time range
            snapshots = self.get_snapshots(start_time, end_time)
            if snapshots.get('status') == 'success':
                results['snapshots'] = snapshots.get('snapshots', [])
            
            # Get OCR text for time range
            ocr = self.get_ocr_text(start_time, end_time)
            if ocr.get('status') == 'success':
                results['ocr_text'] = ocr.get('text_entries', [])
            
            # Get timeline for time range
            timeline = self.timeline_analysis(start_time, end_time, device_serial)
            if timeline.get('status') == 'success':
                results['timeline'] = timeline.get('events', [])
            
            # Summary statistics
            results['summary'] = {
                'total_snapshots': len(results['snapshots']),
                'ocr_entries': len(results['ocr_text']),
                'timeline_events': len(results['timeline']),
                'device_references': self._count_device_references(results, device_serial)
            }
            
            return results
        
        except Exception as e:
            logger.error(f"Error querying recall: {e}")
            return self._error(str(e))
    
    def get_snapshots(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Retrieve Recall snapshots for time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of snapshots with metadata
        """
        try:
            conn = self._get_connection('ukg')
            if not conn:
                return self._error("Cannot connect to Recall database")
            
            cursor = conn.cursor()
            start_ts = self._parse_timestamp(start_time)
            end_ts = self._parse_timestamp(end_time)
            
            # Query knowledge graph for snapshots
            # This is a typical structure - actual schema may vary
            query = """
                SELECT 
                    id, 
                    created_at, 
                    updated_at, 
                    screenshot_hash,
                    window_title,
                    focused_window,
                    active_app,
                    metadata
                FROM snapshots 
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
            """
            
            cursor.execute(query, (start_ts, end_ts))
            rows = cursor.fetchall()
            
            snapshots = []
            for row in rows:
                snapshot = {
                    'id': row['id'] if row['id'] else '',
                    'timestamp': row['created_at'] if row['created_at'] else '',
                    'screenshot_hash': row['screenshot_hash'] if row['screenshot_hash'] else '',
                    'window_title': row['window_title'] if row['window_title'] else '',
                    'focused_window': row['focused_window'] if row['focused_window'] else '',
                    'active_app': row['active_app'] if row['active_app'] else '',
                    'forensic_note': f"Snapshot captured at {row['created_at'] if row['created_at'] else 'unknown'}"
                }
                snapshots.append(snapshot)
            
            conn.close()
            
            return {
                'status': 'success' if snapshots else 'no_data',
                'snapshots': snapshots,
                'count': len(snapshots),
                'time_range': {'start': start_time, 'end': end_time}
            }
        
        except sqlite3.OperationalError as e:
            logger.warning(f"Table structure may differ: {e}")
            # Fallback to generic query
            return self._fallback_snapshot_query(start_time, end_time)
        
        except Exception as e:
            logger.error(f"Error getting snapshots: {e}")
            return self._error(str(e))
    
    def _fallback_snapshot_query(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Fallback method for snapshot query if table structure differs.
        """
        try:
            conn = self._get_connection('ukg')
            if not conn:
                return {'status': 'error', 'snapshots': []}
            
            cursor = conn.cursor()
            
            # Get all tables to understand schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            logger.info(f"Available tables in Recall DB: {tables}")
            
            # Look for snapshot-related tables
            snapshot_tables = [t for t in tables if 'snap' in t.lower()]
            
            if not snapshot_tables:
                conn.close()
                return {
                    'status': 'no_data',
                    'snapshots': [],
                    'note': 'No snapshot tables found in Recall database'
                }
            
            # Try first snapshot table found
            snapshots = []
            for table in snapshot_tables[:1]:
                try:
                    query = f"SELECT * FROM [{table}] LIMIT 100"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        snapshots.append({
                            'id': str(row[0]) if len(row) > 0 else '',
                            'timestamp': str(row[1]) if len(row) > 1 else '',
                            'table': table,
                            'forensic_note': f"Extracted from {table}"
                        })
                except Exception as e:
                    logger.debug(f"Cannot query table {table}: {e}")
            
            conn.close()
            
            return {
                'status': 'success' if snapshots else 'no_data',
                'snapshots': snapshots,
                'count': len(snapshots),
                'note': 'Using fallback query method'
            }
        
        except Exception as e:
            logger.error(f"Fallback query failed: {e}")
            return {'status': 'error', 'snapshots': [], 'error': str(e)}
    
    def get_ocr_text(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Extract OCR text from Recall OCR database.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            OCR text entries with timestamps
        """
        try:
            conn = self._get_connection('ocr')
            if not conn:
                logger.warning("OCR database not available, returning empty")
                return {
                    'status': 'no_data',
                    'text_entries': [],
                    'note': 'OCR database not found in Recall'
                }
            
            cursor = conn.cursor()
            start_ts = self._parse_timestamp(start_time)
            end_ts = self._parse_timestamp(end_time)
            
            # Query OCR index
            query = """
                SELECT 
                    id,
                    created_at,
                    ocr_text,
                    confidence,
                    language,
                    source_snapshot
                FROM ocr_entries
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
            """
            
            try:
                cursor.execute(query, (start_ts, end_ts))
                rows = cursor.fetchall()
            except sqlite3.OperationalError:
                # Try alternative schema
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                logger.info(f"OCR tables available: {tables}")
                rows = []
            
            text_entries = []
            for row in rows:
                if row and len(row) > 2:
                    entry = {
                        'id': row[0] if len(row) > 0 else '',
                        'timestamp': row[1] if len(row) > 1 else '',
                        'text': row[2] if len(row) > 2 else '',
                        'confidence': float(row[3]) if len(row) > 3 else 0.0,
                        'language': row[4] if len(row) > 4 else 'unknown'
                    }
                    text_entries.append(entry)
            
            conn.close()
            
            return {
                'status': 'success' if text_entries else 'no_data',
                'text_entries': text_entries,
                'count': len(text_entries),
                'time_range': {'start': start_time, 'end': end_time}
            }
        
        except Exception as e:
            logger.error(f"Error getting OCR text: {e}")
            return {
                'status': 'partial',
                'text_entries': [],
                'note': f'Error accessing OCR: {str(e)}'
            }
    
    def timeline_analysis(self, start_time: str, end_time: str, device_serial: str = None) -> Dict[str, Any]:
        """
        Analyze timeline of events from Recall.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            device_serial: Optional device filter
            
        Returns:
            Timeline of events
        """
        try:
            events = []
            
            # Get snapshots as timeline events
            snapshots = self.get_snapshots(start_time, end_time)
            if snapshots.get('status') != 'error':
                for snap in snapshots.get('snapshots', []):
                    events.append({
                        'timestamp': snap.get('timestamp', ''),
                        'event_type': 'snapshot_captured',
                        'description': f"Screenshot captured - {snap.get('active_app', 'Unknown app')}",
                        'source': 'recall',
                        'details': snap
                    })
            
            # Get OCR text as timeline events
            ocr = self.get_ocr_text(start_time, end_time)
            if ocr.get('status') != 'error':
                for text_entry in ocr.get('text_entries', [])[:10]:  # Limit to recent 10
                    events.append({
                        'timestamp': text_entry.get('timestamp', ''),
                        'event_type': 'text_detected',
                        'description': f"OCR: {text_entry.get('text', '')[:50]}...",
                        'source': 'recall_ocr',
                        'confidence': text_entry.get('confidence', 0)
                    })
            
            # Sort by timestamp
            events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return {
                'status': 'success' if events else 'no_data',
                'events': events,
                'count': len(events),
                'device_filter': device_serial,
                'time_range': {'start': start_time, 'end': end_time}
            }
        
        except Exception as e:
            logger.error(f"Error in timeline analysis: {e}")
            return self._error(str(e))
    
    def _count_device_references(self, results: Dict[str, Any], device_serial: str = None) -> int:
        """Count references to a device in recall data."""
        if not device_serial:
            return 0
        
        count = 0
        # Search in snapshots
        for snap in results.get('snapshots', []):
            if device_serial.lower() in str(snap).lower():
                count += 1
        
        # Search in OCR text
        for text in results.get('ocr_text', []):
            if device_serial.lower() in str(text).lower():
                count += 1
        
        return count
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[int]:
        """
        Parse timestamp string to Unix timestamp.
        
        Supports:
        - ISO format: 2024-12-29T10:30:00
        - Standard format: 2024-12-29 10:30:00
        - Unix timestamp: 1704062400
        
        Returns:
            Unix timestamp or None
        """
        try:
            # Try Unix timestamp
            if timestamp_str.isdigit():
                return int(timestamp_str)
            
            # Try ISO format
            try:
                dt = datetime.fromisoformat(timestamp_str)
                return int(dt.timestamp())
            except:
                pass
            
            # Try standard format
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                return int(dt.timestamp())
            except:
                pass
            
            logger.error(f"Cannot parse timestamp: {timestamp_str}")
            return None
        
        except Exception as e:
            logger.error(f"Timestamp parsing error: {e}")
            return None


# ═══════════════════════════════════════════════════════════════════════════
# USAGE IN BASE TOOL
# ═══════════════════════════════════════════════════════════════════════════

def example_usage():
    """
    Example of how to use RecallProvider from base tool.
    
    Add to any module in your base tool:
    """
    
    from extensions.bridge import BaseToolExtensionInterface
    
    # Initialize once
    interface = BaseToolExtensionInterface()
    
    # Query Recall for USB session
    print("\n=== Querying Windows 11 Recall ===")
    result = interface.query_recall(
        start_time="2024-12-29 10:00:00",
        end_time="2024-12-29 18:00:00",
        device_serial="USB123456"
    )
    
    print(f"Status: {result.get('status')}")
    print(f"Total Snapshots: {result.get('summary', {}).get('total_snapshots', 0)}")
    print(f"OCR Entries: {result.get('summary', {}).get('ocr_entries', 0)}")
    print(f"Timeline Events: {result.get('summary', {}).get('timeline_events', 0)}")
    
    # Print recent snapshots
    for snapshot in result.get('snapshots', [])[:3]:
        print(f"  - {snapshot.get('timestamp')}: {snapshot.get('active_app')}")
    
    # Print OCR text
    print("\n=== Detected Text (OCR) ===")
    for text_entry in result.get('ocr_text', [])[:5]:
        print(f"  - {text_entry.get('text')}")


if __name__ == '__main__':
    print("Windows 11 Recall Provider - Forensic Extension")
    print("="*70)
    
    provider = RecallProvider()
    print(f"✓ RecallProvider initialized")
    print(f"✓ Database path: {provider.recall_root}")
    print(f"✓ Current user: {provider.user}")
    print("\nTo use in your base tool:")
    print("  from extensions.bridge import BaseToolExtensionInterface")
    print("  interface = BaseToolExtensionInterface()")
    print("  result = interface.query_recall(...)")
