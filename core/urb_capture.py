"""USB Request Block (URB) Capture and Parsing Module.

This module provides complete URB capture capabilities:
- Full URB parsing from .etl files
- Real-time event processing via ETW
- Complete URB data extraction with all fields

Requires:
    - Administrator privileges
    - Windows system
    - Optional: etl-parser library (pip install etl-parser) for .etl file parsing
    - Optional: pythonnet (pip install pythonnet) for advanced .NET ETW APIs
"""

import logging
import subprocess
import os
import sys
import platform
import ctypes
import struct
import threading
import queue
import time
import shutil
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
from enum import IntEnum

try:
    import settings as app_settings
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Check for administrator privileges
def _check_admin() -> bool:
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# USB URB Function Codes (from Windows USB headers)
class URBFunction(IntEnum):
    """URB Function codes from usb.h"""
    URB_FUNCTION_SELECT_CONFIGURATION = 0x0000
    URB_FUNCTION_SELECT_INTERFACE = 0x0001
    URB_FUNCTION_ABORT_PIPE = 0x0002
    URB_FUNCTION_TAKE_FRAME_LENGTH_CONTROL = 0x0003
    URB_FUNCTION_RELEASE_FRAME_LENGTH_CONTROL = 0x0004
    URB_FUNCTION_GET_FRAME_LENGTH = 0x0005
    URB_FUNCTION_SET_FRAME_LENGTH = 0x0006
    URB_FUNCTION_GET_CURRENT_FRAME_NUMBER = 0x0007
    URB_FUNCTION_CONTROL_TRANSFER = 0x0008
    URB_FUNCTION_BULK_OR_INTERRUPT_TRANSFER = 0x0009
    URB_FUNCTION_ISOCH_TRANSFER = 0x000a
    URB_FUNCTION_GET_DESCRIPTOR_FROM_DEVICE = 0x000b
    URB_FUNCTION_SET_DESCRIPTOR_TO_DEVICE = 0x000c
    URB_FUNCTION_SET_FEATURE_TO_DEVICE = 0x000d
    URB_FUNCTION_SET_FEATURE_TO_INTERFACE = 0x000e
    URB_FUNCTION_SET_FEATURE_TO_ENDPOINT = 0x000f
    URB_FUNCTION_CLEAR_FEATURE_TO_DEVICE = 0x0010
    URB_FUNCTION_CLEAR_FEATURE_TO_INTERFACE = 0x0011
    URB_FUNCTION_CLEAR_FEATURE_TO_ENDPOINT = 0x0012
    URB_FUNCTION_GET_STATUS_FROM_DEVICE = 0x0013
    URB_FUNCTION_GET_STATUS_FROM_INTERFACE = 0x0014
    URB_FUNCTION_GET_STATUS_FROM_ENDPOINT = 0x0015
    URB_FUNCTION_RESERVED_0X0016 = 0x0016
    URB_FUNCTION_VENDOR_DEVICE = 0x0017
    URB_FUNCTION_VENDOR_INTERFACE = 0x0018
    URB_FUNCTION_VENDOR_ENDPOINT = 0x0019
    URB_FUNCTION_CLASS_DEVICE = 0x001a
    URB_FUNCTION_CLASS_INTERFACE = 0x001b
    URB_FUNCTION_CLASS_ENDPOINT = 0x001c
    URB_FUNCTION_RESERVE_0X001D = 0x001d
    URB_FUNCTION_SYNC_RESET_PIPE_AND_CLEAR_STALL = 0x001e
    URB_FUNCTION_CLASS_OTHER = 0x001f
    URB_FUNCTION_VENDOR_OTHER = 0x0020
    URB_FUNCTION_GET_STATUS_FROM_OTHER = 0x0021
    URB_FUNCTION_SET_FEATURE_TO_OTHER = 0x0022
    URB_FUNCTION_CLEAR_FEATURE_TO_OTHER = 0x0023
    URB_FUNCTION_GET_INTERFACE = 0x0024
    URB_FUNCTION_SET_INTERFACE = 0x0025
    URB_FUNCTION_GET_CONFIGURATION = 0x0026
    URB_FUNCTION_GET_DESCRIPTOR_FROM_ENDPOINT = 0x0027
    URB_FUNCTION_SET_DESCRIPTOR_TO_ENDPOINT = 0x0028
    URB_FUNCTION_SET_CONFIGURATION = 0x0029
    URB_FUNCTION_GET_DESCRIPTOR_FROM_INTERFACE = 0x002a
    URB_FUNCTION_SET_DESCRIPTOR_TO_INTERFACE = 0x002b
    URB_FUNCTION_GET_MS_FEATURE_DESCRIPTOR = 0x002c


