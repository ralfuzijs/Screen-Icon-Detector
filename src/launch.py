#!/usr/bin/env python3
"""
Launch script that runs just the automation (main.py) component.

This script:
1. Detects available monitors
2. Updates the configuration to use the default monitor
3. Runs the automation program
"""
import os
import sys
import json
import subprocess
import time
import platform
import argparse
from mss import mss
import threading
import importlib.util
import glob

# Check if required modules are available
def check_module_exists(module_name):
    return importlib.util.find_spec(module_name) is not None

# Import the output window if customtkinter is available
output_window_module = None
if check_module_exists("customtkinter"):
    try:
        from output_window import create_output_redirect_window
        output_window_available = True
    except ImportError:
        output_window_available = False
else:
    output_window_available = False

def get_monitors():
    """Get available monitors"""
    with mss() as sct:
        monitors = sct.monitors
    
    # First entry is a combined view of all monitors
    return monitors[1:]

def select_automation_monitor(monitors):
    """Automatically select the first monitor for automation"""
    # No longer ask user for input, just use the first monitor (index 0)
    print(f"Using monitor 1: {monitors[0]['width']}x{monitors[0]['height']} at position ({monitors[0]['left']}, {monitors[0]['top']})")
    return 0

def update_config_with_monitor(monitor_index):
    """Update the default scenario config with the selected monitor"""
    # Get the base directory (two levels up from this file)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the default scenario config
    config_path = os.path.join(base_dir, "scenario_default.json")
    
    try:
        # Load the config
        with open(config_path, 'r', encoding='utf-8') as file:
            config = json.load(file)
        
        # Update the monitor settings
        if "monitor_settings" not in config:
            config["monitor_settings"] = {}
        
        config["monitor_settings"]["enable_monitor_selection"] = True
        config["monitor_settings"]["default_monitor_index"] = monitor_index
        
        # Save the config
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=2, sort_keys=False)
        
        return True
    except Exception as e:
        print(f"Error updating config: {e}")
        return False

def select_scenario():
    """Let the user select which scenario to use"""
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find all scenario files (scenario_*.json)
    scenario_pattern = os.path.join(base_dir, "scenario_*.json")
    scenario_files = glob.glob(scenario_pattern)
    
    if not scenario_files:
        print("\nNo scenarios found.")
        print(f"Expected to find scenario_*.json files in: {base_dir}")
        return None
    
    print("\nAvailable scenarios:")
    for i, filepath in enumerate(scenario_files):
        filename = os.path.basename(filepath)
        # Extract the name without the prefix and extension
        name = filename.replace("scenario_", "").replace(".json", "")
        print(f"{i+1}. {name} ({filename})")
    
    selection = 0
    while selection < 1 or selection > len(scenario_files):
        try:
            selection = int(input(f"\nSelect a scenario (1-{len(scenario_files)}): "))
        except ValueError:
            print("Please enter a valid number")
    
    # Return the selected scenario file name
    return os.path.basename(scenario_files[selection-1])

