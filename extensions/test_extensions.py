#!/usr/bin/env python3
"""
Extension Test Suite - Verify IPI Bridge and Recall Provider

Run this to test the extension architecture before integrating with base tool.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add extensions to path
extensions_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, extensions_dir)

def print_section(title):
    """Print formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_bridge_initialization():
    """Test 1: Bridge Initialization"""
    print_section("TEST 1: Bridge Initialization")
    
    try:
        from bridge import IPIBridge
        bridge = IPIBridge()
        print(f"✓ IPIBridge initialized successfully")
        print(f"  Extensions directory: {bridge.extensions_dir}")
        print(f"  Status: {bridge.message_queue}")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize IPIBridge: {e}")
        return False

def test_interface_initialization():
    """Test 2: Extension Interface"""
    print_section("TEST 2: Extension Interface Initialization")
    
    try:
        from bridge import BaseToolExtensionInterface
        interface = BaseToolExtensionInterface()
        print(f"✓ BaseToolExtensionInterface initialized successfully")
        print(f"  Ready to query extensions")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize interface: {e}")
        return False

def test_recall_provider():
    """Test 3: Recall Provider Initialization"""
    print_section("TEST 3: Recall Provider Initialization")
    
    try:
        from recall_provider import RecallProvider
        provider = RecallProvider()
        print(f"✓ RecallProvider initialized successfully")
        print(f"  Current user: {provider.user}")
        print(f"  Recall database path: {provider.recall_root}")
        
        if provider.recall_root:
            print(f"  ✓ Recall database location found")
        else:
            print(f"  ⚠ Recall database not found (may not be enabled)")
        
        return True
    except Exception as e:
        print(f"✗ Failed to initialize RecallProvider: {e}")
        return False

def test_message_format():
    """Test 4: Message Format Validation"""
    print_section("TEST 4: IPI Message Format")
    
    try:
        from bridge import IPIBridge
        bridge = IPIBridge()
        
        message = bridge.create_message(
            extension='recall_provider',
            action='query_recall',
            data={
                'start_time': '2024-12-29 10:00:00',
                'end_time': '2024-12-29 18:00:00',
                'device_serial': 'TEST123'
            }
        )
        
        print(f"✓ Message created successfully")
        print(f"\nMessage structure:")
        print(json.dumps(message, indent=2))
        
        # Verify required fields
        required_fields = ['version', 'timestamp', 'extension', 'action', 'data', 'message_id']
        missing = [f for f in required_fields if f not in message]
        
        if missing:
            print(f"\n✗ Missing fields: {missing}")
            return False
        else:
            print(f"\n✓ All required fields present")
            return True
    
    except Exception as e:
        print(f"✗ Failed message format test: {e}")
        return False

def test_timestamp_parsing():
    """Test 5: Timestamp Parsing"""
    print_section("TEST 5: Timestamp Parsing")
    
    try:
        from recall_provider import RecallProvider
        provider = RecallProvider()
        
        test_cases = [
            "2024-12-29 10:00:00",
            "2024-12-29T10:00:00",
            str(int(datetime.now().timestamp())),
        ]
        
        all_passed = True
        for timestamp_str in test_cases:
            result = provider._parse_timestamp(timestamp_str)
            status = "✓" if result else "✗"
            print(f"{status} Parsed '{timestamp_str}' → {result}")
            if not result:
                all_passed = False
        
        return all_passed
    
    except Exception as e:
        print(f"✗ Failed timestamp parsing test: {e}")
        return False

def test_interface_methods():
    """Test 6: Interface Method Signatures"""
    print_section("TEST 6: Interface Method Signatures")
    
    try:
        from bridge import BaseToolExtensionInterface
        interface = BaseToolExtensionInterface()
        
        methods = {
            'query_recall': 'Recall database query',
            'get_recall_snapshots': 'Get recall snapshots',
            'get_recall_ocr_text': 'Get OCR text',
            'validate_firmware': 'Firmware validation',
            'get_badusb_risk_score': 'BadUSB risk assessment',
            'detect_hidden_interfaces': 'HID detection',
            'generate_narrative_report': 'AI report generation',
            'generate_executive_summary': 'Executive summary'
        }
        
        all_exist = True
        for method_name, description in methods.items():
            if hasattr(interface, method_name):
                print(f"✓ {method_name:<30} - {description}")
            else:
                print(f"✗ {method_name:<30} - MISSING")
                all_exist = False
        
        return all_exist
    
    except Exception as e:
        print(f"✗ Failed method signature test: {e}")
        return False

def test_integration_flow():
    """Test 7: Full Integration Flow (Simulated)"""
    print_section("TEST 7: Integration Flow Simulation")
    
    try:
        from bridge import BaseToolExtensionInterface
        interface = BaseToolExtensionInterface()
        
        print("Simulating USB device forensics investigation...")
        
        # Simulate device data
        device = {
            'serial': 'USB_TEST_123',
            'vendor_id': '0x1234',
            'product_id': '0x5678',
            'name': 'Test USB Device'
        }
        
        print(f"\n1. Device detected: {device['name']}")
        print(f"   Serial: {device['serial']}")
        
        # Query Recall (will return no_data if disabled)
        print(f"\n2. Querying Windows 11 Recall for device activity...")
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        result = interface.query_recall(
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            device_serial=device['serial']
        )
        
        print(f"   Status: {result.get('status', 'unknown')}")
        if result.get('status') != 'error':
            summary = result.get('summary', {})
            print(f"   Snapshots: {summary.get('total_snapshots', 0)}")
            print(f"   OCR entries: {summary.get('ocr_entries', 0)}")
        
        # Check firmware
        print(f"\n3. Validating firmware and BadUSB risk...")
        risk_score = interface.get_badusb_risk_score(
            device['vendor_id'],
            device['product_id']
        )
        print(f"   Risk Score: {risk_score:.2f} (0.0=safe, 1.0=critical)")
        
        if risk_score < 0.3:
            print(f"   Assessment: ✓ Low Risk")
        elif risk_score < 0.6:
            print(f"   Assessment: ⚠ Medium Risk")
        else:
            print(f"   Assessment: ✗ High Risk")
        
        print(f"\n✓ Integration flow completed successfully")
        return True
    
    except Exception as e:
        print(f"✗ Failed integration flow test: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_results(results):
    """Print test results summary."""
    print_section("TEST RESULTS SUMMARY")
    
    tests = [
        "1. Bridge Initialization",
        "2. Extension Interface",
        "3. Recall Provider",
        "4. Message Format",
        "5. Timestamp Parsing",
        "6. Interface Methods",
        "7. Integration Flow"
    ]
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test}")
    
    print(f"\n{'='*70}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"\n🎉 All tests passed! Extension architecture is ready.")
        print(f"\nNext steps:")
        print(f"1. Integrate extensions into gui_enhanced.py")
        print(f"2. Test with actual USB devices")
        print(f"3. Deploy firmware_validator and ai_reporter modules")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Review errors above.")
    
    print(f"{'='*70}\n")

def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  USB Forensics Tool - Extension Test Suite".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    results = [
        test_bridge_initialization(),
        test_interface_initialization(),
        test_recall_provider(),
        test_message_format(),
        test_timestamp_parsing(),
        test_interface_methods(),
        test_integration_flow()
    ]
    
    print_results(results)
    
    # Return exit code
    return 0 if all(results) else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