# USB Transfer Status Codes
class URBStatus(IntEnum):
    """URB Status codes"""
    USBD_STATUS_SUCCESS = 0x00000000
    USBD_STATUS_PENDING = 0x40000000
    USBD_STATUS_ERROR = 0xC0000000
    USBD_STATUS_HALTED = 0xC0000001
    USBD_STATUS_INVALID_REQUEST = 0xC0000002
    USBD_STATUS_INVALID_PIPE_HANDLE = 0xC0000003
    USBD_STATUS_NO_BANDWIDTH = 0xC0000004
    USBD_STATUS_INTERNAL_HC_ERROR = 0xC0000005
    USBD_STATUS_ERROR_SHORT_TRANSFER = 0xC0000006
    USBD_STATUS_BAD_START_FRAME = 0xC0000007
    USBD_STATUS_ISOCH_REQUEST_FAILED = 0xC0000008
    USBD_STATUS_FRAME_CONTROL_OWNED = 0xC0000009
    USBD_STATUS_FRAME_CONTROL_NOT_OWNED = 0xC000000a
    USBD_STATUS_NOT_SUPPORTED = 0xC000000b
    USBD_STATUS_INAVLID_URB_FUNCTION = 0xC000000c
    USBD_STATUS_INVALID_PARAMETER = 0xC000000d
    USBD_STATUS_ERROR_BUSY = 0xC000000e


@dataclass
class URBTransfer:
    """Complete URB transfer information."""
    timestamp: str
    urb_function: int
    urb_function_name: str
    status: int
    status_name: str
    device_id: str = ""
    vid: str = ""
    pid: str = ""
    endpoint_address: int = 0
    endpoint_direction: str = ""  # IN, OUT
    transfer_buffer_length: int = 0
    actual_length: int = 0
    transfer_flags: int = 0
    transfer_buffer: bytes = field(default_factory=bytes)
    setup_packet: Dict[str, Any] = field(default_factory=dict)  # For control transfers
    interval: int = 0  # For interrupt/isochronous
    start_frame: int = 0  # For isochronous
    number_of_packets: int = 0  # For isochronous
    error_count: int = 0
    pipe_handle: int = 0
    usbd_status: str = ""
    timeout: int = 0
    request_type: int = 0  # bmRequestType for control transfers
    request: int = 0  # bRequest for control transfers
    value: int = 0  # wValue for control transfers
    index: int = 0  # wIndex for control transfers
    length: int = 0  # wLength for control transfers
    raw_data: Dict[str, Any] = field(default_factory=dict)
    event_id: int = 0
    process_id: int = 0
    thread_id: int = 0


