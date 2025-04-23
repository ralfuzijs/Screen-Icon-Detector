"""
Dialog for editing template actions.
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class ActionEditor:
    def __init__(self, parent, action=None, action_index=None, callback=None):
        """
        Initialize the action editor dialog.
        
        Args:
            parent: The parent window
            action: The action to edit (or None for a new action)
            action_index: The index of the action in the list (or None for a new action)
            callback: Function to call with the new/updated action
        """
        self.parent = parent
        self.action = action
        self.action_index = action_index
        self.callback = callback
        
        # Create the dialog window
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Action Editor")
        self.window.geometry("500x400")
        self.window.minsize(400, 300)
        self.window.grab_set()  # Make window modal
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        # Action type selection
        type_frame = ctk.CTkFrame(self.window)
        type_frame.pack(fill="x", padx=10, pady=10)
        
        type_label = ctk.CTkLabel(type_frame, text="Action Type:")
        type_label.pack(side="left", padx=5)
        
        self.action_types = [
            "move_mouse", "click", "double_click", "type_message", 
            "press_key", "wait", "terminate_program"
        ]
        
        # Get current type if editing existing action
        current_type = ""
        if self.action:
            if isinstance(self.action, dict) and "type" in self.action:
                current_type = self.action["type"]
            else:
                current_type = self.action
        
        self.type_var = tk.StringVar(value=current_type)
        self.type_menu = ctk.CTkOptionMenu(
            type_frame, 
            variable=self.type_var, 
            values=self.action_types,
            command=self.update_param_ui
        )
        self.type_menu.pack(side="left", padx=5)
        
        # Frame for parameters
        self.param_frame = ctk.CTkFrame(self.window)
        self.param_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set up parameter variables
        self.message_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.seconds_var = tk.StringVar()
        self.button_var = tk.StringVar(value="left")
        
        # If editing existing action, populate parameters
        if self.action and isinstance(self.action, dict):
            if "message" in self.action:
                self.message_var.set(self.action["message"])
            if "key" in self.action:
                self.key_var.set(self.action["key"])
            if "seconds" in self.action:
                self.seconds_var.set(str(self.action["seconds"]))
            if "button" in self.action:
                self.button_var.set(self.action["button"])
        
        # Update UI based on selected type
        if current_type:
            self.update_param_ui(current_type)
        
        # Button frame
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        save_btn = ctk.CTkButton(button_frame, text="Save", command=self.save_action)
        save_btn.pack(side="right", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.window.destroy)
        cancel_btn.pack(side="right", padx=10)
    
    def update_param_ui(self, action_type):
        """Update parameter UI based on selected action type."""
        # Clear existing widgets
        for widget in self.param_frame.winfo_children():
            widget.destroy()
        
        # Add parameters based on action type
        if action_type == "type_message":
            msg_label = ctk.CTkLabel(self.param_frame, text="Message:")
            msg_label.pack(anchor="w", padx=10, pady=5)
            
            self.msg_entry = ctk.CTkTextbox(self.param_frame, height=100)
            self.msg_entry.pack(fill="both", expand=True, padx=10, pady=5)
            self.msg_entry.insert("1.0", self.message_var.get())
            
            # Update StringVar when text changes
            def update_message_var(event=None):
                self.message_var.set(self.msg_entry.get("1.0", "end-1c"))
            
            self.msg_entry.bind("<KeyRelease>", update_message_var)
            
        elif action_type == "press_key":
            key_label = ctk.CTkLabel(self.param_frame, text="Key:")
            key_label.pack(anchor="w", padx=10, pady=5)
            
            common_keys = [
                "enter", "tab", "space", "backspace", "escape", "up", "down", "left", "right",
                "home", "end", "pageup", "pagedown", "delete", "insert"
            ]
            
            key_menu = ctk.CTkOptionMenu(self.param_frame, variable=self.key_var, values=common_keys)
            key_menu.pack(anchor="w", padx=10, pady=5)
            
            custom_frame = ctk.CTkFrame(self.param_frame)
            custom_frame.pack(fill="x", padx=10, pady=5)
            
            custom_label = ctk.CTkLabel(custom_frame, text="Or Custom Key:")
            custom_label.pack(side="left", padx=5)
            
            self.custom_entry = ctk.CTkEntry(custom_frame)
            self.custom_entry.pack(side="left", padx=5, fill="x", expand=True)
            
            def set_custom_key():
                if self.custom_entry.get():
                    self.key_var.set(self.custom_entry.get())
            
            custom_btn = ctk.CTkButton(custom_frame, text="Set", command=set_custom_key)
            custom_btn.pack(side="right", padx=5)
            
        elif action_type == "wait":
            seconds_label = ctk.CTkLabel(self.param_frame, text="Seconds:")
            seconds_label.pack(anchor="w", padx=10, pady=5)
            
            seconds_entry = ctk.CTkEntry(self.param_frame, textvariable=self.seconds_var)
            seconds_entry.pack(anchor="w", padx=10, pady=5)
            
        elif action_type in ["click", "double_click"]:
            button_label = ctk.CTkLabel(self.param_frame, text="Mouse Button:")
            button_label.pack(anchor="w", padx=10, pady=5)
            
            button_frame = ctk.CTkFrame(self.param_frame)
            button_frame.pack(fill="x", padx=10, pady=5)
            
            for button in ["left", "right", "middle"]:
                btn_radio = ctk.CTkRadioButton(
                    button_frame, 
                    text=button, 
                    variable=self.button_var, 
                    value=button
                )
                btn_radio.pack(side="left", padx=10)
        
        elif action_type == "terminate_program":
            info_label = ctk.CTkLabel(
                self.param_frame, 
                text="This action will terminate the program when executed.\nNo additional parameters needed."
            )
            info_label.pack(anchor="w", padx=10, pady=20)
    
    def save_action(self):
        """Save the action and close the dialog."""
        action_type = self.type_var.get()
        if not action_type:
            messagebox.showwarning("Warning", "Please select an action type.")
            return
            
        new_action = {"type": action_type}
        
        # Add parameters based on action type
        if action_type == "type_message":
            new_action["message"] = self.message_var.get()
        elif action_type == "press_key":
            new_action["key"] = self.key_var.get()
        elif action_type == "wait":
            try:
                new_action["seconds"] = float(self.seconds_var.get())
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid number for seconds.")
                return
        elif action_type in ["click", "double_click"]:
            new_action["button"] = self.button_var.get()
        
        # Call the callback with the new action
        if self.callback:
            self.callback(new_action, self.action_index)
        
        # Close the window
        self.window.destroy()
