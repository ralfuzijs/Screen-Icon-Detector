"""
Custom output window for displaying automation results in a user-friendly way.
"""
import os
import sys
import queue
import threading
import time
import customtkinter as ctk
from tkinter import scrolledtext
import keyboard

class OutputWindow:
    def __init__(self, title="Screen Icon Detector - Automation", width=500, height=300, monitor_info=None):
        """Initialize the output window."""
        # Set up the theme
        ctk.set_default_color_theme("blue")
        
        # Create the main window with forced small size
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.minsize(500, 300)  # Smaller minimum size
        self.root.resizable(True, True)
        
        # First set a small fixed geometry to make proper centering possible
        self.root.geometry(f"{width}x{height}")
        
        # Update to calculate proper window size
        self.root.update_idletasks()
        
        # Calculate position based on monitor info if provided, otherwise center on primary monitor
        win_width = width
        win_height = height
        
        if monitor_info is not None:
            # Position on specified monitor - ensure we have valid data
            try:
                # Get monitor info directly from dict (handle both MSS format and custom dict format)
                mon_left = int(monitor_info.get('left', 0))
                mon_top = int(monitor_info.get('top', 0))
                mon_width = int(monitor_info.get('width', self.root.winfo_screenwidth()))
                mon_height = int(monitor_info.get('height', self.root.winfo_screenheight()))
                
                # Center on the specified monitor
                pos_x = mon_left + (mon_width - win_width) // 2
                pos_y = mon_top + (mon_height - win_height) // 2
                
                # Apply geometry and force an immediate update
                self.root.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
                self.root.update()
                
                print(f"Output window positioned on monitor at ({mon_left}, {mon_top}) with dimensions {mon_width}x{mon_height}")
            except (TypeError, ValueError) as e:
                print(f"Error positioning window on monitor: {e}, using default positioning")
                # Fall back to default positioning
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                pos_x = (screen_width - win_width) // 2
                pos_y = (screen_height - win_height) // 2
                self.root.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
        else:
            # Default center on primary monitor
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            pos_x = (screen_width - win_width) // 2
            pos_y = (screen_height - win_height) // 2
            self.root.geometry(f"{win_width}x{win_height}+{pos_x}+{pos_y}")
            print("Output window: No monitor info provided. Centering on primary monitor.")
        
        # Bring window to top
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        
        # Create a frame for the header
        header_frame = ctk.CTkFrame(self.root)
        header_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        # Add a status label
        self.status_label = ctk.CTkLabel(
            header_frame, 
            text="Status: Running", 
            font=("Arial", 16, "bold"),
            text_color="green"
        )
        self.status_label.pack(side="left", padx=10)
        
        # Add a kill switch button
        self.kill_button = ctk.CTkButton(
            header_frame,
            text="STOP (Ctrl+Esc)",
            command=self.activate_kill_switch,
            fg_color="red",
            hover_color="darkred",
            font=("Arial", 14, "bold")
        )
        self.kill_button.pack(side="right", padx=10)
        
        # Create a text widget to display output
        self.output_text = scrolledtext.ScrolledText(
            self.root, 
            wrap='word',
            bg='#2b2b2b',
            fg='#ffffff',
            font=('Consolas', 11)
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Queue for storing output data
        self.output_queue = queue.Queue()
        
        # Flag to track if kill switch was activated
        self.kill_switch_activated = False
        
        # Set up the protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the queue processing
        self.process_queue()
    
    def write(self, text):
        """Write text to the queue (used for redirecting stdout)."""
        self.output_queue.put(text)
        # Force an update to show text immediately
        self.root.after(1, self.process_immediate)
    
    def direct_write(self, text):
        """Write text directly to the output widget, bypassing the queue.
        This method ensures immediate display of text for real-time output.
        """
        # Execute in the main thread to avoid threading issues
        def update_text():
            # Highlight template matches and important messages
            if "Matched template" in text:
                self.output_text.tag_config("match", foreground="lime green")
                self.output_text.insert("end", text, "match")
            elif "Error" in text or "Failed" in text:
                self.output_text.tag_config("error", foreground="red")
                self.output_text.insert("end", text, "error")
            elif "Kill switch activated" in text:
                self.output_text.tag_config("kill", foreground="orange")
                self.output_text.insert("end", text, "kill")
                self.status_label.configure(text="Status: Stopping...", text_color="orange")
            else:
                self.output_text.insert("end", text)
            
            # Auto-scroll to the bottom
            self.output_text.see("end")
            # Explicitly force update
            self.force_update()
        
        # Schedule in main thread and execute right away
        self.root.after(0, update_text)
    
    def force_update(self):
        """Force immediate UI updates"""
        try:
            self.root.update()
        except Exception:
            # Ignore any update errors that might occur
            pass
    
    def process_immediate(self):
        """Process one item from the queue immediately."""
        try:
            if not self.output_queue.empty():
                text = self.output_queue.get_nowait()
                
                # Highlight template matches and important messages
                if "Matched template" in text:
                    self.output_text.tag_config("match", foreground="lime green")
                    self.output_text.insert("end", text, "match")
                elif "Error" in text or "Failed" in text:
                    self.output_text.tag_config("error", foreground="red")
                    self.output_text.insert("end", text, "error")
                elif "Kill switch activated" in text:
                    self.output_text.tag_config("kill", foreground="orange")
                    self.output_text.insert("end", text, "kill")
                    self.status_label.configure(text="Status: Stopping...", text_color="orange")
                else:
                    self.output_text.insert("end", text)
                
                # Auto-scroll to the bottom
                self.output_text.see("end")
                
                # Force update
                self.root.update_idletasks()
        except Exception as e:
            print(f"Error processing immediate output: {e}")
    
    def flush(self):
        """Need this for compatibility with stdout."""
        # Force UI update when flush is called
        self.root.update_idletasks()
    
    def process_queue(self):
        """Process the queue and update the text widget."""
        try:
            # Process items without blocking the UI
            count = 0
            while not self.output_queue.empty() and count < 20:  # Process in small batches
                text = self.output_queue.get_nowait()
                count += 1
                
                # Highlight template matches and important messages
                if "Matched template" in text:
                    self.output_text.tag_config("match", foreground="lime green")
                    self.output_text.insert("end", text, "match")
                elif "Error" in text or "Failed" in text:
                    self.output_text.tag_config("error", foreground="red")
                    self.output_text.insert("end", text, "error")
                elif "Kill switch activated" in text:
                    self.output_text.tag_config("kill", foreground="orange")
                    self.output_text.insert("end", text, "kill")
                    self.status_label.configure(text="Status: Stopping...", text_color="orange")
                else:
                    self.output_text.insert("end", text)
                
                # Auto-scroll to the bottom
                self.output_text.see("end")
                
            # If we processed any items, force an update
            if count > 0:
                self.root.update_idletasks()
                
        except Exception as e:
            print(f"Error processing queue: {e}")
            
        # Schedule the next check - more frequent updates
        self.root.after(5, self.process_queue)
    
    def activate_kill_switch(self):
        """Activate the kill switch by simulating Ctrl+Esc keypress."""
        self.kill_button.configure(state="disabled")
        self.status_label.configure(text="Status: Stopping...", text_color="orange")
        self.kill_switch_activated = True
        # Simulate the kill switch key combination
        keyboard.press_and_release('ctrl+esc')
        
    def on_closing(self):
        """Handle window closing event."""
        if not self.kill_switch_activated:
            self.activate_kill_switch()
        # Give some time for cleanup before destroying the window
        self.root.after(1000, self.root.destroy)
    
    def start(self):
        """Start the output window main loop."""
        self.root.mainloop()

def create_output_redirect_window(monitor_info=None):
    """Create and return an output window that redirects stdout."""
    # If monitor_info is explicitly provided, use it
    # Otherwise, try to determine which monitor to use based on the scenario file
    if monitor_info is None:
        try:
            import os
            import json
            from mss import mss
            
            # Get the project base directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Default scenario file path
            scenario_path = os.path.join(base_dir, "scenario_default.json")
            
            # Check if the scenario file exists
            if not os.path.exists(scenario_path):
                print("Default scenario file not found. Using default monitor placement.")
            else:
                # Read the scenario file to get the monitor settings
                with open(scenario_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Get monitor settings
                monitor_settings = config.get("monitor_settings", {})
                enable_selection = monitor_settings.get("enable_monitor_selection", True)
                
                if enable_selection:
                    # Get the monitor index from the config
                    automation_monitor_index = monitor_settings.get("default_monitor_index", 0)
                    
                    # Get available monitors
                    with mss() as sct:
                        # First monitor (index 0) in mss is the "all monitors" view, so we skip it
                        all_monitors = sct.monitors[1:]
                    
                    # If there are at least 2 monitors, use the opposite monitor
                    if len(all_monitors) > 1:
                        # If automation is on monitor 0, use monitor 1 for output window
                        # If automation is on any other monitor, use monitor 0 for output window
                        output_monitor_index = 0 if automation_monitor_index != 0 else 1
                        
                        monitor_info = all_monitors[output_monitor_index]
                        print(f"Automation using monitor {automation_monitor_index}, output window using monitor {output_monitor_index}")
        except Exception as e:
            print(f"Error determining monitor for output window: {e}. Using default.")
    
    # Now create the output window with the determined monitor info
    output_window = OutputWindow(monitor_info=monitor_info)
    
    # Save original stdout
    original_stdout = sys.stdout
    
    # Redirect stdout to our output window
    sys.stdout = output_window
    
    return output_window, original_stdout

if __name__ == "__main__":
    # For testing
    window = OutputWindow()
    sys.stdout = window
    
    def test_output():
        print("Starting test output...")
        for i in range(10):
            print(f"Test line {i}")
            time.sleep(0.5)
        print("Matched template: test.png")
        print("Error: Something went wrong")
        print("Kill switch activated! Program stopping...")
    
    threading.Thread(target=test_output).start()
    window.start()
