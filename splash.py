"""Professional splash screen for USB Forensics Tool.

Displays a professional loading screen with creators' names and tool branding.
"""
import tkinter as tk
from tkinter import font as tkfont
import time
import threading


def show_splash():
    """Display professional splash screen with creators' names."""
    root = tk.Tk()
    root.title("USB Forensics Tool")
    root.geometry("600x400")
    root.resizable(False, False)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Set dark professional background
    root.configure(bg='#1e3a8a')
    
    # Main frame
    main_frame = tk.Frame(root, bg='#1e3a8a')
    main_frame.pack(fill='both', expand=True)
    
    # Logo/Title
    title_font = tkfont.Font(family='Segoe UI', size=28, weight='bold')
    title_label = tk.Label(
        main_frame,
        text='🔍 USB Forensics Tool',
        font=title_font,
        bg='#1e3a8a',
        fg='#3b82f6'
    )
    title_label.pack(pady=(40, 10))
    
    # Subtitle
    subtitle_font = tkfont.Font(family='Segoe UI', size=12)
    subtitle_label = tk.Label(
        main_frame,
        text='Professional Edition',
        font=subtitle_font,
        bg='#1e3a8a',
        fg='#10b981'
    )
    subtitle_label.pack(pady=(0, 40))
    
    # Divider
    divider = tk.Frame(main_frame, bg='#3b82f6', height=2)
    divider.pack(fill='x', padx=40, pady=20)
    
    # Creators section
    creators_title_font = tkfont.Font(family='Segoe UI', size=11, weight='bold')
    creators_title = tk.Label(
        main_frame,
        text='Created by:',
        font=creators_title_font,
        bg='#1e3a8a',
        fg='#ffffff'
    )
    creators_title.pack(pady=(10, 15))
    
    # Creators names
    creators_font = tkfont.Font(family='Segoe UI', size=13)
    creators = [
        'Srirevanth A',
        'Naghul Pranav C B',
        'Deeekshitha'
    ]
    
    for creator in creators:
        creator_label = tk.Label(
            main_frame,
            text=f'• {creator}',
            font=creators_font,
            bg='#1e3a8a',
            fg='#fbbf24'
        )
        creator_label.pack(pady=5)
    
    # Divider 2
    divider2 = tk.Frame(main_frame, bg='#3b82f6', height=2)
    divider2.pack(fill='x', padx=40, pady=20)
    
    # Loading message
    loading_font = tkfont.Font(family='Segoe UI', size=10, slant='italic')
    loading_label = tk.Label(
        main_frame,
        text='Loading Professional Edition...',
        font=loading_font,
        bg='#1e3a8a',
        fg='#9ca3af'
    )
    loading_label.pack(pady=(20, 10))
    
    # Progress bar (simple animated dots)
    progress_font = tkfont.Font(family='Segoe UI', size=12)
    progress_label = tk.Label(
        main_frame,
        text='●○○',
        font=progress_font,
        bg='#1e3a8a',
        fg='#3b82f6'
    )
    progress_label.pack(pady=(0, 20))
    
    # Animate progress
    def animate_progress():
        states = ['●○○', '●●○', '●●●']
        for state in states * 2:
            progress_label.config(text=state)
            root.update()
            time.sleep(0.3)
    
    # Show splash and animate
    root.update()
    animate_progress()
    
    # Close splash after animation
    root.destroy()


def show_splash_async(callback=None):
    """Show splash screen in a thread and optionally call callback when done."""
    def splash_thread():
        show_splash()
        if callback:
            callback()
    
    thread = threading.Thread(target=splash_thread, daemon=True)
    thread.start()


if __name__ == '__main__':
    show_splash()
