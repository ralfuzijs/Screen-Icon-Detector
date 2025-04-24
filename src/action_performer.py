import pyautogui
import time
import random
import pyperclip  # Add this import for clipboard operations
import sys
import pandas as pd
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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

        # Dictionary to store Excel data between actions
        self.excel_memory = {}
    
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
    
    def scroll_wheel(self, direction, amount=1):
        """Perform a mouse wheel scroll in the specified direction."""
        try:
            # Check kill switch before action
            if 'check_kill_switch' in globals():
                check_kill_switch()
                
            # PyAutoGUI uses positive for up, negative for down
            # But it's more intuitive to specify "up" or "down" explicitly
            scroll_value = amount if direction == "up" else -amount
            
            print(f"Scrolling {direction} by {amount} clicks")
            pyautogui.scroll(scroll_value)
            time.sleep(self.post_action_delay)
            return True
        except Exception as e:
            print(f"Error scrolling wheel: {e}")
            return False
    
    def handle_excel(self, file_path, sheet_name, column_name, start_row=1, end_row=None, 
                    use_last_filled=False, mode="extract_data", target_column=""):
        """
        Handle Excel file operations with enhanced functionality:
        - Extract data range from Excel to memory
        - Perform Google searches on stored data
        - Write search results back to Excel
        """
        try:
            # Find Excel file
            full_path = self.find_excel_file(file_path)
            if not os.path.exists(full_path):
                print(f"Error: Excel file not found: {file_path}")
                return False
            
            # Load the Excel file
            df = pd.read_excel(full_path, sheet_name=sheet_name)
            
            # Check if column exists
            if column_name not in df.columns:
                print(f"Error: Column {column_name} not found in sheet {sheet_name}")
                return False
            
            # Adjust for 1-based indexing (Excel rows start at 1, pandas at 0)
            start_idx = start_row - 1
            
            # Find last filled entry if needed
            if use_last_filled:
                # Find the last non-NaN value in the column
                valid_indices = df.index[df[column_name].notna()].tolist()
                if valid_indices:
                    end_idx = max(valid_indices)
                else:
                    end_idx = start_idx  # Default to start if no valid entries
            else:
                end_idx = (end_row - 1) if end_row is not None else (len(df) - 1)
            
            # Make sure indices are within bounds
            start_idx = max(0, min(start_idx, len(df) - 1))
            end_idx = max(start_idx, min(end_idx, len(df) - 1))
            
            # Create key for this data set
            memory_key = f"{file_path}_{sheet_name}_{column_name}_{start_row}_to_{end_idx + 1}"
            
            # Process based on mode
            if mode == "extract_data":
                # Extract values from specified range
                values = df.iloc[start_idx:end_idx+1][column_name].tolist()
                # Filter out NaN values
                values = [str(val) for val in values if pd.notna(val)]
                
                # Store values in memory
                self.excel_memory[memory_key] = values
                
                print(f"Extracted {len(values)} values from column {column_name} (rows {start_row} to {end_idx + 1})")
                
                # Display first few values for debug
                if values:
                    preview = values[:3]
                    if len(values) > 3:
                        preview.append("...")
                    print(f"Preview: {preview}")
                
                return True
                
            elif mode == "first_row_only":
                # Just process the first row
                if len(df) > start_idx and pd.notna(df.iloc[start_idx][column_name]):
                    value = str(df.iloc[start_idx][column_name])
                    print(f"Processing single value: {value}")
                    self.type_message(value)
                return True
                
            elif mode == "search_data":
                # Check if we have data in memory
                if memory_key not in self.excel_memory or not self.excel_memory[memory_key]:
                    print(f"No data found in memory for {memory_key}. Run an 'extract_data' action first.")
                    return False
                
                # Check if target column exists
                if target_column not in df.columns:
                    print(f"Error: Target column {target_column} not found in sheet {sheet_name}")
                    return False
                
                # Get the stored values
                values = self.excel_memory[memory_key]
                
                # Perform Google search for each value and store results
                search_results = []
                
                for i, value in enumerate(values):
                    try:
                        print(f"Searching for: {value}")
                        result = self.google_search(value)
                        search_results.append(result)
                        
                        # Add a small delay between searches to avoid rate limiting
                        if i < len(values) - 1:
                            time.sleep(random.uniform(1, 2))
                    except Exception as e:
                        print(f"Error searching for '{value}': {e}")
                        search_results.append(f"Error: {str(e)}")
                
                # Write results back to Excel
                for i, result in enumerate(search_results):
                    row_idx = start_idx + i
                    if row_idx <= end_idx:
                        df.at[row_idx, target_column] = result
                
                # Save the updated Excel file
                df.to_excel(full_path, sheet_name=sheet_name, index=False)
                print(f"Updated {len(search_results)} search results in column {target_column}")
                
                return True
            
            else:
                print(f"Unknown Excel mode: {mode}")
                return False
                
        except Exception as e:
            print(f"Error handling Excel file: {e}")
            return False
    
    def find_excel_file(self, file_path):
        """Find an Excel file by checking multiple locations."""
        # Get project directory
        project_dir = os.path.dirname(os.path.dirname(__file__))
        
        # Check relative to project root
        abs_path = os.path.join(project_dir, file_path)
        if os.path.exists(abs_path):
            return abs_path
        
        # Check in excel_files folder
        excel_folder_path = os.path.join(project_dir, "excel_files", os.path.basename(file_path))
        if os.path.exists(excel_folder_path):
            return excel_folder_path
        
        # Default to original path
        return file_path
    
    def google_search(self, query):
        """Perform a Google search and return the top result."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Format the search query
            search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            # Send the request
            response = requests.get(search_url, headers=headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to find the first search result
            first_result = soup.select_one(".yuRUbf a")
            if first_result:
                title = first_result.select_one("h3")
                url = first_result["href"]
                
                if title:
                    return f"{title.text} - {url}"
                return url
                
            # Alternative approach if the first selector doesn't work
            search_results = soup.select(".tF2Cxc")
            if search_results:
                for result in search_results:
                    link = result.select_one("a")
                    if link and link.has_attr("href"):
                        title_element = result.select_one("h3")
                        title = title_element.text if title_element else "No title"
                        return f"{title} - {link['href']}"
            
            return "No results found"
            
        except Exception as e:
            print(f"Error during Google search: {e}")
            return f"Error: {str(e)}"

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
        elif action_type == "scroll_wheel" and isinstance(params, dict):
            direction = params.get('direction', 'down')
            amount = params.get('amount', 1)
            return self.scroll_wheel(direction, amount)
        elif action_type == "excel" and isinstance(params, dict):
            return self.handle_excel(
                params.get('file', ''),
                params.get('sheet', ''),
                params.get('column', ''),
                params.get('start_row', 1),
                params.get('end_row', None),
                params.get('use_last_filled', False),
                params.get('mode', 'extract_data'),
                params.get('target_column', '')
            )
        else:
            print(f"Unknown action type or invalid parameters: {action_type}")
            return False
