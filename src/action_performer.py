import pyautogui
import time
import random
import pyperclip  # Add this import for clipboard operations
import sys
import pandas as pd
import os

# Import the kill switch flag from main
try:
    from main import kill_switch_activated, check_kill_switch
except ImportError:
    # Fallback if main module can't be imported
    kill_switch_activated = False
    def check_kill_switch():
        return False

class ActionPerformer:
    def __init__(self, config=None):
        self.config = config or {}
        # Set default values if not provided in config
        self.smooth_move = self.config.get('smooth_mouse_movement', False)
        self.move_duration = self.config.get('mouse_move_duration', 0.5)
        self.click_delay = self.config.get('click_delay', 0.1)
        self.type_delay = self.config.get('type_delay', 0.01)
        self.post_action_delay = self.config.get('post_action_delay', 0.5)
        self.typing_method = self.config.get('typing_method', 'clipboard')  # 'clipboard' or 'character'
        
        # Store the selected monitor, will be set later
        self.selected_monitor = None
        
        # Configure pyautogui settings
        pyautogui.PAUSE = self.config.get('pyautogui_pause', 0.1)
        pyautogui.FAILSAFE = True
    
    def set_monitor(self, monitor):
        """Set the monitor to use for coordinate adjustments"""
        self.selected_monitor = monitor
        if monitor:
            print(f"Action performer will use monitor at position ({monitor['left']}, {monitor['top']})")
    
    def adjust_coordinates(self, x, y):
        """Adjust coordinates based on the selected monitor"""
        if self.selected_monitor:
            # If monitor is selected, add the monitor's offset to make coordinates global
            adjusted_x = self.selected_monitor['left'] + x
            adjusted_y = self.selected_monitor['top'] + y
            return adjusted_x, adjusted_y
        else:
            # No monitor selected, use coordinates directly
            return x, y
    
    def move_mouse(self, x, y):
        """Move the mouse to the specified coordinates, using smooth movement if configured."""
        try:
            # Check kill switch before action
            if 'check_kill_switch' in globals():
                check_kill_switch()
            
            # Adjust coordinates based on selected monitor
            adjusted_x, adjusted_y = self.adjust_coordinates(x, y)
            
            if self.smooth_move:
                # Add slight randomness for more human-like movement
                pyautogui.moveTo(
                    adjusted_x + random.uniform(-5, 5),
                    adjusted_y + random.uniform(-5, 5),
                    duration=self.move_duration
                )
            else:
                pyautogui.moveTo(adjusted_x, adjusted_y)
            
            time.sleep(self.post_action_delay)
            return True
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False
    
    def click(self, button='left', clicks=1):
        """Perform a mouse click at current position."""
        try:
            # Check kill switch before action
            if 'check_kill_switch' in globals():
                check_kill_switch()
                
            pyautogui.click(button=button, clicks=clicks)
            time.sleep(self.click_delay)
            return True
        except Exception as e:
            print(f"Error clicking: {e}")
            return False
    
    def double_click(self, button='left'):
        """Perform a double-click."""
        return self.click(button=button, clicks=2)
    
    def type_message(self, message):
        """Type a message using the configured method."""
        try:
            if not message:
                return False
            
            # Check kill switch before potentially lengthy operation
            if 'check_kill_switch' in globals():
                check_kill_switch()
            
            typing_method = self.typing_method
            
            # Use the clipboard method (faster, less visible typing)
            if typing_method == 'clipboard':
                print(f"Using clipboard method to type: {message}")
                # Save original clipboard content
                original_clipboard = pyperclip.paste()
                
                # Copy message to clipboard
                pyperclip.copy(message)
                
                # Paste the content
                pyautogui.hotkey('ctrl', 'v')
                # Wait a bit after pasting
                time.sleep(self.post_action_delay)
                
                # Restore the original clipboard content
                pyperclip.copy(original_clipboard)
                return True
            
            # Use character-by-character typing (slower, more visible typing)
            elif typing_method == 'character':
                print(f"Using character-by-character method to type: {message}")
                for char in message:
                    # Check kill switch periodically during character typing
                    if 'check_kill_switch' in globals():
                        check_kill_switch()
                    
                    # For basic ASCII characters
                    if ord(char) < 128:
                        pyautogui.write(char, interval=self.type_delay + random.uniform(-0.005, 0.005))
                    else:
                        # For special characters, use the clipboard for individual characters
                        char_clipboard = pyperclip.paste()
                        pyperclip.copy(char)
                        pyautogui.hotkey('ctrl', 'v')
                        pyperclip.copy(char_clipboard)
                    time.sleep(self.type_delay)
                
                time.sleep(self.post_action_delay)
                return True
            
            # Use a hybrid method if specified
            elif typing_method == 'hybrid':
                print(f"Using hybrid method to type: {message}")
                # First few characters typed individually for visibility
                visibility_chars = min(len(message), self.config.get('hybrid_visibility_chars', 5))
                
                # Type the first few characters slowly
                for char in message[:visibility_chars]:
                    if ord(char) < 128:
                        pyautogui.write(char, interval=self.type_delay * 2)
                    else:
                        char_clipboard = pyperclip.paste()
                        pyperclip.copy(char)
                        pyautogui.hotkey('ctrl', 'v')
                        pyperclip.copy(char_clipboard)
                    time.sleep(self.type_delay * 2)
                
                # Paste the rest if there's more
                if visibility_chars < len(message):
                    remaining = message[visibility_chars:]
                    original_clipboard = pyperclip.paste()
                    pyperclip.copy(remaining)
                    pyautogui.hotkey('ctrl', 'v')
                    pyperclip.copy(original_clipboard)
                
                time.sleep(self.post_action_delay)
                return True
            
            else:
                print(f"Unknown typing method: {typing_method}, defaulting to clipboard")
                # Default to clipboard method
                original_clipboard = pyperclip.paste()
                pyperclip.copy(message)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(self.post_action_delay)
                pyperclip.copy(original_clipboard)
                return True
            
        except Exception as e:
            print(f"Error typing message: {e}")
            return False
    
    def press_key(self, key):
        """Press a specific key (e.g., 'enter', 'tab', etc.)."""
        try:
            # Check kill switch before action
            if 'check_kill_switch' in globals():
                check_kill_switch()
                
            pyautogui.press(key)
            time.sleep(self.post_action_delay)
            return True
        except Exception as e:
            print(f"Error pressing key: {e}")
            return False
    
    def handle_excel(self, file_path, sheet_name, column_name):
        """Handle Excel file operations."""
        try:
            print(f"Excel action: Opening file {file_path}, sheet {sheet_name}, column {column_name}")
            
            # Check kill switch before potentially lengthy operation
            if 'check_kill_switch' in globals():
                check_kill_switch()
            
            # Try to find the file - check if it's a relative path
            if not os.path.isabs(file_path):
                # Try to find relative to the current working directory
                abs_path = os.path.abspath(file_path)
                if os.path.exists(abs_path):
                    file_path = abs_path
                else:
                    # Try to find relative to the script directory
                    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    abs_path = os.path.join(script_dir, file_path)
                    if os.path.exists(abs_path):
                        file_path = abs_path
            
            # Make sure the file exists
            if not os.path.exists(file_path):
                print(f"Error: Excel file not found: {file_path}")
                return False
            
            # Load the Excel file
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Check if column exists
            if column_name not in df.columns:
                print(f"Error: Column {column_name} not found in sheet {sheet_name}")
                return False
            
            # Get column values (for now we'll just print them, but you could do more)
            column_values = df[column_name].tolist()
            print(f"Found {len(column_values)} values in column {column_name}")
            
            # You could do more operations here, like:
            # - Type specific values from the column
            # - Update values in the column and save back to file
            # - Use values to drive other actions
            
            # For demonstration, we'll type the first value if it exists
            if len(column_values) > 0 and str(column_values[0]) != "nan":
                first_value = str(column_values[0])
                print(f"Typing first value from column: {first_value}")
                self.type_message(first_value)
            
            return True
            
        except Exception as e:
            print(f"Error handling Excel file: {e}")
            return False

    def perform_action(self, action_type, params=None):
        """Perform an action based on the action type and parameters."""
        # Check kill switch before action
        if 'check_kill_switch' in globals():
            check_kill_switch()
            
        if action_type == "move_mouse" and isinstance(params, tuple) and len(params) == 2:
            return self.move_mouse(params[0], params[1])
        elif action_type == "click":
            button = params.get('button', 'left') if isinstance(params, dict) else 'left'
            return self.click(button=button)
        elif action_type == "double_click":
            button = params.get('button', 'left') if isinstance(params, dict) else 'left'
            return self.double_click(button=button)
        elif action_type == "type_message" and isinstance(params, str):
            return self.type_message(params)
        elif action_type == "press_key" and isinstance(params, str):
            return self.press_key(params)
        elif action_type == "excel" and isinstance(params, dict):
            return self.handle_excel(
                params.get('file', ''),
                params.get('sheet', ''),
                params.get('column', '')
            )
        else:
            print(f"Unknown action type or invalid parameters: {action_type}")
            return False
