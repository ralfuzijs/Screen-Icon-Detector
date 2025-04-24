import cv2
import numpy as np
from template_matcher import TemplateMatcher
from visualizer import display_results
from action_performer import ActionPerformer
from monitor_option import get_monitors, select_monitor
import os
import sys
import pyautogui
import time
import json
import keyboard
import threading
import signal
from PIL import Image
from mss import mss
import argparse
from config_editor.config_manager import find_scenario_files

# Global kill switch flag
kill_switch_activated = False
# Global monitor selection
selected_monitor = None

def setup_kill_switch():
    """Setup a global kill switch (Ctrl+Esc) to stop the program from anywhere."""
    def on_kill_switch():
        global kill_switch_activated
        print("\n*** Kill switch activated! Program stopping... ***")
        kill_switch_activated = True
        
    # Register the keyboard hotkey for Ctrl+Esc
    keyboard.add_hotkey('ctrl+esc', on_kill_switch)
    print("Kill switch ready: Press Ctrl+Esc to stop the program at any time")

def check_kill_switch():
    """Check if kill switch has been activated and exit if it has."""
    if kill_switch_activated:
        print("Exiting due to kill switch activation...")
        # Clean shutdown
        keyboard.unhook_all()
        # Exit with a non-zero code to indicate it wasn't a normal termination
        sys.exit(1)

