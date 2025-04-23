"""
Matching settings tab for the config editor.
"""
import tkinter as tk
import customtkinter as ctk

class MatchingTab:
    def __init__(self, parent, config):
        """
        Initialize the matching settings tab.
        
        Args:
            parent: The parent container (CTkTabview tab)
            config: The configuration dictionary
        """
        self.parent = parent
        self.config = config
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the matching tab UI."""
        # Create a frame for the content
        content_frame = ctk.CTkFrame(self.parent)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a title
        title = ctk.CTkLabel(content_frame, text="Matching Settings", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)
        
        # Create a scrollable frame for settings
        settings_frame = ctk.CTkScrollableFrame(content_frame)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Match threshold
        threshold_frame = ctk.CTkFrame(settings_frame)
        threshold_frame.pack(fill="x", padx=5, pady=5)
        
        threshold_label = ctk.CTkLabel(threshold_frame, text="Match Threshold:")
        threshold_label.pack(side="left", padx=5)
        
        self.threshold_var = tk.StringVar(value=str(self.config.get("match_threshold", 0.75)))
        threshold_entry = ctk.CTkEntry(threshold_frame, textvariable=self.threshold_var, width=100)
        threshold_entry.pack(side="left", padx=5)
        
        threshold_info = ctk.CTkLabel(threshold_frame, text="(0.0 to 1.0, higher = more strict)")
        threshold_info.pack(side="left", padx=5)
        
        # Distance threshold
        distance_frame = ctk.CTkFrame(settings_frame)
        distance_frame.pack(fill="x", padx=5, pady=5)
        
        distance_label = ctk.CTkLabel(distance_frame, text="Match Distance Threshold (pixels):")
        distance_label.pack(side="left", padx=5)
        
        self.distance_var = tk.StringVar(value=str(self.config.get("match_distance_pixels_threshold", 50)))
        distance_entry = ctk.CTkEntry(distance_frame, textvariable=self.distance_var, width=100)
        distance_entry.pack(side="left", padx=5)
    
    def update_config(self):
        """Update config with current UI values."""
        try:
            threshold = float(self.threshold_var.get())
            if 0 <= threshold <= 1:
                self.config["match_threshold"] = threshold
                
            distance = int(self.distance_var.get())
            if distance > 0:
                self.config["match_distance_pixels_threshold"] = distance
            return True
        except (ValueError, AttributeError) as e:
            print(f"Error updating matching settings: {e}")
            return False
