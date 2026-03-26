import tkinter as tk
from tkinter import ttk
import logging

from gui.pages.devices_page import DevicesPage
from gui.pages.storage_page import StoragePage
from gui.pages.timeline_page import TimelinePage
from gui.pages.analysis_page import AnalysisPage
from gui.pages.usb_behavior_page import USBBehaviorPage
from gui.pages.urb_capture_page import URBCapturePage
from gui.pages.security_page import SecurityPage
from gui.pages.export_page import ExportPage
from gui.pages.settings_page import SettingsPage
from utils.settings import load_settings

logger = logging.getLogger(__name__)

class USBForensicsApp(tk.Tk):
    """Professional USB Forensics Application with Modern Side Panel."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        self.title("USB Forensics Tool - Professional Edition")
        self.geometry("1400x900")
        self.configure(bg="#ffffff")
        
        self.resizable(True, True)
        self.settings = load_settings()
        
        # Set styles
        self._setup_styles()
        
        # Create main layout
        self._create_main_layout()
        
        logger.info("USB Forensics GUI initialized")
    
    def _setup_styles(self):
        """Setup modern styling."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Sidebar.TFrame', background='#1f2937')
        style.configure('Main.TFrame', background='#f3f4f6')
        style.configure('Sidebar.TLabel', background='#1f2937', foreground='#ffffff')
        style.configure('Header.TLabel', background='#ffffff', foreground='#1f2937', font=('Segoe UI', 14, 'bold'))
        style.configure('Title.TLabel', foreground='#1f2937', font=('Segoe UI', 12, 'bold'))
        
        # Treeview styling
        style.configure('Treeview', font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))
    
    def _create_main_layout(self):
        """Create main application layout with side panel."""
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Side panel (navigation)
        self.sidebar = ttk.Frame(main_container, style='Sidebar.TFrame', width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.sidebar.pack_propagate(False)
        
        # Content area
        self.content_area = ttk.Frame(main_container, style='Main.TFrame')
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create sidebar content
        self._create_sidebar()
        
        # Create main content pages
        self.pages = {}
        self.pages['devices'] = DevicesPage(self.content_area, self)
        self.pages['storage'] = StoragePage(self.content_area, self)
        self.pages['timeline'] = TimelinePage(self.content_area, self)
        self.pages['analysis'] = AnalysisPage(self.content_area, self)
        if self.settings.get('wireshark_enabled', False):
            self.pages['usb_behavior'] = USBBehaviorPage(self.content_area, self)
        self.pages['urb'] = URBCapturePage(self.content_area, self)
        self.pages['security'] = SecurityPage(self.content_area, self)
        self.pages['export'] = ExportPage(self.content_area, self)
        self.pages['settings'] = SettingsPage(self.content_area, self)
        
        # Show first page
        self.show_page('devices')
    
    def _create_sidebar(self):
        """Create sidebar navigation panel."""
        # Header
        header_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        header_frame.pack(fill=tk.X, padx=10, pady=20)
        
        title_label = ttk.Label(header_frame, text="📱 USB Forensics", style='Sidebar.TLabel', font=('Segoe UI', 12, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Professional Edition", style='Sidebar.TLabel', font=('Segoe UI', 9))
        subtitle_label.pack()
        
        # Separator
        sep = tk.Frame(self.sidebar, bg='#374151', height=1)
        sep.pack(fill=tk.X, padx=10, pady=10)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ('devices', '📱 All Devices', self._on_nav_devices),
            ('storage', '💾 Storage Forensics', self._on_nav_storage),
            ('timeline', '📊 Timeline', self._on_nav_timeline),
            ('analysis', '🔍 Analysis', self._on_nav_analysis),
            ('usb_behavior', '🧬 USB Behavior', self._on_nav_usb_behavior),
            ('urb', '🔌 URB Capture', self._on_nav_urb),
            ('security', '🛡️ Security', self._on_nav_security),
            ('export', '📁 Export', self._on_nav_export),
            ('settings', '⚙️ Settings', self._on_nav_settings),
        ]

        if not self.settings.get('wireshark_enabled', False):
            nav_items = [item for item in nav_items if item[0] != 'usb_behavior']
        
        for key, label, command in nav_items:
            btn_frame = tk.Frame(self.sidebar, bg='#1f2937')
            btn_frame.pack(fill=tk.X, padx=8, pady=4)
            
            btn = tk.Label(
                btn_frame, 
                text=label,
                bg='#374151',
                fg='#ffffff',
                font=('Segoe UI', 10),
                padx=15,
                pady=12,
                cursor='hand2',
                relief=tk.FLAT
            )
            btn.pack(fill=tk.X)
            btn.bind('<Button-1>', lambda e, k=key, c=command: (c(), self._update_nav_highlight(k)))
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#3b82f6'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#374151'))
            
            self.nav_buttons[key] = btn
        
        # Bottom section
        bottom_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        about_label = ttk.Label(
            bottom_frame,
            text="USB Forensics Tool v2.0\nCreated by:\n• Srirevanth A\n• Naghul Pranav C B\n• Deeekshitha",
            style='Sidebar.TLabel',
            font=('Segoe UI', 8),
            justify=tk.LEFT
        )
        about_label.pack()
    
    def _update_nav_highlight(self, page_key):
        """Update navigation button highlights."""
        for key, btn in self.nav_buttons.items():
            if key == page_key:
                btn.config(bg='#3b82f6')
            else:
                btn.config(bg='#374151')
    
    def _on_nav_devices(self):
        self.show_page('devices')
    
    def _on_nav_storage(self):
        self.show_page('storage')
    
    def _on_nav_timeline(self):
        self.show_page('timeline')
    
    def _on_nav_analysis(self):
        self.show_page('analysis')

    def _on_nav_usb_behavior(self):
        self.show_page('usb_behavior')
    
    def _on_nav_urb(self):
        self.show_page('urb')
    
    def _on_nav_security(self):
        self.show_page('security')
    
    def _on_nav_export(self):
        self.show_page('export')
    
    def _on_nav_settings(self):
        self.show_page('settings')
    
    def show_page(self, page_name):
        """Show specific page."""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
