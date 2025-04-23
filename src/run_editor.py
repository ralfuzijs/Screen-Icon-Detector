#!/usr/bin/env python3
"""
Simple launcher for the configuration editor.
This is the recommended way to run the editor.
"""
import os
import sys
import argparse

def main():
    # Parse command line arguments for monitor positioning
    parser = argparse.ArgumentParser(description="Run the Screen Icon Detector configuration editor")
    parser.add_argument("--monitor-left", type=int, help="Left position of the monitor")
    parser.add_argument("--monitor-top", type=int, help="Top position of the monitor")
    parser.add_argument("--monitor-width", type=int, help="Width of the monitor")
    parser.add_argument("--monitor-height", type=int, help="Height of the monitor")
    parser.add_argument("--monitor-index", type=int, help="Index of the monitor")
    
    args = parser.parse_args()
    
    # Get the project root directory (one level up from src folder)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Add project root to Python path
    sys.path.append(project_root)
    
    # Add src to Python path
    src_path = os.path.join(project_root, "src")
    sys.path.append(src_path)
    
    # Now import the ConfigEditor class
    from config_editor.editor_app import ConfigEditor
    
    # Default config path
    config_path = os.path.join(project_root, "scenario_default.json")
    
    print(f"Project root: {project_root}")
    print(f"Config path: {config_path}")
    
    # Create the editor
    editor = ConfigEditor(config_path)
    
    # Set monitor position information if provided
    if args.monitor_left is not None and args.monitor_top is not None:
        print(f"Positioning editor window on monitor at ({args.monitor_left}, {args.monitor_top})")
        
        # Pass full monitor information to editor
        editor.monitor_info = {
            "left": args.monitor_left,
            "top": args.monitor_top,
            "width": args.monitor_width if args.monitor_width else 1920,
            "height": args.monitor_height if args.monitor_height else 1080,
            "index": args.monitor_index if args.monitor_index is not None else 0
        }
    
    # Run the editor
    editor.run()

if __name__ == "__main__":
    main()