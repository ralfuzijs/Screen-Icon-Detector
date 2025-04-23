"""
Configuration management functions for loading and saving config files.
"""
import os
import json
import glob
from tkinter import messagebox

def load_config(config_path):
    """Load the configuration from the JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        print(f"Config loaded from {config_path}")
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        messagebox.showerror("Error", f"Failed to load configuration: {e}")
        return {}

def save_config(config, config_path, show_message=True):
    """
    Save the configuration to the JSON file.
    
    Args:
        config: Configuration dictionary to save
        config_path: Path to save the configuration to
        show_message: Whether to show a success message (default: True)
    """
    try:
        # Create a backup of the current config
        backup_path = f"{config_path}.backup"
        try:
            with open(config_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"Backup created at {backup_path}")
        except Exception as backup_e:
            print(f"Warning: Could not create backup: {backup_e}")
        
        # Save the updated config - ensure consistent formatting and ordering
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=2, sort_keys=False)
        
        print(f"Config saved to {config_path}")
        
        # Only show the success message if requested
        if show_message:
            messagebox.showinfo("Success", "Configuration saved successfully!")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        messagebox.showerror("Error", f"Failed to save configuration: {e}")
        return False

def find_scenario_files(base_dir, current_config_path):
    """Find all scenario JSON files in the base directory."""
    try:
        # Look for scenario_*.json files in the base directory
        scenario_pattern = os.path.join(base_dir, "scenario_*.json")
        scenario_files = glob.glob(scenario_pattern)
        
        # Get just the filenames
        scenario_files = [os.path.basename(f) for f in scenario_files]
        
        # Debug print
        print(f"Found scenario files in {base_dir}: {scenario_files}")
        
        if not scenario_files:
            # Fallback to just the current file if no scenario files found
            current_name = os.path.basename(current_config_path)
            scenario_files = [current_name]
            print(f"No scenario files found, using current file: {current_name}")
            
        return scenario_files
    except Exception as e:
        print(f"Error finding scenario files: {e}")
        # Fallback to default scenario
        return ["scenario_default.json"]