def capture_screenshot(output_path=None, delay=3.0):
    """Capture a screenshot and optionally save it to the specified path."""
    # Check kill switch before potentially lengthy operation
    check_kill_switch()
    
    # Add a delay before taking the screenshot
    print(f"Waiting for {delay} seconds before capturing screenshot...")
    time.sleep(delay)
    
    # Move cursor to center of screen BEFORE taking screenshot
    # This helps avoid hover effects when searching for icons
    try:
        global selected_monitor
        
        if selected_monitor:
            # Calculate center of the selected monitor
            center_x = selected_monitor['left'] + selected_monitor['width'] // 2
            center_y = selected_monitor['top'] + selected_monitor['height'] // 2
        else:
            # Get screen size
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2
            
        # Move cursor to center of screen/monitor
        pyautogui.moveTo(center_x, center_y, duration=0.2)
        print(f"Cursor reset to center ({center_x}, {center_y})")
    except Exception as e:
        print(f"Error resetting cursor position: {e}")
    
    # Small delay to ensure cursor movement is complete
    time.sleep(0.1)
    
    # Now take the screenshot
    if selected_monitor:
        # Use mss to capture the specific monitor
        with mss() as sct:
            # Capture the selected monitor
            screenshot_mss = sct.grab(selected_monitor)
            # Convert to PIL Image
            screenshot = Image.frombytes("RGB", screenshot_mss.size, screenshot_mss.bgra, "raw", "BGRX")
    else:
        # Capture the entire screen using pyautogui
        screenshot = pyautogui.screenshot()
    
    if output_path:
        screenshot.save(output_path)
    
    # Convert PIL image to OpenCV format
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def load_config(base_dir, scenario_file=None):
    """Load configuration from the specified scenario file or select from available scenarios."""
    try:
        # If no scenario file specified, find available ones
        if scenario_file is None:
            available_scenarios = find_scenario_files(base_dir, os.path.join(base_dir, "scenario_default.json"))
            
            # If only one scenario file exists, use it
            if len(available_scenarios) == 1:
                scenario_file = available_scenarios[0]
                print(f"Using the only available scenario: {scenario_file}")
            # Otherwise, let user select
            else:
                print("\nAvailable scenario files:")
                for i, file in enumerate(available_scenarios):
                    print(f"{i+1}. {file}")
                
                try:
                    selection = int(input("\nSelect scenario number (or press Enter for default): ") or 1) - 1
                    if 0 <= selection < len(available_scenarios):
                        scenario_file = available_scenarios[selection]
                    else:
                        scenario_file = "scenario_default.json"
                        print(f"Invalid selection. Using default scenario.")
                except ValueError:
                    scenario_file = "scenario_default.json"
                    print(f"Invalid input. Using default scenario.")
        
        config_path = os.path.join(base_dir, scenario_file)
        print(f"Loading configuration from: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config, scenario_file
    except Exception as e:
        print(f"Error loading configuration: {e}")
        # As a fallback, try loading the default scenario
        if scenario_file != "scenario_default.json":
            print("Trying to fall back to default scenario...")
            default_path = os.path.join(base_dir, "scenario_default.json")
            with open(default_path, 'r') as f:
                return json.load(f), "scenario_default.json"
        else:
            raise

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Screen Icon Detector')
    parser.add_argument('--scenario', type=str, help='Scenario file to use (e.g., scenario_1.json)')
    args = parser.parse_args()
    
    # Get base directory
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load configuration with specified or selected scenario file
    config, active_scenario = load_config(base_dir, args.scenario)
    
    # Setup the kill switch at program start
    setup_kill_switch()
    
    # Handle monitor selection based on configuration 
    global selected_monitor
    monitor_settings = config.get('monitor_settings', {})
    enable_monitor_selection = monitor_settings.get('enable_monitor_selection', False)
    
    if enable_monitor_selection:
        # Get available monitors
        monitors = get_monitors()
        
        # Get monitor index from configuration
        default_index = monitor_settings.get('default_monitor_index', 0)
        
        # Check if the index is valid
        if 0 <= default_index < len(monitors):
            selected_monitor = monitors[default_index]
            print(f"Using monitor {default_index+1}: {selected_monitor['width']}x{selected_monitor['height']} at position ({selected_monitor['left']}, {selected_monitor['top']})")
        else:
            print(f"Invalid monitor_index {default_index} in scenario_default.json (found {len(monitors)} monitors). Using full screen.")
    else:
        print("Monitor selection disabled in scenario_default.json. Using full screen.")
    
    # Template and screenshot directories
    templates_dir = os.path.normpath(os.path.join(base_dir, 'templates'))
    screenshots_dir = os.path.normpath(os.path.join(base_dir, 'screenshots'))
    
    # Get default template matching methods and thresholds from config
    default_template_methods = config.get('default_template_methods', config.get('template_methods', ['TM_CCOEFF_NORMED']))
    threshold = config.get('match_threshold', 0.8)
    distance_pixels_threshold = config.get('match_distance_pixels_threshold', 50)
    
    # Load templates with their specific methods and actions
    templates_config = config['templates']
    template_matchers = {}
    template_actions = {}  # Store actions for each template path
    template_enabled = {}  # Store enabled status for each template
    template_dependencies = {}  # Store dependencies between templates
    template_order = []  # Preserve template order from config
    template_names = {}  # Store template names indexed by path for dependency lookup

    # Handle the new template format (list of objects with path and methods)
    if templates_config and isinstance(templates_config[0], dict):
        for template_config in templates_config:
            # Extract template path(s) - handle both single and multiple paths
            template_paths = []
            
            # Handle the 'paths' format (list of paths)
            if "paths" in template_config and isinstance(template_config["paths"], list):
                for path in template_config["paths"]:
                    if isinstance(path, str):
                        norm_path = os.path.normpath(os.path.join(base_dir, path))
                        template_paths.append(norm_path)
            
            # Handle the deprecated 'path' format (single string or list)
            elif "path" in template_config:
                if isinstance(template_config["path"], str):
                    # Single path as string
                    norm_path = os.path.normpath(os.path.join(base_dir, template_config["path"]))
                    template_paths.append(norm_path)
                elif isinstance(template_config["path"], list) and len(template_config["path"]) > 0:
                    # 'path' incorrectly contains a list - use first element
                    if isinstance(template_config["path"][0], str):
                        norm_path = os.path.normpath(os.path.join(base_dir, template_config["path"][0]))
                        template_paths.append(norm_path)
            
            # Skip if no valid paths found
            if not template_paths:
                print(f"Warning: Template {template_config.get('name', 'Unknown')} has no valid paths, skipping.")
                continue
            
            # Store template name 
            template_name = template_config.get("name", os.path.basename(template_paths[0]))
            
            # Use template-specific methods if provided, otherwise use default methods
            template_methods = template_config.get('methods', default_template_methods)
            
            # Create a matcher for each path and store in template_matchers
            for template_path in template_paths:
                template_matchers[template_path] = TemplateMatcher(
                    template_path, 
                    template_methods, 
                    threshold,
                    distance_pixels_threshold
                )
                
                # Store template name for later dependency resolution
                template_names[template_path] = template_name
            
            # Only store the first path in template_order to avoid duplicates
            # This ensures each template is processed only once in the main loop
            template_order.append(template_paths[0])
            
            # Store actions, enabled status, and dependencies for all paths
            for path in template_paths:
                template_actions[path] = template_config.get('actions', [])
                template_enabled[path] = template_config.get('enabled', True)
                if 'depends_on' in template_config:
                    template_dependencies[path] = template_config['depends_on']
                elif len(template_order) > 1:
                    # Default to previous template if no dependency specified
                    template_dependencies[path] = template_names.get(template_order[-2], "")
    # Handle the old template format (list of strings)
    else:
        for template_path in templates_config:
            template_path = os.path.normpath(os.path.join(base_dir, template_path))
            template_matchers[template_path] = TemplateMatcher(
                template_path, 
                default_template_methods, 
                threshold,
                distance_pixels_threshold
            )
            
            # For backward compatibility - get actions from the old 'actions' object
            template_name = os.path.basename(template_path)
            template_actions[template_path] = config.get('actions', {}).get(template_name, [])
    
    if not template_matchers:
        print("No templates found in the configuration.")
        sys.exit(1)
    
    # DO NOT resolve dependencies to paths - keep them as names
    # We want to reference dependency relationships by template name, not by specific path
    
    # Initialize action performer and pass the selected monitor
    action_performer = ActionPerformer(config.get('action_settings', {}))
    action_performer.set_monitor(selected_monitor)  # Pass the selected monitor

    max_loops = config.get('max_loops', 0)
    loop_count = 0
    
    # Check if any template is disabled and print information
    any_disabled = any(not enabled for enabled in template_enabled.values())
    if any_disabled:
        print("\nTemplate Status:")
        for template in template_order:
            template_name = template_names.get(template, os.path.basename(template))
            status = "Enabled" if template_enabled[template] else "Disabled"
            print(f"  - {template_name}: {status}")
        print("")

    # Keep track of executed template names (not paths)
    executed_template_names = set()

    # Main program loop
    try:
        while max_loops == 0 or loop_count < max_loops:
            # Check if the maximum number of loops has been reached
            loop_count += 1

            # Check for kill switch activation at the start of each iteration
            check_kill_switch()
            
            # Capture a new screenshot at the beginning of each iteration
            screenshot_path = os.path.normpath(os.path.join(screenshots_dir, 'current_screenshot.png'))
            screenshot = capture_screenshot(screenshot_path)
            
            # Flag to track if any template was matched in this iteration
            template_matched = False
            
            # Flag to track if we should stop after current template
            stop_after_current = False
            
            # Process templates in the order defined in the config
            for template in template_order:
                # Get current template name
                template_name = template_names[template]
                
                # Skip if template is disabled
                if not template_enabled[template]:
                    print(f"Skipping disabled template: {template_name}")
                    continue
                
                # Check for dependencies using template names, not paths
                if template in template_dependencies and template_dependencies[template]:
                    depends_on_name = template_dependencies[template]
                    
                    # Check if dependency template name has been executed
                    if depends_on_name not in executed_template_names:
                        print(f"Skipping template due to unsatisfied dependency: {template_name} (needs {depends_on_name})")
                        stop_after_current = True
                        break
                
                # Find all paths for this template name
                template_paths = [p for p, n in template_names.items() if n == template_name]
                
                # Try each path until we find a match
                match_found = False
                for path in template_paths:
                    template_matcher = template_matchers[path]
                    
                    # Check kill switch before each template matching operation
                    check_kill_switch()
                    
                    match_coordinates, match_results = template_matcher.match_template(screenshot)
                    
                    if match_coordinates:
                        template_matched = True
                        match_found = True
                        print(f"Matched template: {template_name} (using {os.path.basename(path)})")
                        
                        # Display the results only if visualizer is enabled
                        if config.get('visualizer_enabled', True):
                            display_results(screenshot, match_coordinates, match_results, template_name, selected_monitor)
                        
                        # Perform actions based on the match and get updated screenshot
                        screenshot = perform_actions(
                            screenshot_path, 
                            match_coordinates, 
                            template_actions.get(path, []),
                            action_performer,
                            screenshots_dir
                        )
                        
                        # Add this template's name to executed templates
                        executed_template_names.add(template_name)
                        
                        break  # Exit the path loop once a match is found
                
                # If none of the paths matched
                if not match_found:
                    print(f"No match found for template: {template_name}")
                    if config.get('visualizer_enabled', True) and config.get('show_failed_matches', False):
                        # Optionally show failed matches
                        display_results(screenshot, None, match_results, template_name, selected_monitor)
                
                # Break after the first template is matched and actions are performed
                if match_found and config.get('process_one_template_per_iteration', True):
                    break
            
            # Stop the program if a disabled template was encountered or a dependency failed
            if stop_after_current:
                print("Stopping program due to disabled template or dependency failure")
                break
                
            # If no template was matched, wait for the specified interval
            if not template_matched:
                # Use a shorter sleep interval to check kill switch more frequently
                interval = config['screenshot_interval']
                for _ in range(int(interval)):
                    time.sleep(1)
                    check_kill_switch()
    
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        # Clean up resources
        keyboard.unhook_all()
        print("Program terminated.")

def perform_actions(screenshot_path, match_coordinates, actions, action_performer, screenshots_dir):
    """
    Execute actions defined in the config for a matched template.
    Captures a new screenshot after click or double-click actions.
    Returns the latest screenshot.
    """
    x, y, w, h = match_coordinates
    center_x, center_y = x + w // 2, y + h // 2
    
    # Use the current screenshot path for saving updated screenshots
    current_screenshot = cv2.imread(screenshot_path)
    
    for action in actions:
        # Check kill switch before each action
        check_kill_switch()
        
        # Handle string action types (backward compatibility)
        if isinstance(action, str):
            if action == "move_mouse":
                action_performer.move_mouse(center_x, center_y)
            elif action == "click":
                action_performer.click()
                # Capture a new screenshot after click
                current_screenshot = capture_screenshot(screenshot_path)
            elif action == "double_click":
                action_performer.double_click()
                # Capture a new screenshot after double-click
                current_screenshot = capture_screenshot(screenshot_path)
        
        # Handle dictionary action types (new format with parameters)
        elif isinstance(action, dict) and 'type' in action:
            action_type = action['type']
            
            if action_type == "move_mouse":
                action_performer.move_mouse(center_x, center_y)
            elif action_type == "click":
                action_performer.click(action.get('button', 'left'))
                # Capture a new screenshot after click
                current_screenshot = capture_screenshot(screenshot_path)
            elif action_type == "double_click":
                action_performer.double_click(action.get('button', 'left'))
                # Capture a new screenshot after double-click
                current_screenshot = capture_screenshot(screenshot_path)
            elif action_type == "type_message":
                action_performer.type_message(action.get('message', ''))
            elif action_type == "press_key":
                action_performer.press_key(action.get('key', 'enter'))
            elif action_type == "wait":
                wait_seconds = float(action.get('seconds', 1.0))
                print(f"Waiting for {wait_seconds} seconds...")
                time.sleep(wait_seconds)
            elif action_type == "terminate_program":
                kill_switch_activated = True
                return False
            elif action_type == "excel":
                action_performer.handle_excel(
                    action.get('file', ''),
                    action.get('sheet', ''),
                    action.get('column', '')
                )

    return current_screenshot

if __name__ == "__main__":
    main()