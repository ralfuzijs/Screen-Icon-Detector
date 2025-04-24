"""
Dialog for editing template actions.
"""
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from tkinter import filedialog
import pandas as pd
import os

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
        
        # Initialize variables for Excel action
        self.excel_mode_var = tk.StringVar(value="search_data")  # Default mode
        self.excel_start_row_var = None
        self.excel_end_row_var = None
        self.excel_use_last_filled_var = None
        self.excel_target_column_var = None

        # Initialize variables for scrollwheel action
        self.scroll_direction_var = tk.StringVar(value="down")
        self.scroll_amount_var = tk.StringVar(value="1")
        
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
            "press_key", "wait", "terminate_program", "excel", "scroll_wheel"
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
        
        # Frame for parameters - replace with scrollable frame
        self.param_frame = ctk.CTkScrollableFrame(self.window)
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
    
    def find_excel_file(self, file_path):
        """
        Find an Excel file by checking multiple locations.
        Returns the valid file path if found, otherwise returns the original path.
        """
        # If absolute path and exists, return it
        if os.path.isabs(file_path) and os.path.exists(file_path):
            return file_path
            
        # Get project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Check relative to project root
        abs_path = os.path.join(project_dir, file_path)
        if os.path.exists(abs_path):
            return abs_path
            
        # Check in excel_files folder
        excel_folder_path = os.path.join(project_dir, "excel_files", os.path.basename(file_path))
        if os.path.exists(excel_folder_path):
            return excel_folder_path
            
        # If file contains path separators, try just the basename in excel_files
        if os.path.dirname(file_path):
            simple_path = os.path.join(project_dir, "excel_files", os.path.basename(file_path))
            if os.path.exists(simple_path):
                return simple_path
                
        # Return original if not found
        return file_path
    
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
        
        elif action_type == "excel":
            # Initialize variables for Excel action
            self.excel_file_var = tk.StringVar(value=self.action.get("file", "") if self.action and "file" in self.action else "")
            self.excel_sheet_var = tk.StringVar(value=self.action.get("sheet", "") if self.action and "sheet" in self.action else "")
            self.excel_column_var = tk.StringVar(value=self.action.get("column", "") if self.action and "column" in self.action else "")
            self.sheets_list = []
            self.columns_list = []
            
            # File selection
            file_frame = ctk.CTkFrame(self.param_frame)
            file_frame.pack(fill="x", padx=10, pady=5)
            
            file_label = ctk.CTkLabel(file_frame, text="Excel File:")
            file_label.pack(side="left", padx=5)
            
            file_entry = ctk.CTkEntry(file_frame, textvariable=self.excel_file_var, width=200)
            file_entry.pack(side="left", padx=5, fill="x", expand=True)
            
            def browse_file():
                # Get the path to the excel_files folder
                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                excel_dir = os.path.join(project_dir, "excel_files")
                
                # Create the folder if it doesn't exist
                if not os.path.exists(excel_dir):
                    os.makedirs(excel_dir, exist_ok=True)
                
                file_path = filedialog.askopenfilename(
                    title="Select Excel File",
                    filetypes=[("Excel files", "*.xlsx;*.xls"), ("All files", "*.*")],
                    initialdir=excel_dir  # Set initial directory to excel_files folder
                )
                
                if file_path:
                    # Always use the excel_files folder reference format
                    file_name = os.path.basename(file_path)
                    rel_path = os.path.join("excel_files", file_name)
                    
                    # Set the path and load sheets
                    self.excel_file_var.set(rel_path)
                    self.load_excel_sheets()
            
            browse_button = ctk.CTkButton(file_frame, text="Browse", command=browse_file)
            browse_button.pack(side="right", padx=5)
            
            # Sheet selection
            sheet_frame = ctk.CTkFrame(self.param_frame)
            sheet_frame.pack(fill="x", padx=10, pady=5)
            
            sheet_label = ctk.CTkLabel(sheet_frame, text="Sheet:")
            sheet_label.pack(side="left", padx=5)
            
            self.sheet_menu = ctk.CTkOptionMenu(
                sheet_frame,
                variable=self.excel_sheet_var,
                values=[""],
                command=self.load_excel_columns
            )
            self.sheet_menu.pack(side="left", padx=5, fill="x", expand=True)
            
            # Add a cell selection header
            cell_header_frame = ctk.CTkFrame(self.param_frame)
            cell_header_frame.pack(fill="x", padx=10, pady=(10, 0))
            
            cell_header = ctk.CTkLabel(cell_header_frame, text="Cell Selection:", font=ctk.CTkFont(weight="bold"))
            cell_header.pack(anchor="w", padx=5)
            
            cell_info = ctk.CTkLabel(cell_header_frame, text="Select the cell to edit by choosing a column and row number")
            cell_info.pack(anchor="w", padx=5, pady=(0, 5))
            
            # Column selection
            column_frame = ctk.CTkFrame(self.param_frame)
            column_frame.pack(fill="x", padx=10, pady=5)
            
            column_label = ctk.CTkLabel(column_frame, text="Column:")
            column_label.pack(side="left", padx=5)
            
            self.column_menu = ctk.CTkOptionMenu(
                column_frame,
                variable=self.excel_column_var,
                values=[""]
            )
            self.column_menu.pack(side="left", padx=5, fill="x", expand=True)
            
            # Row range selection
            row_frame = ctk.CTkFrame(self.param_frame)
            row_frame.pack(fill="x", padx=10, pady=5)
            
            # Start row input
            start_row_label = ctk.CTkLabel(row_frame, text="Start Row:")
            start_row_label.pack(side="left", padx=5)
            
            self.excel_start_row_var = tk.StringVar(
                value=str(self.action.get("start_row", "1")) if self.action and "start_row" in self.action else "1"
            )
            start_row_entry = ctk.CTkEntry(row_frame, textvariable=self.excel_start_row_var, width=60)
            start_row_entry.pack(side="left", padx=5)
            
            # End row input
            end_row_label = ctk.CTkLabel(row_frame, text="End Row:")
            end_row_label.pack(side="left", padx=5)
            
            self.excel_end_row_var = tk.StringVar(
                value=str(self.action.get("end_row", "5")) if self.action and "end_row" in self.action else "5"
            )
            end_row_entry = ctk.CTkEntry(row_frame, textvariable=self.excel_end_row_var, width=60)
            end_row_entry.pack(side="left", padx=5)
            
            # Checkbox for "last filled entry"
            self.excel_use_last_filled_var = tk.BooleanVar(
                value=self.action.get("use_last_filled", False) if self.action else False
            )
            use_last_filled_checkbox = ctk.CTkCheckBox(
                row_frame, 
                text="Use last filled entry", 
                variable=self.excel_use_last_filled_var,
                command=lambda: end_row_entry.configure(state="disabled" if self.excel_use_last_filled_var.get() else "normal")
            )
            use_last_filled_checkbox.pack(side="left", padx=15)
            
            # Update end_row state based on checkbox
            end_row_entry.configure(state="disabled" if self.excel_use_last_filled_var.get() else "normal")
            
            # Operation type frame
            mode_frame = ctk.CTkFrame(self.param_frame)
            mode_frame.pack(fill="x", padx=10, pady=5)
            
            mode_label = ctk.CTkLabel(mode_frame, text="Operation Mode:", font=ctk.CTkFont(weight="bold"))
            mode_label.pack(anchor="w", padx=5, pady=(5, 0))
            
            # Radio buttons for operation mode
            modes = [
                ("Extract data from Excel (to memory)", "extract_data"),
                ("Perform Google search on memory data", "search_data"),
                ("Process first row only", "first_row_only")
            ]
            
            self.excel_mode_var.set(self.action.get("mode", "extract_data") if self.action else "extract_data")
            
            for text, value in modes:
                radio_btn = ctk.CTkRadioButton(
                    mode_frame,
                    text=text,
                    variable=self.excel_mode_var,
                    value=value
                )
                radio_btn.pack(anchor="w", padx=20, pady=2)
            
            # Target column for search results (only shown for search mode)
            def update_target_visibility(*args):
                if self.excel_mode_var.get() == "search_data":
                    target_frame.pack(fill="x", padx=10, pady=5)
                else:
                    target_frame.pack_forget()
            
            self.excel_mode_var.trace_add("write", update_target_visibility)
            
            target_frame = ctk.CTkFrame(self.param_frame)
            
            target_header = ctk.CTkLabel(target_frame, text="Search Results Target:", font=ctk.CTkFont(weight="bold"))
            target_header.pack(anchor="w", padx=5, pady=(5, 0))
            
            target_column_frame = ctk.CTkFrame(target_frame)
            target_column_frame.pack(fill="x", padx=10, pady=5)
            
            target_column_label = ctk.CTkLabel(target_column_frame, text="Target Column:")
            target_column_label.pack(side="left", padx=5)
            
            self.excel_target_column_var = tk.StringVar(
                value=self.action.get("target_column", "") if self.action and "target_column" in self.action else ""
            )
            
            self.target_column_menu = ctk.CTkOptionMenu(
                target_column_frame,
                variable=self.excel_target_column_var,
                values=self.columns_list if hasattr(self, "columns_list") else [""]
            )
            self.target_column_menu.pack(side="left", padx=5, fill="x", expand=True)
            
            # Show/hide target frame based on current mode
            update_target_visibility()
            
            # Load sheets if a file is already specified
            if self.excel_file_var.get():
                self.load_excel_sheets()
        
        elif action_type == "scroll_wheel":
            # Initialize with existing values if editing
            if self.action and isinstance(self.action, dict):
                if "direction" in self.action:
                    self.scroll_direction_var.set(self.action["direction"])
                if "amount" in self.action:
                    self.scroll_amount_var.set(str(self.action["amount"]))
            
            # Direction selection
            direction_frame = ctk.CTkFrame(self.param_frame)
            direction_frame.pack(fill="x", padx=10, pady=5)
            
            direction_label = ctk.CTkLabel(direction_frame, text="Scroll Direction:")
            direction_label.pack(side="left", padx=5)
            
            # Radio buttons for direction
            for direction in ["up", "down"]:
                direction_radio = ctk.CTkRadioButton(
                    direction_frame,
                    text=direction,
                    variable=self.scroll_direction_var,
                    value=direction
                )
                direction_radio.pack(side="left", padx=10)
            
            # Amount selection
            amount_frame = ctk.CTkFrame(self.param_frame)
            amount_frame.pack(fill="x", padx=10, pady=5)
            
            amount_label = ctk.CTkLabel(amount_frame, text="Scroll Amount:")
            amount_label.pack(side="left", padx=5)
            
            amount_entry = ctk.CTkEntry(amount_frame, textvariable=self.scroll_amount_var, width=100)
            amount_entry.pack(side="left", padx=5)
            
            amount_info = ctk.CTkLabel(amount_frame, text="(Number of 'clicks' to scroll)")
            amount_info.pack(side="left", padx=5)
    
    def load_excel_sheets(self):
        """Load sheets from the selected Excel file."""
        file_path = self.excel_file_var.get()
        if not file_path:
            return
        
        try:
            # Find the file using the helper method
            file_path = self.find_excel_file(file_path)
            
            # Make sure the file exists
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {self.excel_file_var.get()}\n\nPlease check if the file exists in the 'excel_files' folder.")
                return
            
            # Load Excel file and get sheet names
            excel = pd.ExcelFile(file_path)
            self.sheets_list = excel.sheet_names
            
            # Update the sheet dropdown
            self.sheet_menu.configure(values=self.sheets_list)
            
            # If there's only one sheet, select it automatically
            if len(self.sheets_list) == 1:
                self.excel_sheet_var.set(self.sheets_list[0])
                self.load_excel_columns()
            # If the previously selected sheet exists in the new file, keep it selected
            elif self.excel_sheet_var.get() in self.sheets_list:
                self.load_excel_columns()
            # Otherwise, clear the sheet selection
            else:
                self.excel_sheet_var.set("")
                self.excel_column_var.set("")
                self.column_menu.configure(values=[""])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {str(e)}")
            self.sheets_list = []
            self.sheet_menu.configure(values=[""])
            self.excel_sheet_var.set("")
            self.excel_column_var.set("")
            self.column_menu.configure(values=[""])
    
    def load_excel_columns(self, *args):
        """Load columns from the selected sheet."""
        file_path = self.excel_file_var.get()
        sheet_name = self.excel_sheet_var.get()
        
        if not file_path or not sheet_name:
            self.columns_list = []
            self.column_menu.configure(values=[""])
            self.excel_column_var.set("")
            return
        
        try:
            # Find the file using the helper method
            file_path = self.find_excel_file(file_path)
            
            # Load Excel file and get column names
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            self.columns_list = df.columns.tolist()
            
            # Update both column dropdowns
            self.column_menu.configure(values=self.columns_list)
            if hasattr(self, "target_column_menu"):
                self.target_column_menu.configure(values=self.columns_list)
            
            # If the previously selected column exists in the new sheet, keep it selected
            if self.excel_column_var.get() not in self.columns_list:
                self.excel_column_var.set("")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load columns: {str(e)}")
            self.columns_list = []
            self.column_menu.configure(values=[""])
            self.excel_column_var.set("")

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
        elif action_type == "excel":
            # Validate Excel parameters
            if not self.excel_file_var.get():
                messagebox.showwarning("Warning", "Please select an Excel file.")
                return
            if not self.excel_sheet_var.get():
                messagebox.showwarning("Warning", "Please select a sheet.")
                return
            if not self.excel_column_var.get():
                messagebox.showwarning("Warning", "Please select a column.")
                return
            
            try:
                # Validate start row
                start_row = int(self.excel_start_row_var.get())
                if start_row < 1:
                    raise ValueError("Start row must be 1 or greater.")
                    
                # Validate end row if not using last filled
                if not self.excel_use_last_filled_var.get():
                    end_row = int(self.excel_end_row_var.get())
                    if end_row < start_row:
                        raise ValueError("End row must be greater than or equal to start row.")
                
                # For search mode, validate target column
                if self.excel_mode_var.get() == "search_data" and not self.excel_target_column_var.get():
                    messagebox.showwarning("Warning", "Please select a target column for search results.")
                    return
                    
            except ValueError as e:
                messagebox.showwarning("Warning", str(e))
                return
                
            # Store all Excel parameters
            new_action["file"] = self.excel_file_var.get()
            new_action["sheet"] = self.excel_sheet_var.get()
            new_action["column"] = self.excel_column_var.get()
            new_action["start_row"] = int(self.excel_start_row_var.get())
            new_action["use_last_filled"] = self.excel_use_last_filled_var.get()
            
            if not self.excel_use_last_filled_var.get():
                new_action["end_row"] = int(self.excel_end_row_var.get())
            
            new_action["mode"] = self.excel_mode_var.get()
            
            if self.excel_mode_var.get() == "search_data":
                new_action["target_column"] = self.excel_target_column_var.get()
        
        elif action_type == "scroll_wheel":
            new_action["direction"] = self.scroll_direction_var.get()
            try:
                amount = int(self.scroll_amount_var.get())
                if amount <= 0:
                    raise ValueError("Scroll amount must be positive")
                new_action["amount"] = amount
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid positive number for scroll amount.")
                return
        
        # Call the callback with the new action
        if self.callback:
            self.callback(new_action, self.action_index)
        
        # Close the window
        self.window.destroy()
