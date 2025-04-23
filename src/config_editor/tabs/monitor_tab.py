"""
Monitor settings tab for the config editor.
"""
import tkinter as tk
import customtkinter as ctk
from ..utils.monitor_utils import get_available_monitors

class MonitorTab:
    def __init__(self, parent, config):
        """
        Initialize the monitor settings tab.
        
        Args:
            parent: The parent container (CTkTabview tab)
            config: The configuration dictionary
        """
        self.parent = parent
        self.config = config
        
        # Get monitor settings from config
        self.monitor_settings = self.config.get("monitor_settings", {})
        self.enable_selection = self.monitor_settings.get("enable_monitor_selection", True)
        self.default_index = self.monitor_settings.get("default_monitor_index", 0)
        
        # Store the original index for later reference
        self.original_monitor_index = self.default_index
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the monitor tab UI."""
        # Create a frame for the content
        content_frame = ctk.CTkFrame(self.parent)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a title
        title = ctk.CTkLabel(content_frame, text="Monitor Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)
        
        # Create a scrollable frame for settings
        settings_frame = ctk.CTkScrollableFrame(content_frame)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Enable monitor selection
        enable_frame = ctk.CTkFrame(settings_frame)
        enable_frame.pack(fill="x", padx=5, pady=5)
        
        enable_label = ctk.CTkLabel(enable_frame, text="Enable Monitor Selection:")
        enable_label.pack(side="left", padx=5)
        
        self.enable_monitor_var = tk.BooleanVar(value=self.enable_selection)
        enable_check = ctk.CTkCheckBox(enable_frame, text="", variable=self.enable_monitor_var)
        enable_check.pack(side="left", padx=5)
        
        # Get available monitors
        self.monitors = get_available_monitors()
        
        # Available monitors section
        monitors_frame = ctk.CTkFrame(settings_frame)
        monitors_frame.pack(fill="x", padx=5, pady=5)
        
        monitors_label = ctk.CTkLabel(monitors_frame, text="Available Monitors:", anchor="w")
        monitors_label.pack(fill="x", padx=5, pady=2)
        
        self.monitors_listbox = tk.Listbox(monitors_frame, bg="#2a2d2e", fg="white", 
                                      selectbackground="#1f6aa5", highlightthickness=0, height=4)
        self.monitors_listbox.pack(fill="x", padx=5, pady=5)
        
        # Populate monitors listbox
        for i, monitor in enumerate(self.monitors):
            self.monitors_listbox.insert(tk.END, 
                            f"Monitor {i}: {monitor['width']}x{monitor['height']} at ({monitor['left']}, {monitor['top']})")
        
        # Monitor selection callback
        def on_monitor_select(event):
            if self.monitors_listbox.curselection():
                selected_idx = self.monitors_listbox.curselection()[0]
                self.monitor_index_var.set(str(selected_idx))
        
        self.monitors_listbox.bind('<<ListboxSelect>>', on_monitor_select)
        
        # Default monitor index
        monitor_frame = ctk.CTkFrame(settings_frame)
        monitor_frame.pack(fill="x", padx=5, pady=5)
        
        monitor_label = ctk.CTkLabel(monitor_frame, text="Default Monitor Index:")
        monitor_label.pack(side="left", padx=5)
        
        self.monitor_index_var = tk.StringVar(value=str(self.default_index))
        monitor_entry = ctk.CTkEntry(monitor_frame, textvariable=self.monitor_index_var, width=100)
        monitor_entry.pack(side="left", padx=5)
        
        monitor_info = ctk.CTkLabel(monitor_frame, text="(0 = primary monitor, 1 = secondary, etc.)")
        monitor_info.pack(side="left", padx=5)
        
        # Callback for enable/disable checkbox
        def toggle_monitor_selection():
            if not self.enable_monitor_var.get():
                # Save the current index before disabling
                try:
                    self.original_monitor_index = int(self.monitor_index_var.get())
                except ValueError:
                    self.original_monitor_index = 0
            else:
                # Restore the original index
                self.monitor_index_var.set(str(self.original_monitor_index))
        
        enable_check.configure(command=toggle_monitor_selection)
    
    def update_config(self):
        """Update config with current UI values."""
        try:
            monitor_index = int(self.monitor_index_var.get())
            if monitor_index >= 0:
                if "monitor_settings" not in self.config:
                    self.config["monitor_settings"] = {}
                
                self.config["monitor_settings"]["enable_monitor_selection"] = self.enable_monitor_var.get()
                self.config["monitor_settings"]["default_monitor_index"] = monitor_index
            return True
        except (ValueError, AttributeError) as e:
            print(f"Error updating monitor settings: {e}")
            return False