def launch_automation(scenario=None, use_output_window=True):
    """Launch the automation program with optional scenario."""
    try:
        # Get the base directory (two levels up from this file)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Build the command to run the main.py script - properly quote the path
        python_exe = sys.executable
        main_script = os.path.join(base_dir, "src", "main.py")
        
        # Build command list
        cmd = [python_exe, main_script]
        
        if scenario:
            cmd.extend(["--scenario", scenario])
        
        # Check if we can use the GUI output window
        if output_window_available and use_output_window:
            try:
                # Get available monitors
                monitors = get_monitors()
                
                # Default to monitor 0 for automation, which means use monitor 1 for output
                automation_monitor_index = 0
                
                # Try to read the monitor settings from the scenario file
                if scenario:
                    scenario_path = os.path.join(base_dir, scenario)
                    if os.path.exists(scenario_path):
                        with open(scenario_path, 'r', encoding='utf-8') as file:
                            config = json.load(file)
                            if "monitor_settings" in config and config["monitor_settings"].get("enable_monitor_selection", False):
                                automation_monitor_index = config["monitor_settings"].get("default_monitor_index", 0)
                
                # Determine which monitor to use for the output window
                output_monitor_index = None
                if len(monitors) > 1:  # Only if we have multiple monitors
                    # If automation is on monitor 0, use monitor 1 for output window
                    # If automation is on any other monitor, use monitor 0 for output window
                    output_monitor_index = 1 if automation_monitor_index == 0 else 0
                    
                    print(f"Automation running on monitor {automation_monitor_index+1}, output window on monitor {output_monitor_index+1}")
                
                # Get output monitor information if available
                output_monitor = monitors[output_monitor_index] if output_monitor_index is not None and output_monitor_index < len(monitors) else None
                
                # Create output window with correct monitor info
                output_window, original_stdout = create_output_redirect_window(monitor_info=output_monitor)
                
                # For single monitor setup, minimize the output window
                if len(monitors) <= 1:
                    output_window.root.iconify()
                
                # Print initial message
                print("Starting automation process...\n")
                
                # Function to run the process and handle its output
                def run_process():
                    try:
                        # For Windows, use direct module import instead of subprocess to avoid path issues
                        if platform.system() == "Windows":
                            print(f"Directly importing main module to avoid Windows path issues...")
                            
                            # Add src directory to path if not already there
                            src_dir = os.path.join(base_dir, "src")
                            if src_dir not in sys.path:
                                sys.path.append(src_dir)
                            
                            # Save original argv
                            original_argv = sys.argv.copy()
                            
                            # Set up argv for the main module
                            sys.argv = [main_script]
                            if scenario:
                                sys.argv.extend(["--scenario", scenario])
                            
                            try:
                                # Import the main module
                                import importlib.util
                                spec = importlib.util.spec_from_file_location("main", main_script)
                                main_module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(main_module)
                                
                                # Run main function
                                main_module.main()
                            except Exception as e:
                                print(f"Error running main module: {e}")
                                import traceback
                                traceback.print_exc()
                            finally:
                                # Restore original argv
                                sys.argv = original_argv
                        else:
                            # Non-Windows systems can continue to use subprocess
                            # Use shell=True on Windows to avoid command window popup
                            use_shell = False
                            
                            # Start process with unbuffered output and specific environment variables
                            # to disable Python's output buffering
                            env = os.environ.copy()
                            env['PYTHONUNBUFFERED'] = '1'
                            
                            # Print the exact command being executed for debugging
                            print(f"Executing: {' '.join(cmd)}")
                            
                            process = subprocess.Popen(
                                cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=0,  # Unbuffered
                                universal_newlines=True,
                                shell=use_shell,
                                env=env
                            )
                            
                            # Force window update before starting the output loop
                            output_window.root.update()
                            
                            # Use a simpler method that processes lines directly
                            for line in iter(process.stdout.readline, ''):
                                if line:
                                    # Write directly to the output window
                                    output_window.direct_write(line)
                                    # Force UI update after each line
                                    output_window.force_update()
                            
                            # Wait for process to terminate
                            process.wait()
                        
                        # Process completion
                        print("\nAutomation process completed.")
                        
                        # Restore original stdout when done
                        sys.stdout = original_stdout
                    except Exception as e:
                        print(f"Error in automation process: {e}")
                        import traceback
                        traceback.print_exc()
                
                # Start the process in a separate thread
                process_thread = threading.Thread(target=run_process, daemon=True)
                process_thread.start()
                
                # Start the output window main loop
                output_window.start()
            
            except Exception as e:
                print(f"Error setting up output window: {e}")
        else:
            # Fallback for when output window isn't available or not requested
            if platform.system() == "Windows":
                # For Windows, use direct module import instead of subprocess
                src_dir = os.path.join(base_dir, "src")
                if src_dir not in sys.path:
                    sys.path.append(src_dir)
                
                # Save original argv
                original_argv = sys.argv.copy()
                
                # Set up argv for the main module
                sys.argv = [main_script]
                if scenario:
                    sys.argv.extend(["--scenario", scenario])
                
                try:
                    # Import the main module
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("main", main_script)
                    main_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(main_module)
                    
                    # Run main function
                    main_module.main()
                except Exception as e:
                    print(f"Error running main module: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    # Restore original argv
                    sys.argv = original_argv
            else:
                # Non-Windows systems can continue to use subprocess
                subprocess.run(cmd)
                
        return True
    except Exception as e:
        print(f"Error launching automation: {e}")
        return False

def launch_full_application(scenario=None, debug=False):
    """Launch the application with optional scenario."""
    print(f"Launching application...")
    
    # Get monitors
    monitors = get_monitors()
    
    # If monitors detected, automatically use the default monitor
    if monitors:
        # Step 1: Automatically select the default monitor
        automation_monitor_index = select_automation_monitor(monitors)
        
        # Update the config file to use this monitor
        update_config_with_monitor(automation_monitor_index)
        
        # Step 2: If no scenario was specified via command line, select scenario in terminal
        if not scenario:
            scenario = select_scenario()
            if not scenario:
                print("No scenario selected. Using default.")
        
        # Step 3: Only now launch automation with the output window
        print(f"Starting with scenario: {scenario}")
        launch_automation(scenario, use_output_window=True)
    else:
        # No monitors detected
        print("No monitors detected. Running in fallback mode.")
        
        # If no scenario was specified via command line, select scenario in terminal
        if not scenario:
            scenario = select_scenario()
            if not scenario:
                print("No scenario selected. Using default.")
        
        # Launch automation with selected scenario
        launch_automation(scenario, use_output_window=True)
    
    return True

def check_scenario_exists(scenario_name):
    """Check if a specific scenario exists in the project directory."""
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check for scenario with and without the "scenario_" prefix
    scenario_paths = [
        os.path.join(base_dir, f"scenario_{scenario_name}.json"),
        os.path.join(base_dir, f"{scenario_name}.json")
    ]
    
    # If scenario_name already has the prefix, also check directly
    if scenario_name.startswith("scenario_"):
        scenario_paths.append(os.path.join(base_dir, f"{scenario_name}.json"))
    
    # Check if any of the possible paths exist
    for path in scenario_paths:
        if os.path.exists(path):
            print(f"Scenario found: {os.path.basename(path)}")
            return True
            
    print(f"Scenario not found: {scenario_name}")
    return False

def list_available_scenarios():
    """List all available scenarios."""
    # Get the base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Find all scenario files (scenario_*.json)
    scenario_pattern = os.path.join(base_dir, "scenario_*.json")
    scenario_files = glob.glob(scenario_pattern)
    
    if scenario_files:
        print("\nAvailable scenarios:")
        for i, filepath in enumerate(scenario_files):
            filename = os.path.basename(filepath)
            # Extract the name without the prefix and extension
            name = filename.replace("scenario_", "").replace(".json", "")
            print(f"{i+1}. {name} ({filename})")
    else:
        print("\nNo scenarios found.")
        print(f"Expected to find scenario_*.json files in: {base_dir}")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Screen Icon Detector - Launch Control")
    
    # Main action groups (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("--check-scenario", metavar="SCENARIO_NAME", 
                             help="Check if a specific scenario exists")
    action_group.add_argument("--list-scenarios", action="store_true",
                             help="List all available scenarios")
    action_group.add_argument("--automation-only", action="store_true",
                             help="Launch just the automation component")
    action_group.add_argument("--editor-only", action="store_true",
                             help="Launch just the editor component")
    
    # Additional options
    parser.add_argument("--scenario", metavar="SCENARIO_NAME",
                       help="Specify a scenario to load (when launching full app)")
    parser.add_argument("--config", metavar="CONFIG_FILE",
                       help="Specify a custom configuration file")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug mode")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")
    parser.add_argument("--version", action="store_true",
                       help="Show version information")
    
    args = parser.parse_args()

    # Handle version request
    if args.version:
        print("Screen Icon Detector v1.0.0")
        return 0
        
    # Handle scenario checks
    if args.check_scenario:
        return 0 if check_scenario_exists(args.check_scenario) else 1
    
    if args.list_scenarios:
        list_available_scenarios()
        return 0
    
    # Handle --editor-only option
    if args.editor_only:
        # Import the editor functions
        from config_editor import run_editor
        # Launch the editor with default scenario
        run_editor()
        return 0
    
    # Launch component
    if args.automation_only:
        # When using automation-only, don't show the GUI window
        # This allows for CLI usage with terminal-only output
        launch_automation(args.scenario, use_output_window=False)
        return 0
    
    # Default: launch automation application with GUI window
    launch_full_application(scenario=args.scenario, debug=args.debug)
    return 0

if __name__ == "__main__":
    sys.exit(main())
