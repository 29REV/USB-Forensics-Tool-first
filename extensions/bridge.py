#!/usr/bin/env python3
"""
Inter-Process Interface (IPI) Bridge - Extension Communication Layer

This module provides a JSON-based bridge for communicating between the base USB Forensics Tool
and external extension modules without modifying the original source code.

Architecture:
  - Base Tool → JSON Message → Bridge → Extension Module
  - Extension Module → JSON Response → Bridge → Base Tool

No modifications to base tool required. Simple import and use.
"""

import json
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class IPIBridge:
    """Inter-Process Interface Bridge for extension communication."""
    
    def __init__(self, extensions_dir: str = None):
        """
        Initialize the IPI Bridge.
        
        Args:
            extensions_dir: Path to extensions directory (auto-detected if None)
        """
        if extensions_dir is None:
            # Auto-detect extensions directory
            self.extensions_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'extensions'
            )
        else:
            self.extensions_dir = extensions_dir
        
        self.extension_modules = {}
        self.message_queue = []
        
        logger.info(f"IPI Bridge initialized with extensions_dir: {self.extensions_dir}")
    
    def register_extension(self, module_name: str, module_path: str) -> bool:
        """
        Register an extension module.
        
        Args:
            module_name: Name of the extension (e.g., 'recall_provider')
            module_path: Path to the module file
            
        Returns:
            bool: True if registration successful
        """
        try:
            if not os.path.exists(module_path):
                logger.error(f"Extension module not found: {module_path}")
                return False
            
            self.extension_modules[module_name] = {
                'path': module_path,
                'registered_at': datetime.now().isoformat(),
                'status': 'ready'
            }
            
            logger.info(f"Extension registered: {module_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering extension {module_name}: {e}")
            return False
    
    def create_message(self, extension: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standard IPI message.
        
        Args:
            extension: Target extension name
            action: Action to perform
            data: Payload data
            
        Returns:
            Standard message dictionary
        """
        message = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'extension': extension,
            'action': action,
            'data': data,
            'message_id': f"{extension}_{action}_{int(datetime.now().timestamp() * 1000)}"
        }
        
        return message
    
    def send_to_extension(self, extension: str, action: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a message to an extension module.
        
        Args:
            extension: Target extension name
            action: Action to perform
            data: Payload data
            
        Returns:
            Response from extension or None if failed
        """
        try:
            message = self.create_message(extension, action, data)
            
            logger.info(f"IPI Bridge: Sending to {extension} - Action: {action}")
            logger.debug(f"IPI Bridge: Message payload: {json.dumps(message, indent=2)}")
            
            # Route to appropriate extension
            if extension == 'recall_provider':
                from extensions.recall_provider import RecallProvider
                provider = RecallProvider()
                response = provider.process_message(message)
                return response
            
            elif extension == 'firmware_validator':
                from extensions.firmware_validator import FirmwareValidator
                validator = FirmwareValidator()
                response = validator.process_message(message)
                return response
            
            elif extension == 'ai_reporter':
                from extensions.ai_reporter import AIReporter
                reporter = AIReporter()
                response = reporter.process_message(message)
                return response
            
            else:
                logger.error(f"Unknown extension: {extension}")
                return self._error_response(f"Unknown extension: {extension}")
            
        except Exception as e:
            logger.error(f"Error sending to extension {extension}: {e}")
            return self._error_response(str(e))
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create standard error response."""
        return {
            'status': 'error',
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
    
    def query_extension(self, extension: str, query_type: str, query_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Query an extension for specific information.
        
        Args:
            extension: Target extension name
            query_type: Type of query
            query_data: Query parameters
            
        Returns:
            Query results
        """
        return self.send_to_extension(extension, f"query_{query_type}", query_data)


class BaseToolExtensionInterface:
    """
    Simple interface for base tool to communicate with extensions.
    
    Usage in existing code:
        from extensions.bridge import BaseToolExtensionInterface
        
        interface = BaseToolExtensionInterface()
        result = interface.query_recall(
            start_time="2024-12-29 10:00:00",
            end_time="2024-12-29 18:00:00",
            device_serial="ABC123"
        )
    """
    
    def __init__(self):
        """Initialize the extension interface."""
        self.bridge = IPIBridge()
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for the interface."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # ═══════════════════════════════════════════════════════════
    # Recall Provider Interface
    # ═══════════════════════════════════════════════════════════
    
    def query_recall(self, start_time: str, end_time: str, device_serial: str = None) -> Dict[str, Any]:
        """
        Query Windows 11 Recall database for USB session activity.
        
        Args:
            start_time: Start timestamp (ISO format or 'YYYY-MM-DD HH:MM:SS')
            end_time: End timestamp
            device_serial: Optional device serial to filter
            
        Returns:
            Dictionary with recall data and OCR text
        """
        data = {
            'start_time': start_time,
            'end_time': end_time,
            'device_serial': device_serial
        }
        
        result = self.bridge.send_to_extension('recall_provider', 'query_recall', data)
        return result or {}
    
    def get_recall_snapshots(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        Get Recall snapshots for time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of snapshot records
        """
        result = self.query_recall(start_time, end_time)
        return result.get('snapshots', []) if result else []
    
    def get_recall_ocr_text(self, start_time: str, end_time: str) -> List[str]:
        """
        Extract OCR text from Recall for time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of OCR text strings
        """
        result = self.query_recall(start_time, end_time)
        return result.get('ocr_text', []) if result else []
    
    # ═══════════════════════════════════════════════════════════
    # Firmware Validator Interface
    # ═══════════════════════════════════════════════════════════
    
    def validate_firmware(self, vendor_id: str, product_id: str, device_name: str = None) -> Dict[str, Any]:
        """
        Validate device firmware and detect BadUSB indicators.
        
        Args:
            vendor_id: USB Vendor ID (e.g., '0x1234')
            product_id: USB Product ID (e.g., '0x5678')
            device_name: Optional device name for context
            
        Returns:
            Risk assessment with firmware details
        """
        data = {
            'vendor_id': vendor_id,
            'product_id': product_id,
            'device_name': device_name
        }
        
        result = self.bridge.send_to_extension('firmware_validator', 'validate_firmware', data)
        return result or {}
    
    def get_badusb_risk_score(self, vendor_id: str, product_id: str) -> float:
        """
        Get BadUSB risk score for device.
        
        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            
        Returns:
            Risk score 0.0-1.0 (0=safe, 1=critical)
        """
        result = self.validate_firmware(vendor_id, product_id)
        return result.get('risk_score', 0.0) if result else 0.0
    
    def detect_hidden_interfaces(self, vendor_id: str, product_id: str) -> List[Dict[str, Any]]:
        """
        Detect hidden HID interfaces (BadUSB signatures).
        
        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            
        Returns:
            List of detected hidden interfaces
        """
        result = self.validate_firmware(vendor_id, product_id)
        return result.get('hidden_interfaces', []) if result else []
    
    # ═══════════════════════════════════════════════════════════
    # AI Reporter Interface
    # ═══════════════════════════════════════════════════════════
    
    def generate_narrative_report(self, raw_logs: List[str], analysis_data: Dict[str, Any] = None) -> str:
        """
        Generate AI-powered narrative report from raw logs.
        
        Args:
            raw_logs: List of raw log entries
            analysis_data: Additional analysis context
            
        Returns:
            Formatted narrative report
        """
        data = {
            'raw_logs': raw_logs,
            'analysis_data': analysis_data or {}
        }
        
        result = self.bridge.send_to_extension('ai_reporter', 'generate_report', data)
        return result.get('report', '') if result else ''
    
    def generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate executive summary for investigation.
        
        Args:
            analysis_results: Analysis results from base tool
            
        Returns:
            Executive summary text
        """
        data = {'analysis_results': analysis_results}
        result = self.bridge.send_to_extension('ai_reporter', 'executive_summary', data)
        return result.get('summary', '') if result else ''


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION EXAMPLES FOR BASE TOOL
# ═══════════════════════════════════════════════════════════════════════════

def example_usage():
    """
    Example of how to use the extension interface in existing base tool.
    
    Just add this to any module in your base tool:
    """
    
    # Initialize extension interface (one time)
    ext = BaseToolExtensionInterface()
    
    # Example 1: Query Recall database
    print("\n=== Example 1: Query Windows 11 Recall ===")
    recall_data = ext.query_recall(
        start_time="2024-12-29 10:00:00",
        end_time="2024-12-29 18:00:00",
        device_serial="USB123456"
    )
    print(f"Recall Data: {json.dumps(recall_data, indent=2)}")
    
    # Example 2: Check for BadUSB
    print("\n=== Example 2: Firmware Validation ===")
    risk_score = ext.get_badusb_risk_score("0x1234", "0x5678")
    print(f"BadUSB Risk Score: {risk_score}")
    
    # Example 3: Generate narrative report
    print("\n=== Example 3: AI Narrative Report ===")
    logs = ["Device connected at 10:00", "File activity detected", "Device safely ejected at 18:00"]
    report = ext.generate_narrative_report(logs)
    print(f"Report:\n{report}")


if __name__ == '__main__':
    # Test bridge connectivity
    print("IPI Bridge - Testing Extension Communication Layer")
    print("="*70)
    
    bridge = IPIBridge()
    print(f"✓ Bridge initialized")
    print(f"✓ Extensions directory: {bridge.extensions_dir}")
    print("\nReady to communicate with extension modules.")
    print("\nTo use in your base tool:")
    print("  from extensions.bridge import BaseToolExtensionInterface")
    print("  ext = BaseToolExtensionInterface()")
    print("  recall_data = ext.query_recall(...)")
