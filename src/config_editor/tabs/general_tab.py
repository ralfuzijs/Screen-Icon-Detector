"""
General settings tab for the config editor.
"""
import tkinter as tk
import customtkinter as ctk

class GeneralTab:
    def __init__(self, parent, config):
        """
        Initialize the general settings tab.
        
        Args:
            parent: The parent container (CTkTabview tab)
            config: The configuration dictionary
        """
        self.parent = parent
        self.config = config
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the general tab UI."""
        # Create a frame for the content
        content_frame = ctk.CTkFrame(self.parent)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a title
        title = ctk.CTkLabel(content_frame, text="General Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)
        
        # Create a scrollable frame for settings
        settings_frame = ctk.CTkScrollableFrame(content_frame)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Screenshot interval
        interval_frame = ctk.CTkFrame(settings_frame)
        interval_frame.pack(fill="x", padx=5, pady=5)
        
        interval_label = ctk.CTkLabel(interval_frame, text="Screenshot Interval (seconds):")
        interval_label.pack(side="left", padx=5)
        
        self.interval_var = tk.StringVar(value=str(self.config.get("screenshot_interval", 10)))
        interval_entry = ctk.CTkEntry(interval_frame, textvariable=self.interval_var, width=100)
        interval_entry.pack(side="left", padx=5)
        
        # Max loops
        loops_frame = ctk.CTkFrame(settings_frame)
        loops_frame.pack(fill="x", padx=5, pady=5)
        
        loops_label = ctk.CTkLabel(loops_frame, text="Maximum Loops (0 for unlimited):")
        loops_label.pack(side="left", padx=5)
        
        self.loops_var = tk.StringVar(value=str(self.config.get("max_loops", 0)))
        loops_entry = ctk.CTkEntry(loops_frame, textvariable=self.loops_var, width=100)
        loops_entry.pack(side="left", padx=5)
        
        # Visualizer enabled
        vis_frame = ctk.CTkFrame(settings_frame)
        vis_frame.pack(fill="x", padx=5, pady=5)
        
        vis_label = ctk.CTkLabel(vis_frame, text="Visualizer Enabled:")
        vis_label.pack(side="left", padx=5)
        
        self.vis_var = tk.BooleanVar(value=self.config.get("visualizer_enabled", False))
        vis_check = ctk.CTkCheckBox(vis_frame, text="", variable=self.vis_var)
        vis_check.pack(side="left", padx=5)
        
        # Show failed matches
        failed_frame = ctk.CTkFrame(settings_frame)
        failed_frame.pack(fill="x", padx=5, pady=5)
        
        failed_label = ctk.CTkLabel(failed_frame, text="Show Failed Matches:")
        failed_label.pack(side="left", padx=5)
        
        self.failed_var = tk.BooleanVar(value=self.config.get("show_failed_matches", True))
        failed_check = ctk.CTkCheckBox(failed_frame, text="", variable=self.failed_var)
        failed_check.pack(side="left", padx=5)
        
        # Process one template per iteration
        process_frame = ctk.CTkFrame(settings_frame)
        process_frame.pack(fill="x", padx=5, pady=5)
        
        process_label = ctk.CTkLabel(process_frame, text="Process One Template Per Iteration:")
        process_label.pack(side="left", padx=5)
        
        self.process_var = tk.BooleanVar(value=self.config.get("process_one_template_per_iteration", False))
        process_check = ctk.CTkCheckBox(process_frame, text="", variable=self.process_var)
        process_check.pack(side="left", padx=5)
    
    def update_config(self):
        """Update config with current UI values."""
        try:
            self.config["screenshot_interval"] = int(self.interval_var.get())
            self.config["max_loops"] = int(self.loops_var.get())
            self.config["visualizer_enabled"] = self.vis_var.get()
            self.config["show_failed_matches"] = self.failed_var.get()
            self.config["process_one_template_per_iteration"] = self.process_var.get()
            return True
        except (ValueError, AttributeError) as e:
            print(f"Error updating general settings: {e}")
            return False