class URBCapture:
    """Complete URB capture and parsing implementation."""
    
    def __init__(self):
        self.is_admin = _check_admin()
        self.is_windows = platform.system() == "Windows"
        self.trace_file: Optional[str] = None
        self.session_name: str = "USB-Forensics-URB-Trace"
        self.realtime_queue: queue.Queue = queue.Queue()
        self.realtime_thread: Optional[threading.Thread] = None
        self.realtime_running: bool = False
        self.realtime_callback: Optional[Callable[[URBTransfer], None]] = None
        self._realtime_lock = threading.Lock()
        self._logman_available = shutil.which("logman") is not None
        
    def is_available(self) -> bool:
        """Check if URB capture is available."""
        if not self.is_windows:
            logger.warning("URB capture only available on Windows")
            return False
        if not self.is_admin:
            logger.warning("Administrator privileges required for URB capture")
            return False
        if not self._logman_available:
            logger.warning("logman utility not found in PATH - ETW capture unavailable")
            return False
        return True
    
    # ========== .etl FILE PARSING ==========
    
    def parse_etl_file(self, etl_file: str) -> List[URBTransfer]:
        """
        Parse .etl file and extract complete URB data.
        
        Uses etl-parser library for full event extraction.
        Falls back to alternative methods if library not available.
        
        Args:
            etl_file: Path to .etl trace file
            
        Returns:
            List of URBTransfer objects with complete URB data
        """
        if not os.path.exists(etl_file):
            logger.error(f"ETL file not found: {etl_file}")
            return []
        
        urbs = []
        
        # Try using etl-parser library (recommended)
        try:
            from etl.etl import IEtlFileObserver, build_from_stream
            from etl.event import Event
            
            logger.info(f"Parsing ETL file using etl-parser: {etl_file}")
            
            class URBParserObserver(IEtlFileObserver):
                def __init__(self, urb_list):
                    self.urb_list = urb_list
                    self.usb_providers = {
                        'Microsoft-Windows-USB-USBPORT',
                        'Microsoft-Windows-USB-USBXHCI',
                        'Microsoft-Windows-USB-UCX',
                        'Microsoft-Windows-USB-USBHUB3',
                        'Microsoft-Windows-USB-USBHUB'
                    }
                
                def on_event_record(self, event: Event):
                    """Process each event from ETL file."""
                    try:
                        # Check if this is a USB-related event
                        provider_name = getattr(event, 'provider_name', '')
                        if not any(provider in provider_name for provider in self.usb_providers):
                            return
                        
                        # Parse ETW event data
                        event_data = event.parse_etw() if hasattr(event, 'parse_etw') else {}
                        
                        # Extract URB information
                        urb = self._extract_urb_from_event(event, event_data)
                        if urb:
                            self.urb_list.append(urb)
                    except Exception as e:
                        logger.debug(f"Error processing event: {e}")
                
                def _extract_urb_from_event(self, event: Event, event_data: Dict) -> Optional[URBTransfer]:
                    """Extract URB data from ETW event."""
                    try:
                        # Get event properties
                        timestamp = datetime.fromtimestamp(
                            getattr(event, 'timestamp', time.time()),
                            tz=timezone.utc
                        ).isoformat()
                        
                        event_id = getattr(event, 'event_id', 0)
                        process_id = getattr(event, 'process_id', 0)
                        thread_id = getattr(event, 'thread_id', 0)
                        
                        # Extract USB-specific fields from event data
                        # These field names vary by Windows version and provider
                        urb_function = event_data.get('Function', event_data.get('URBFunction', 0))
                        status = event_data.get('Status', event_data.get('USBDStatus', 0))
                        device_id = event_data.get('DeviceId', event_data.get('DeviceID', ''))
                        endpoint = event_data.get('EndpointAddress', event_data.get('Endpoint', 0))
                        transfer_length = event_data.get('TransferBufferLength', event_data.get('Length', 0))
                        actual_length = event_data.get('ActualLength', event_data.get('Actual', 0))
                        
                        # Extract VID/PID from device_id
                        vid, pid = self._extract_vid_pid(device_id)
                        
                        # Determine endpoint direction
                        endpoint_dir = "IN" if (endpoint & 0x80) else "OUT"
                        
                        # Extract transfer buffer data if available
                        transfer_buffer = event_data.get('TransferBuffer', b'')
                        if isinstance(transfer_buffer, str):
                            try:
                                transfer_buffer = bytes.fromhex(transfer_buffer.replace(' ', ''))
                            except:
                                transfer_buffer = b''
                        
                        # Extract setup packet for control transfers
                        setup_packet = {}
                        if urb_function == URBFunction.URB_FUNCTION_CONTROL_TRANSFER:
                            setup_packet = {
                                'bmRequestType': event_data.get('bmRequestType', event_data.get('RequestType', 0)),
                                'bRequest': event_data.get('bRequest', event_data.get('Request', 0)),
                                'wValue': event_data.get('wValue', event_data.get('Value', 0)),
                                'wIndex': event_data.get('wIndex', event_data.get('Index', 0)),
                                'wLength': event_data.get('wLength', event_data.get('Length', 0))
                            }
                        
                        # Create URB transfer object
                        urb = URBTransfer(
                            timestamp=timestamp,
                            urb_function=urb_function,
                            urb_function_name=self._get_urb_function_name(urb_function),
                            status=status,
                            status_name=self._get_status_name(status),
                            device_id=device_id,
                            vid=vid,
                            pid=pid,
                            endpoint_address=endpoint,
                            endpoint_direction=endpoint_dir,
                            transfer_buffer_length=transfer_length,
                            actual_length=actual_length,
                            transfer_buffer=transfer_buffer[:1024],  # Limit to 1KB for storage
                            setup_packet=setup_packet,
                            interval=event_data.get('Interval', 0),
                            start_frame=event_data.get('StartFrame', 0),
                            number_of_packets=event_data.get('NumberOfPackets', 0),
                            error_count=event_data.get('ErrorCount', 0),
                            pipe_handle=event_data.get('PipeHandle', 0),
                            timeout=event_data.get('Timeout', 0),
                            request_type=setup_packet.get('bmRequestType', 0),
                            request=setup_packet.get('bRequest', 0),
                            value=setup_packet.get('wValue', 0),
                            index=setup_packet.get('wIndex', 0),
                            length=setup_packet.get('wLength', 0),
                            raw_data=event_data,
                            event_id=event_id,
                            process_id=process_id,
                            thread_id=thread_id
                        )
                        
                        return urb
                    except Exception as e:
                        logger.debug(f"Error extracting URB: {e}")
                        return None
                
                def _extract_vid_pid(self, device_id: str) -> tuple:
                    """Extract VID and PID from device ID string."""
                    vid, pid = "", ""
                    if 'VID_' in device_id:
                        try:
                            vid_start = device_id.index('VID_') + 4
                            vid = device_id[vid_start:vid_start+4]
                        except:
                            pass
                    if 'PID_' in device_id:
                        try:
                            pid_start = device_id.index('PID_') + 4
                            pid = device_id[pid_start:pid_start+4]
                        except:
                            pass
                    return vid, pid
                
                def _get_urb_function_name(self, func_code: int) -> str:
                    """Get human-readable URB function name."""
                    try:
                        return URBFunction(func_code).name
                    except:
                        return f"UNKNOWN_0x{func_code:04X}"
                
                def _get_status_name(self, status: int) -> str:
                    """Get human-readable status name."""
                    try:
                        return URBStatus(status & 0xFFFFFFFF).name
                    except:
                        return f"STATUS_0x{status:08X}"
            
            # Parse the ETL file
            with open(etl_file, "rb") as f:
                etl_data = f.read()
                etl_reader = build_from_stream(etl_data)
                observer = URBParserObserver(urbs)
                etl_reader.parse(observer)
            
            logger.info(f"Parsed {len(urbs)} URBs from ETL file")
            return urbs
            
        except ImportError:
            logger.warning("etl-parser not installed. Install with: pip install etl-parser")
            logger.info("Falling back to alternative parsing method...")
            return self._parse_etl_alternative(etl_file)
        except Exception as e:
            logger.error(f"Error parsing ETL file: {e}", exc_info=True)
            return []
    
    def _parse_etl_alternative(self, etl_file: str) -> List[URBTransfer]:
        """Alternative ETL parsing using Windows SDK tools (tracerpt).
        
        Note: This is a limited fallback. For full URB parsing, install etl-parser:
            pip install etl-parser
        """
        logger.info("Using alternative parsing method (tracerpt)")
        logger.warning("Alternative parsing has limited functionality. For full URB data, install: pip install etl-parser")
        
        xml_file = etl_file.replace('.etl', '_temp.xml')
        urbs = []
        
        try:
            result = subprocess.run(
                ["tracerpt", etl_file, "-o", xml_file, "-of", "XML"],
                capture_output=True,
                timeout=120,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"tracerpt failed: {result.stderr}")
                return []
            
            if not os.path.exists(xml_file):
                logger.error(f"tracerpt did not create output file: {xml_file}")
                return []
            
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(xml_file)
                root = tree.getroot()
                events = root.findall('.//*[@EventID]')
                logger.info(f"Found {len(events)} events in ETL file (detailed URB parsing requires etl-parser)")
            except Exception as parse_error:
                logger.debug(f"Could not parse XML: {parse_error}")
            
            return urbs
            
        except FileNotFoundError:
            logger.error("tracerpt not found. Please install Windows SDK tools or use etl-parser library.")
            return []
        except Exception as e:
            logger.error(f"Alternative parsing failed: {e}")
            return []
        finally:
            try:
                if os.path.exists(xml_file):
                    os.remove(xml_file)
            except Exception:
                pass
    
    # ========== CREATE .etl FILES ==========
    
    def start_etw_capture(self, duration_seconds: int = 60, 
                         output_file: str = None) -> Optional[str]:
        """
        Start ETW trace session to capture USB URBs to .etl file.
        
        Args:
            duration_seconds: How long to capture (0 = manual stop)
            output_file: Output .etl file path (optional)
            
        Returns:
            Path to trace file if successful, None otherwise
        """
        if not self.is_available():
            return None
            
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Use configured reports directory if available
            reports_dir = "reports"
            if SETTINGS_AVAILABLE:
                try:
                    cfg = app_settings.load_settings()
                    reports_dir = cfg.get('reports_directory', 'reports')
                except Exception:
                    pass
            output_file = os.path.join(reports_dir, f"usb_trace_{timestamp}.etl")
        
        # Ensure reports directory exists
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create reports directory: {e}")
            return None
        
        self.trace_file = output_file
        
        try:
            # Stop any existing session (may not exist, that's OK)
            try:
                result = subprocess.run(
                    ["logman", "stop", self.session_name, "-ets"],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    logger.info(f"Stopped existing ETW session '{self.session_name}'")
            except Exception as e:
                logger.debug(f"Could not stop existing session (may not exist): {e}")
            
            # Start ETW trace session for USB - register ALL providers
            providers = [
                "Microsoft-Windows-USB-USBPORT",
                "Microsoft-Windows-USB-USBXHCI",
                "Microsoft-Windows-USB-UCX"
            ]
            
            # Create and start trace session (use single provider for compatibility)
            cmd = [
                "logman", "create", "trace", self.session_name,
                "-p", providers[0],
                "-o", output_file,
                "-ets"
            ]
            
            logger.debug(f"Running logman: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                logger.error(f"logman failed ({result.returncode}): {error_msg}")
                # Clean up existing session if it exists
                try:
                    subprocess.run(["logman", "delete", self.session_name, "-ets"], capture_output=True, timeout=5)
                except:
                    pass
                return None
            
            logger.info(f"ETW trace started. Output: {output_file}")
            logger.info(f"Capturing USB provider: {providers[0]}")
            if duration_seconds > 0:
                logger.info(f"Capturing for {duration_seconds} seconds...")
                # Schedule stop after duration
                threading.Timer(duration_seconds, self.stop_etw_capture).start()
            
            return output_file
            
        except subprocess.TimeoutExpired:
            logger.error("logman command timed out")
            return None
        except FileNotFoundError:
            logger.error("logman utility not found in PATH")
            return None
        except Exception as e:
            logger.error(f"Error starting ETW capture: {e}")
            return None
    
    def stop_etw_capture(self) -> bool:
        """Stop active ETW trace session."""
        try:
            result = subprocess.run(
                ["logman", "stop", self.session_name, "-ets"],
                capture_output=True,
                timeout=10,
                text=True
            )
            if result.returncode == 0:
                logger.info(f"ETW trace session '{self.session_name}' stopped")
                return True
            else:
                logger.warning(f"Failed to stop session (may not exist): {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error stopping ETW capture: {e}")
            return False
    
    # ========== REAL-TIME EVENT PROCESSING ==========
    
    def start_realtime_capture(self, callback: Callable[[URBTransfer], None],
                              providers: Optional[List[str]] = None) -> bool:
        """
        Start real-time URB capture via ETW.
        
        Args:
            callback: Function to call for each captured URB
            providers: List of ETW provider names (optional)
            
        Returns:
            True if started successfully
        """
        if not self.is_available():
            return False
        
        with self._realtime_lock:
            if self.realtime_running:
                logger.warning("Real-time capture already running")
                return False
            
            self.realtime_callback = callback
            self.realtime_running = True
        
        # Default USB providers
        if not providers:
            providers = [
                "Microsoft-Windows-USB-USBPORT",
                "Microsoft-Windows-USB-USBXHCI",
                "Microsoft-Windows-USB-UCX"
            ]
        
        # Start real-time processing thread
        self.realtime_thread = threading.Thread(
            target=self._realtime_worker,
            args=(providers,),
            daemon=True
        )
        self.realtime_thread.start()
        
        logger.info("Real-time URB capture started")
        return True
    
    def stop_realtime_capture(self) -> bool:
        """Stop real-time URB capture."""
        with self._realtime_lock:
            if not self.realtime_running:
                return False
            
            self.realtime_running = False
        
        if self.realtime_thread:
            self.realtime_thread.join(timeout=5.0)
        
        logger.info("Real-time URB capture stopped")
        return True
    
    def _realtime_worker(self, providers: List[str]):
        """Worker thread for real-time ETW event processing."""
        try:
            # Use configured reports directory
            reports_dir = "reports"
            if SETTINGS_AVAILABLE:
                try:
                    cfg = app_settings.load_settings()
                    reports_dir = cfg.get('reports_directory', 'reports')
                except Exception:
                    pass
            
            temp_trace = os.path.join(reports_dir, f"realtime_urb_{int(time.time())}.etl")
            os.makedirs(os.path.dirname(temp_trace), exist_ok=True)
            
            try:
                # Start ETW session to file
                self._start_etw_session(temp_trace, providers)
                
                last_size = 0
                last_parse_time = time.time()
                processed_urb_ids = set()  # Track processed URBs to avoid duplicates
                
                while self.realtime_running:
                    time.sleep(2)  # Poll every 2 seconds
                    
                    if os.path.exists(temp_trace):
                        current_size = os.path.getsize(temp_trace)
                        if current_size > last_size:
                            # New data available, parse incrementally
                            current_time = time.time()
                            if current_time - last_parse_time > 5:  # Parse every 5 seconds
                                urbs = self.parse_etl_file(temp_trace)
                                # Filter to new URBs - use timestamp + device + endpoint as unique key
                                for urb in urbs:
                                    # Create unique identifier from URB properties
                                    urb_id = f"{urb.timestamp}|{urb.device_id}|{urb.endpoint_address}|{urb.transfer_buffer_length}"
                                    if urb_id not in processed_urb_ids:
                                        processed_urb_ids.add(urb_id)
                                        if self.realtime_callback:
                                            self.realtime_callback(urb)
                                last_parse_time = current_time
                                last_size = current_size
                
            finally:
                self._stop_etw_session()
                try:
                    if os.path.exists(temp_trace):
                        os.remove(temp_trace)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Real-time worker error: {e}", exc_info=True)
            with self._realtime_lock:
                self.realtime_running = False
    
    def _start_etw_session(self, output_file: str, providers: List[str]) -> bool:
        """Start ETW trace session with USB providers."""
        try:
            # Stop any existing session (may not exist, that's OK)
            try:
                subprocess.run(
                    ["logman", "stop", self.session_name, "-ets"],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass  # Session may not exist
            
            # Clean up leftover session
            try:
                subprocess.run(
                    ["logman", "delete", self.session_name, "-ets"],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass
            
            # Create and start new session with main provider
            cmd = [
                "logman", "create", "trace", self.session_name,
                "-p", providers[0] if providers else "Microsoft-Windows-USB-USBPORT",
                "-o", output_file,
                "-ets"
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=10, text=True)
            if result.returncode == 0:
                logger.info("ETW session started successfully")
            else:
                logger.error(f"ETW session failed: {result.stderr.strip() if result.stderr else 'Unknown'}")
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to start ETW session: {e}")
            return False
    
    def _stop_etw_session(self) -> bool:
        """Stop ETW trace session."""
        try:
            result = subprocess.run(
                ["logman", "stop", self.session_name, "-ets"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to stop ETW session: {e}")
            return False
    
    def _get_urb_function_name(self, func_code: int) -> str:
        """Get human-readable URB function name."""
        try:
            return URBFunction(func_code).name
        except:
            return f"UNKNOWN_0x{func_code:04X}"
    
    def _get_status_name(self, status: int) -> str:
        """Get human-readable status name."""
        try:
            return URBStatus(status & 0xFFFFFFFF).name
        except:
            return f"STATUS_0x{status:08X}"


# ========== CONVENIENCE FUNCTIONS ==========

def parse_etl_file(etl_file: str) -> List[URBTransfer]:
    """Parse .etl file and return list of URBs."""
    capture = URBCapture()
    return capture.parse_etl_file(etl_file)


def start_realtime_urb_capture(callback: Callable[[URBTransfer], None]) -> Optional[URBCapture]:
    """Start real-time URB capture with callback."""
    capture = URBCapture()
    if capture.start_realtime_capture(callback):
        return capture
    return None


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Parse ETL file
    if len(sys.argv) > 1:
        etl_file = sys.argv[1]
        print(f"Parsing ETL file: {etl_file}")
        urbs = parse_etl_file(etl_file)
        print(f"Found {len(urbs)} URBs")
        for urb in urbs[:10]:  # Print first 10
            print(f"\nURB: {urb.urb_function_name}")
            print(f"  Device: {urb.vid}:{urb.pid}")
            print(f"  Endpoint: {urb.endpoint_address} ({urb.endpoint_direction})")
            print(f"  Length: {urb.transfer_buffer_length} bytes")
            print(f"  Status: {urb.status_name}")
    else:
        print("Usage: urb_capture.py <etl_file>")
        print("\nFor real-time capture, use the URBCapture class programmatically.")