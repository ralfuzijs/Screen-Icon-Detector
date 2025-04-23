"""
Main configuration editor application.
"""
import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from .config_manager import load_config, save_config, find_scenario_files
from .tabs.general_tab import GeneralTab
from .tabs.templates_tab import TemplatesTab
from .tabs.matching_tab import MatchingTab
from .tabs.monitor_tab import MonitorTab

class ConfigEditor:
    def __init__(self, config_path):
        """
        Initialize the configuration editor.
        
        Args:
            config_path: Path to the configuration file
        """
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_path = config_path
        self.config = load_config(config_path)
        
        # Find all available scenario files
        self.scenario_files = find_scenario_files(self.base_dir, config_path)
        self.current_scenario = os.path.basename(config_path)
        
        # For scenario switching
        self.next_scenario = None
        
        # Apply the saved appearance mode before setting up UI
        self.apply_saved_appearance_mode()
        
        # Tab references
        self.tabs = {}
        
        # Set up the UI
        self.setup_ui()
    
    def apply_saved_appearance_mode(self):
        """Apply the saved appearance mode from config."""
        # Default to Light if not specified
        saved_mode = self.config.get("appearance_mode", "Light")
        
        # Only accept valid values
        if saved_mode not in ["Light", "Dark"]:
            saved_mode = "Light"
            
        # Apply the appearance mode
        ctk.set_appearance_mode(saved_mode)
        print(f"Applied saved appearance mode: {saved_mode}")
    
    def switch_scenario(self, scenario_filename):
        """Switch to a different scenario configuration file."""
        if scenario_filename == self.current_scenario:
            return  # Already using this scenario
        
        # Save the current configuration to the CURRENT file path before switching
        if self.update_config_from_ui():
            save_config(self.config, self.config_path, show_message=False)
        
        # Update config path AFTER saving the current config
        new_path = os.path.join(self.base_dir, scenario_filename)
        self.config_path = new_path
        self.current_scenario = scenario_filename
        
        # Load the new configuration from the new path
        self.config = load_config(new_path)
        
        # Destroy existing widgets in tabs (keep the main window)
        for tab in self.tabs.values():
            # If tab has a parent attribute (the tab container)
            if hasattr(tab, 'parent'):
                for widget in tab.parent.winfo_children():
                    widget.destroy()
        
        # Rebuild the tabs with the new configuration
        self.tabs = {}
        self.tabs["general"] = GeneralTab(self.tabview.tab("General"), self.config)
        self.tabs["templates"] = TemplatesTab(self.tabview.tab("Templates"), self.config, self.base_dir)
        self.tabs["matching"] = MatchingTab(self.tabview.tab("Matching"), self.config)
        self.tabs["monitor"] = MonitorTab(self.tabview.tab("Monitor"), self.config)
        
        # Update the window title to reflect the new scenario
        self.root.title(f"Screen Icon Detector - {scenario_filename}")
        
        print(f"Switched to scenario: {scenario_filename}")
    
    def setup_ui(self):
        """Set up the main UI window and components."""
        # Set up the theme
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("Screen Icon Detector - Configuration Editor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Add window close protocol to handle proper shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add scenario selector in top left and appearance mode selector in top right
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(side="top", fill="x", padx=10, pady=(10, 0))
        
        # Left side - Scenario selector
        scenario_frame = ctk.CTkFrame(header_frame)
        scenario_frame.pack(side="left", fill="x", padx=10)
        
        scenario_label = ctk.CTkLabel(scenario_frame, text="Scenario:")
        scenario_label.pack(side="left", padx=5)
        
        scenario_var = tk.StringVar(value=self.current_scenario)
        scenario_menu = ctk.CTkOptionMenu(
            scenario_frame,
            values=self.scenario_files,
            variable=scenario_var,
            command=self.switch_scenario
        )
        scenario_menu.pack(side="left", padx=5)
        
        # Right side - Appearance mode
        appearance_frame = ctk.CTkFrame(header_frame)
        appearance_frame.pack(side="right", fill="x", padx=10)
        
        appearance_label = ctk.CTkLabel(appearance_frame, text="Appearance Mode:")
        appearance_label.pack(side="left", padx=5)
        
        def change_appearance_mode(new_appearance_mode):
            ctk.set_appearance_mode(new_appearance_mode)
        
        appearance_mode_menu = ctk.CTkOptionMenu(
            appearance_frame, 
            values=["Light", "Dark"],  # Removed "System" option
            command=change_appearance_mode
        )
        appearance_mode_menu.pack(side="left", padx=5)
        appearance_mode_menu.set(ctk.get_appearance_mode())  # Set to current mode
        
        # Create a tabview for different sections
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        general_tab = self.tabview.add("General")
        templates_tab = self.tabview.add("Templates")
        matching_tab = self.tabview.add("Matching")
        monitor_tab = self.tabview.add("Monitor")
        
        # Initialize tab modules
        self.tabs["general"] = GeneralTab(general_tab, self.config)
        self.tabs["templates"] = TemplatesTab(templates_tab, self.config, self.base_dir)
        self.tabs["matching"] = MatchingTab(matching_tab, self.config)
        self.tabs["monitor"] = MonitorTab(monitor_tab, self.config)
        
        # Add save/reset buttons at the bottom
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(fill="x", padx=10, pady=10)
        
        self.save_button = ctk.CTkButton(
            self.button_frame, 
            text="Save Scenario", 
            command=self.save_config,
            fg_color="green"
        )
        self.save_button.pack(side="right", padx=10)
        
        self.save_run_button = ctk.CTkButton(
            self.button_frame, 
            text="Save & Run Scenario", 
            command=self.save_and_run,
            fg_color="blue"
        )
        self.save_run_button.pack(side="right", padx=10)
        
        self.reset_button = ctk.CTkButton(
            self.button_frame, 
            text="Reset to Saved", 
            command=self.reset_config
        )
        self.reset_button.pack(side="right", padx=10)
    
    def on_closing(self):
        """Handle window close event."""
        # Simply close without asking to save changes
        self.root.destroy()
        self.next_scenario = None  # Ensure we don't try to reload
    
    def check_for_unsaved_changes(self):
        """Check if there are unsaved changes."""
        # This is a simplified check - in a real app, you might want to compare
        # the current config with the saved one to determine if changes were made
        return True  # For now, always ask to save
    
    def update_config_from_ui(self):
        """Update config with values from all UI elements."""
        # Update from each tab
        for tab_name, tab in self.tabs.items():
            if not tab.update_config():
                print(f"Warning: Failed to update config from {tab_name} tab")
        
        # Save the current appearance mode
        self.config["appearance_mode"] = ctk.get_appearance_mode()
        
        return True
    
    def save_config(self):
        """Save the current configuration to the JSON file."""
        # Update config with current UI values before saving
        if self.update_config_from_ui():
            return save_config(self.config, self.config_path)
        return False
    
    def reset_config(self):
        """Reset the UI to match the saved configuration."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all changes?"):
            # Reload config and recreate UI
            self.config = load_config(self.config_path)
            self.root.destroy()
            self.setup_ui()
    
    def save_and_run(self):
        """Save the current configuration and run the scenario."""
        if self.save_config():
            self.run_scenario()

    def run_scenario(self):
        """Run the current scenario using the main.py script."""
        try:
            import subprocess
            import sys

            # Make sure the templates directory exists
            templates_dir = os.path.join(self.base_dir, "templates")
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)
                print(f"Created templates directory: {templates_dir}")

            # Get the path to the main.py script
            main_script_path = os.path.join(self.base_dir, "src", "main.py")

            if not os.path.exists(main_script_path):
                messagebox.showerror("Error", f"Main script not found at: {main_script_path}")
                return False

            # Get the path to the Python executable
            python_exe = sys.executable

            # Run the script in a new process
            print(f"Running scenario: {self.current_scenario} with {main_script_path}")

            # Create a pop-up to show that the scenario is running
            messagebox.showinfo("Running Scenario", 
                                f"Running scenario: {self.current_scenario}\n\n"
                                "The main script is now running in a separate process.\n"
                                "Check the terminal for output.")

            # Start the process
            subprocess.Popen([python_exe, main_script_path])

            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run scenario: {e}")
            print(f"Error running scenario: {e}")
            return False
    
    def run(self):
        """Run the config editor application."""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error in main loop: {e}")
