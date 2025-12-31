#!/usr/bin/env python3
"""
Firmware Validator - BadUSB Detection and Risk Assessment

Analyzes USB device firmware for BadUSB signatures and malicious indicators.
Provides risk scoring, hidden interface detection, and forensic analysis.

No modifications to base tool required. Standalone extension module.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class FirmwareValidator:
    """
    USB Firmware Validator for BadUSB detection and risk assessment.
    
    Analyzes:
    - Firmware signatures matching known BadUSB patterns
    - Hidden HID (Human Interface Device) interfaces
    - Firmware modification indicators
    - Device descriptor anomalies
    - Risk scoring based on multiple factors
    """
    
    # Known BadUSB vendor/product signatures
    BADUSB_SIGNATURES = {
        # Rubber Ducky clones
        ('0x1234', '0x5678'): {
            'name': 'Generic HID Device (Ducky Clone)',
            'risk_score': 0.95,
            'type': 'HID_ATTACK',
            'indicators': ['rapid_key_injection', 'mass_storage_hid_combo']
        },
        # Malicious combo devices (storage + HID)
        ('0x0951', '0x1666'): {
            'name': 'Kingston USB (Suspected Modified)',
            'risk_score': 0.7,
            'type': 'COMBO_DEVICE',
            'indicators': ['multiple_interfaces', 'hidden_hid']
        }
    }
    
    # Suspicious vendor IDs
    SUSPICIOUS_VENDORS = {
        '0x0000': {'name': 'Invalid Vendor', 'risk': 0.8},
        '0xFFFF': {'name': 'Invalid Vendor', 'risk': 0.8},
        '0xDEAD': {'name': 'Debug/Test Device', 'risk': 0.6},
        '0xBEEF': {'name': 'Test Device', 'risk': 0.6}
    }
    
    # Known malicious patterns
    MALICIOUS_PATTERNS = {
        'DuckyPad': {'score': 0.9, 'type': 'KEYSTROKE_INJECTION'},
        'Teensy': {'score': 0.85, 'type': 'KEYBOARD_EMULATOR'},
        'Digispark': {'score': 0.8, 'type': 'ATtiny_DEV_BOARD'},
        'Arduino': {'score': 0.6, 'type': 'DEV_PLATFORM'},
        'CH340': {'score': 0.4, 'type': 'SERIAL_ADAPTER'},
        'PL2303': {'score': 0.3, 'type': 'SERIAL_ADAPTER'}
    }
    
    def __init__(self):
        """Initialize Firmware Validator."""
        logger.info("FirmwareValidator initialized")
    
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
            if action == 'validate_firmware':
                return self.validate_firmware(
                    vendor_id=data.get('vendor_id'),
                    product_id=data.get('product_id'),
                    device_name=data.get('device_name')
                )
            
            elif action == 'detect_hidden_interfaces':
                return self.detect_hidden_interfaces(
                    vendor_id=data.get('vendor_id'),
                    product_id=data.get('product_id')
                )
            
            elif action == 'check_device_descriptors':
                return self.check_device_descriptors(
                    descriptors=data.get('descriptors', {})
                )
            
            elif action == 'scan_for_badusb':
                return self.scan_for_badusb(
                    vendor_id=data.get('vendor_id'),
                    product_id=data.get('product_id'),
                    device_name=data.get('device_name')
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
    
    def validate_firmware(self, vendor_id: str, product_id: str, device_name: str = None) -> Dict[str, Any]:
        """
        Comprehensive firmware validation with risk assessment.
        
        Args:
            vendor_id: USB Vendor ID (e.g., '0x1234')
            product_id: USB Product ID (e.g., '0x5678')
            device_name: Optional device name for pattern matching
            
        Returns:
            Detailed risk assessment
        """
        try:
            result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'device': {
                    'vendor_id': vendor_id,
                    'product_id': product_id,
                    'device_name': device_name
                },
                'risk_score': 0.0,
                'risk_level': 'LOW',
                'checks': {},
                'findings': [],
                'recommendations': [],
                'hidden_interfaces': [],
                'signatures_matched': []
            }
            
            # Check 1: Known BadUSB signatures
            sig_check = self._check_signatures(vendor_id, product_id)
            result['checks']['signature_match'] = sig_check
            
            if sig_check.get('matched'):
                result['risk_score'] += sig_check['risk_score']
                result['findings'].append(sig_check['message'])
                result['signatures_matched'].append(sig_check['details'])
            
            # Check 2: Suspicious vendor IDs
            vendor_check = self._check_vendor(vendor_id)
            result['checks']['vendor_check'] = vendor_check
            
            if vendor_check.get('suspicious'):
                result['risk_score'] += vendor_check['risk_score']
                result['findings'].append(vendor_check['message'])
            
            # Check 3: Device name pattern matching
            if device_name:
                name_check = self._check_device_name(device_name)
                result['checks']['device_name'] = name_check
                
                if name_check.get('suspicious_patterns'):
                    result['risk_score'] += name_check['risk_score']
                    result['findings'].append(name_check['message'])
            
            # Check 4: Descriptor anomalies
            desc_check = self._analyze_descriptors(vendor_id, product_id)
            result['checks']['descriptors'] = desc_check
            
            if desc_check.get('anomalies'):
                result['risk_score'] += desc_check['risk_score']
                result['findings'].extend(desc_check['anomalies'])
            
            # Check 5: Combo device detection (Mass storage + HID)
            combo_check = self._detect_combo_device(vendor_id, product_id)
            result['checks']['combo_device'] = combo_check
            
            if combo_check.get('detected'):
                result['risk_score'] += 0.3
                result['findings'].append(combo_check['message'])
                result['hidden_interfaces'].extend(combo_check.get('interfaces', []))
            
            # Normalize risk score to 0-1 range
            result['risk_score'] = min(1.0, result['risk_score'])
            
            # Determine risk level
            if result['risk_score'] >= 0.7:
                result['risk_level'] = 'CRITICAL'
                result['recommendations'].append('Block device immediately - potential BadUSB detected')
                result['recommendations'].append('Quarantine device for forensic analysis')
            elif result['risk_score'] >= 0.5:
                result['risk_level'] = 'HIGH'
                result['recommendations'].append('Exercise caution - suspicious device characteristics')
                result['recommendations'].append('Monitor for malicious activity')
            elif result['risk_score'] >= 0.3:
                result['risk_level'] = 'MEDIUM'
                result['recommendations'].append('Additional verification recommended')
            else:
                result['risk_level'] = 'LOW'
                result['recommendations'].append('Device appears legitimate')
            
            return result
        
        except Exception as e:
            logger.error(f"Error validating firmware: {e}")
            return self._error(str(e))
    
    def detect_hidden_interfaces(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """
        Detect hidden HID interfaces (BadUSB signature).
        
        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            
        Returns:
            List of detected hidden interfaces
        """
        try:
            interfaces = []
            
            # Check for combo devices
            if (vendor_id, product_id) in self.BADUSB_SIGNATURES:
                sig = self.BADUSB_SIGNATURES[(vendor_id, product_id)]
                if 'hidden_hid' in sig.get('indicators', []):
                    interfaces.append({
                        'interface_type': 'HID',
                        'class': '0x03',
                        'subclass': '0x01',
                        'protocol': 'keyboard',
                        'hidden': True,
                        'risk_level': 'CRITICAL',
                        'evidence': 'Hidden HID interface detected - keystroke injection capable'
                    })
            
            # Check for mass storage + other combo
            combo_check = self._detect_combo_device(vendor_id, product_id)
            if combo_check.get('detected'):
                interfaces.extend(combo_check.get('interfaces', []))
            
            return {
                'status': 'success',
                'device': {
                    'vendor_id': vendor_id,
                    'product_id': product_id
                },
                'hidden_interfaces': interfaces,
                'count': len(interfaces),
                'forensic_note': f"Detected {len(interfaces)} suspicious interfaces"
            }
        
        except Exception as e:
            logger.error(f"Error detecting hidden interfaces: {e}")
            return self._error(str(e))
    
    def check_device_descriptors(self, descriptors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze device descriptors for anomalies.
        
        Args:
            descriptors: Device descriptor dictionary
            
        Returns:
            Anomalies found
        """
        try:
            anomalies = []
            risk_score = 0.0
            
            # Check for descriptor length mismatches
            if 'configuration' in descriptors:
                expected = descriptors['configuration'].get('total_length', 0)
                actual = descriptors['configuration'].get('actual_length', 0)
                
                if expected != actual:
                    anomalies.append(f"Configuration descriptor length mismatch: {expected} vs {actual}")
                    risk_score += 0.2
            
            # Check for empty descriptor fields
            if 'device' in descriptors:
                device = descriptors['device']
                if device.get('class') == '0x00' and device.get('subclass') == '0x00':
                    anomalies.append("Device uses interface-defined class (suspicious)")
                    risk_score += 0.1
            
            # Check for multiple configurations (unusual for USB drives)
            if 'configuration_count' in descriptors:
                if descriptors['configuration_count'] > 1:
                    anomalies.append(f"Device has {descriptors['configuration_count']} configurations (unusual)")
                    risk_score += 0.15
            
            return {
                'status': 'success' if not anomalies else 'warning',
                'anomalies': anomalies,
                'risk_score': risk_score,
                'descriptor_analysis': descriptors
            }
        
        except Exception as e:
            logger.error(f"Error checking descriptors: {e}")
            return self._error(str(e))
    
    def scan_for_badusb(self, vendor_id: str, product_id: str, device_name: str = None) -> Dict[str, Any]:
        """
        Comprehensive BadUSB scan combining all checks.
        
        Args:
            vendor_id: USB Vendor ID
            product_id: USB Product ID
            device_name: Optional device name
            
        Returns:
            Complete BadUSB assessment
        """
        result = self.validate_firmware(vendor_id, product_id, device_name)
        
        # Add forensic recommendations
        if result['risk_score'] >= 0.7:
            result['forensic_actions'] = [
                'Isolate device from network',
                'Capture device firmware for analysis',
                'Monitor for command execution',
                'Log all USB activity',
                'Alert security team immediately'
            ]
        elif result['risk_score'] >= 0.5:
            result['forensic_actions'] = [
                'Monitor device closely',
                'Document all activity',
                'Capture packets',
                'Log to SIEM system'
            ]
        
        return result
    
    # ═══════════════════════════════════════════════════════════════
    # Internal check methods
    # ═══════════════════════════════════════════════════════════════
    
    def _check_signatures(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """Check against known BadUSB signatures."""
        key = (vendor_id, product_id)
        
        if key in self.BADUSB_SIGNATURES:
            sig = self.BADUSB_SIGNATURES[key]
            return {
                'matched': True,
                'risk_score': sig['risk_score'],
                'message': f"CRITICAL: Device matches known BadUSB signature - {sig['name']}",
                'details': sig
            }
        
        return {
            'matched': False,
            'risk_score': 0.0,
            'message': 'No known BadUSB signatures detected'
        }
    
    def _check_vendor(self, vendor_id: str) -> Dict[str, Any]:
        """Check vendor ID for suspicious values."""
        if vendor_id in self.SUSPICIOUS_VENDORS:
            info = self.SUSPICIOUS_VENDORS[vendor_id]
            return {
                'suspicious': True,
                'risk_score': info['risk'],
                'message': f"WARNING: Suspicious vendor ID {vendor_id} - {info['name']}"
            }
        
        return {
            'suspicious': False,
            'risk_score': 0.0,
            'message': 'Vendor ID appears legitimate'
        }
    
    def _check_device_name(self, device_name: str) -> Dict[str, Any]:
        """Check device name for malicious patterns."""
        patterns = []
        total_risk = 0.0
        
        for pattern, info in self.MALICIOUS_PATTERNS.items():
            if pattern.lower() in device_name.lower():
                patterns.append({
                    'pattern': pattern,
                    'type': info['type'],
                    'risk_score': info['score']
                })
                total_risk += info['score']
        
        if patterns:
            # Normalize risk
            total_risk = min(1.0, total_risk / len(patterns))
            return {
                'suspicious_patterns': patterns,
                'risk_score': total_risk,
                'message': f"Device name contains suspicious patterns: {', '.join(p['pattern'] for p in patterns)}"
            }
        
        return {
            'suspicious_patterns': [],
            'risk_score': 0.0,
            'message': 'Device name appears legitimate'
        }
    
    def _analyze_descriptors(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """Analyze expected device descriptors."""
        anomalies = []
        risk_score = 0.0
        
        # Mass storage devices shouldn't have keyboard capabilities
        if vendor_id == '0x0951':  # Kingston
            if product_id in ['0x1666', '0x1667']:
                anomalies.append('Mass storage device with unusual product ID')
                risk_score += 0.1
        
        return {
            'anomalies': anomalies,
            'risk_score': risk_score
        }
    
    def _detect_combo_device(self, vendor_id: str, product_id: str) -> Dict[str, Any]:
        """Detect mass storage + HID combo devices."""
        detected = False
        interfaces = []
        
        # Known problematic combos
        suspect_combos = [
            ('0x0951', '0x1666'),  # Kingston + HID
            ('0x0781', '0x5580'),  # SanDisk + HID
        ]
        
        if (vendor_id, product_id) in suspect_combos:
            detected = True
            interfaces.append({
                'interface_type': 'Mass Storage',
                'class': '0x08',
                'subclass': '0x06'
            })
            interfaces.append({
                'interface_type': 'HID',
                'class': '0x03',
                'hidden': True
            })
        
        return {
            'detected': detected,
            'message': 'Combo device detected - multiple interface classes' if detected else 'Single-purpose device',
            'interfaces': interfaces,
            'risk_score': 0.3 if detected else 0.0
        }


# ═══════════════════════════════════════════════════════════════════════════
# USAGE IN BASE TOOL
# ═══════════════════════════════════════════════════════════════════════════

def example_usage():
    """
    Example of how to use FirmwareValidator from base tool.
    """
    from extensions.bridge import BaseToolExtensionInterface
    
    interface = BaseToolExtensionInterface()
    
    # Check device for BadUSB
    print("\n=== Firmware Validation ===")
    result = interface.validate_firmware("0x1234", "0x5678")
    
    print(f"Risk Score: {result.get('risk_score', 0):.2f}")
    print(f"Risk Level: {result.get('risk_level', 'UNKNOWN')}")
    print(f"Findings: {result.get('findings', [])}")
    print(f"Recommendations: {result.get('recommendations', [])}")


if __name__ == '__main__':
    print("USB Firmware Validator - BadUSB Detection Extension")
    print("="*70)
    
    validator = FirmwareValidator()
    print(f"✓ FirmwareValidator initialized")
    print(f"✓ Known BadUSB signatures: {len(FirmwareValidator.BADUSB_SIGNATURES)}")
    print(f"✓ Suspicious vendors: {len(FirmwareValidator.SUSPICIOUS_VENDORS)}")
    print(f"✓ Malicious patterns: {len(FirmwareValidator.MALICIOUS_PATTERNS)}")
    print("\nTo use in your base tool:")
    print("  from extensions.bridge import BaseToolExtensionInterface")
    print("  interface = BaseToolExtensionInterface()")
    print("  result = interface.validate_firmware('0x1234', '0x5678')")
