"""
Templates configuration tab for the config editor.
"""
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from ..dialogs.action_editor import ActionEditor

class TemplatesTab:
    def __init__(self, parent, config, base_dir):
        """
        Initialize the templates tab.
        
        Args:
            parent: The parent container (CTkTabview tab)
            config: The configuration dictionary
            base_dir: Base directory for relative paths
        """
        self.parent = parent
        self.config = config
        self.base_dir = base_dir
        
        # Current selection state
        self.current_template_index = None
        self.current_actions = []
        self.paths_list = []
        
        # Drag and drop variables
        self.drag_source_index = None
        self.dragging = False
        self.action_drag_source_index = None
        self.action_dragging = False
        self.template_drag_source_index = None
        self.template_dragging = False
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the templates tab UI."""
        # Create a frame for the content
        content_frame = ctk.CTkFrame(self.parent)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add a title
        title = ctk.CTkLabel(content_frame, text="Templates Configuration", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)
        
        # Split into left (list) and right (details) panels
        panel_frame = ctk.CTkFrame(content_frame)
        panel_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - template list
        list_frame = ctk.CTkFrame(panel_frame, width=300)
        list_frame.pack(side="left", fill="y", padx=5, pady=5)
        list_frame.pack_propagate(False)  # Prevent shrinking
        
        list_label = ctk.CTkLabel(list_frame, text="Templates", font=ctk.CTkFont(weight="bold"))
        list_label.pack(pady=5)
        
        # Button frame for add/remove
        btn_frame = ctk.CTkFrame(list_frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        add_btn = ctk.CTkButton(btn_frame, text="Add", width=80, command=self.add_template)
        add_btn.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(btn_frame, text="Remove", width=80, command=self.remove_template)
        remove_btn.pack(side="right", padx=5)
        
        # Create a frame to contain templates listbox and scrollbar
        templates_list_frame = ctk.CTkFrame(list_frame)
        templates_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Templates listbox
        self.templates_listbox = tk.Listbox(templates_list_frame, bg="#2a2d2e", fg="white", 
                                           selectbackground="#1f6aa5", highlightthickness=0)
        self.templates_listbox.pack(side="left", fill="both", expand=True)
        self.templates_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        # Add drag and drop events for templates listbox
        self.templates_listbox.bind("<ButtonPress-1>", self.on_template_drag_start)
        self.templates_listbox.bind("<B1-Motion>", self.on_template_drag_motion)
        self.templates_listbox.bind("<ButtonRelease-1>", self.on_template_drag_end)
        
        # Add scrollbar for templates listbox
        templates_scrollbar = tk.Scrollbar(templates_list_frame, orient="vertical")
        templates_scrollbar.pack(side="right", fill="y")
        
        # Connect scrollbar to listbox
        self.templates_listbox.config(yscrollcommand=templates_scrollbar.set)
        templates_scrollbar.config(command=self.templates_listbox.yview)
        
        # Populate the listbox
        for template in self.config.get("templates", []):
            self.templates_listbox.insert(tk.END, template.get("name", "Unnamed Template"))
        
        # Right panel - template details
        self.details_frame = ctk.CTkScrollableFrame(panel_frame)
        self.details_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Initial message
        self.details_label = ctk.CTkLabel(self.details_frame, text="Select a template to edit its details")
        self.details_label.pack(pady=20)
        
        # If there are templates, select the first one
        if self.templates_listbox.size() > 0:
            self.templates_listbox.selection_set(0)
            self.on_template_select(None)  # None for the event
    
    def on_template_select(self, event):
        """Handle template selection from the listbox."""
        # Clear the details frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Get the selected index
        if not self.templates_listbox.curselection():
            return
            
        index = self.templates_listbox.curselection()[0]
        self.current_template_index = index
        template = self.config.get("templates", [])[index]
        
        # Create form fields for template details
        name_frame = ctk.CTkFrame(self.details_frame)
        name_frame.pack(fill="x", padx=5, pady=5)
        
        name_label = ctk.CTkLabel(name_frame, text="Template Name:")
        name_label.pack(side="left", padx=5)
        
        self.name_var = tk.StringVar(value=template.get("name", ""))
        name_entry = ctk.CTkEntry(name_frame, textvariable=self.name_var, width=200)
        name_entry.pack(side="left", padx=5)
        
        # Enabled checkbox
        enabled_frame = ctk.CTkFrame(self.details_frame)
        enabled_frame.pack(fill="x", padx=5, pady=5)
        
        enabled_label = ctk.CTkLabel(enabled_frame, text="Enabled:")
        enabled_label.pack(side="left", padx=5)
        
        self.enabled_var = tk.BooleanVar(value=template.get("enabled", True))
        enabled_check = ctk.CTkCheckBox(enabled_frame, text="", variable=self.enabled_var)
        enabled_check.pack(side="left", padx=5)
        
        # Template paths (multiple)
        paths_frame = ctk.CTkFrame(self.details_frame)
        paths_frame.pack(fill="x", padx=5, pady=5)
        
        # Create a frame to hold the label and info icon
        paths_label_frame = ctk.CTkFrame(paths_frame, fg_color="transparent")
        paths_label_frame.pack(fill="x", padx=5, pady=2)
        
        paths_label = ctk.CTkLabel(paths_label_frame, text="Template Paths:", anchor="w")
        paths_label.pack(side="left", padx=5)
        
        # Create an info icon
        info_icon = ctk.CTkLabel(paths_label_frame, text="ⓘ", font=ctk.CTkFont(size=16), text_color="#1f6aa5")
        info_icon.pack(side="left", padx=2)
        
        # Add tooltip functionality to the info icon
        self.tooltip_window = None
        
        def show_tooltip(event):
            x, y = event.x_root, event.y_root
            self.tooltip_window = tk.Toplevel(self.parent)
            self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
            self.tooltip_window.wm_geometry(f"+{x+10}+{y+10}")
            
            # Get the current appearance mode to set appropriate colors
            mode = ctk.get_appearance_mode()
            bg_color = "#343638" if mode == "Dark" else "#EBEBEB"
            fg_color = "#DCE4EE" if mode == "Dark" else "#505050"
            
            frame = tk.Frame(self.tooltip_window, background=bg_color, borderwidth=1, relief="solid")
            frame.pack()
            
            label = tk.Label(
                frame, 
                text="Drag paths to reorder them",
                background=bg_color,
                foreground=fg_color,
                padx=5,
                pady=2,
                font=("Segoe UI", 10)
            )
            label.pack()
        
        def hide_tooltip():
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        
        info_icon.bind("<Enter>", show_tooltip)
        info_icon.bind("<Leave>", lambda e: hide_tooltip())
        
        # Determine if it's a single path or multiple paths - more consistent handling
        if "path" in template:
            # Convert single path to array format
            self.paths_list = [template["path"]]
        elif "paths" in template:
            # Multiple paths
            self.paths_list = template["paths"]
        else:
            self.paths_list = []
        
        # Create a frame to contain both listbox and scrollbar
        paths_list_frame = ctk.CTkFrame(paths_frame)
        paths_list_frame.pack(fill="x", padx=5, pady=5)
        
        # Listbox for paths
        self.paths_listbox = tk.Listbox(paths_list_frame, bg="#2a2d2e", fg="white", 
                                        selectbackground="#1f6aa5", highlightthickness=0, height=10,
                                        exportselection=0)  # Add exportselection=0 to maintain selection
        self.paths_listbox.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar for paths listbox
        paths_scrollbar = tk.Scrollbar(paths_list_frame, orient="vertical")
        paths_scrollbar.pack(side="right", fill="y")
        
        # Connect scrollbar to listbox
        self.paths_listbox.config(yscrollcommand=paths_scrollbar.set)
        paths_scrollbar.config(command=self.paths_listbox.yview)
        
        # Bind drag and drop events
        self.paths_listbox.bind("<ButtonPress-1>", self.on_path_drag_start)
        self.paths_listbox.bind("<B1-Motion>", self.on_path_drag_motion)
        self.paths_listbox.bind("<ButtonRelease-1>", self.on_path_drag_end)
        
        # Populate paths listbox
        for path in self.paths_list:
            self.paths_listbox.insert(tk.END, path)
        
        # Select first item by default if available
        if len(self.paths_list) > 0:
            self.paths_listbox.selection_set(0)
        
        # Add buttons for managing paths
        paths_btn_frame = ctk.CTkFrame(paths_frame)
        paths_btn_frame.pack(fill="x", padx=5, pady=5)
        
        add_path_btn = ctk.CTkButton(paths_btn_frame, text="Add Path", width=100, 
                                    command=self.add_template_path)
        add_path_btn.pack(side="left", padx=5)
        
        snipping_tool_btn = ctk.CTkButton(paths_btn_frame, text="Capture Screenshot", width=120,
                                       command=self.open_snipping_tool)
        snipping_tool_btn.pack(side="left", padx=5)
        
        remove_path_btn = ctk.CTkButton(paths_btn_frame, text="Remove Path", width=100,
                                       command=self.remove_template_path)
        remove_path_btn.pack(side="left", padx=5)
        
        # Template methods
        methods_frame = ctk.CTkFrame(self.details_frame)
        methods_frame.pack(fill="x", padx=5, pady=5)
        
        methods_label = ctk.CTkLabel(methods_frame, text="Template Methods:", anchor="w")
        methods_label.pack(fill="x", padx=5, pady=2)
        
        # Get all available methods
        all_methods = ["TM_CCOEFF_NORMED", "TM_CCORR_NORMED", "TM_SQDIFF_NORMED"]
        
        # Create a dictionary of method checkboxes
        self.method_vars = {}
        methods_box = ctk.CTkFrame(methods_frame)
        methods_box.pack(fill="x", padx=5, pady=5)
        
        # Get current template methods
        template_methods = template.get("methods", self.config.get("default_template_methods", ["TM_CCOEFF_NORMED"]))
        
        # Create checkboxes for each method
        for i, method in enumerate(all_methods):
            # Create a variable for this method and initialize it based on whether it's in template_methods
            self.method_vars[method] = tk.BooleanVar(value=method in template_methods)
            
            # Create the checkbox
            method_check = ctk.CTkCheckBox(methods_box, text=method, variable=self.method_vars[method])
            
            # Place in a grid (3 columns)
            row = i // 3
            col = i % 3
            method_check.grid(row=row, column=col, padx=5, pady=2, sticky="w")
        
        # Dependencies
        depends_frame = ctk.CTkFrame(self.details_frame)
        depends_frame.pack(fill="x", padx=5, pady=5)
        
        depends_label = ctk.CTkLabel(depends_frame, text="Depends On Template:")
        depends_label.pack(side="left", padx=5)
        
        # Get all template names for dependencies dropdown
        template_names = [t.get("name", "Unnamed") for t in self.config.get("templates", [])]
        
        self.depends_var = tk.StringVar(value=template.get("depends_on", ""))
        depends_menu = ctk.CTkOptionMenu(depends_frame, variable=self.depends_var,
                                        values=[""] + template_names)
        depends_menu.pack(side="left", padx=5)
        
        # Actions section
        actions_frame = ctk.CTkFrame(self.details_frame)
        actions_frame.pack(fill="x", padx=5, pady=5)
        
        actions_label = ctk.CTkLabel(actions_frame, text="Actions:", anchor="w", 
                                     font=ctk.CTkFont(weight="bold"))
        actions_label.pack(fill="x", padx=5, pady=2)
        
        # Create a frame to contain actions listbox and scrollbar
        actions_list_frame = ctk.CTkFrame(actions_frame)
        actions_list_frame.pack(fill="x", padx=5, pady=5)
        
        # Actions listbox
        self.actions_listbox = tk.Listbox(actions_list_frame, bg="#2a2d2e", fg="white", 
                                         selectbackground="#1f6aa5", highlightthickness=0, height=5,
                                         exportselection=0)
        self.actions_listbox.pack(side="left", fill="x", expand=True)
        
        # Add scrollbar for actions listbox
        actions_scrollbar = tk.Scrollbar(actions_list_frame, orient="vertical")
        actions_scrollbar.pack(side="right", fill="y")
        
        # Connect scrollbar to listbox
        self.actions_listbox.config(yscrollcommand=actions_scrollbar.set)
        actions_scrollbar.config(command=self.actions_listbox.yview)
        
        # Bind drag and drop events
        self.actions_listbox.bind("<ButtonPress-1>", self.on_action_drag_start)
        self.actions_listbox.bind("<B1-Motion>", self.on_action_drag_motion)
        self.actions_listbox.bind("<ButtonRelease-1>", self.on_action_drag_end)
        
        # Action buttons
        action_btn_frame = ctk.CTkFrame(actions_frame)
        action_btn_frame.pack(fill="x", padx=5, pady=5)
        
        add_action_btn = ctk.CTkButton(action_btn_frame, text="Add Action", width=100,
                                      command=self.add_template_action)
        add_action_btn.pack(side="left", padx=5)
        
        edit_action_btn = ctk.CTkButton(action_btn_frame, text="Edit Action", width=100,
                                       command=self.edit_template_action)
        edit_action_btn.pack(side="left", padx=5)
        
        remove_action_btn = ctk.CTkButton(action_btn_frame, text="Remove Action", width=100,
                                         command=self.remove_template_action)
        remove_action_btn.pack(side="left", padx=5)
        
        # Populate actions listbox
        self.current_actions = template.get("actions", [])
        self.update_actions_listbox()
        
        # Select first action by default if available
        if len(self.current_actions) > 0:
            self.actions_listbox.selection_set(0)
    
    def update_actions_listbox(self):
        """Update the actions listbox with the current actions."""
        self.actions_listbox.delete(0, tk.END)
        for action in self.current_actions:
            if isinstance(action, dict) and "type" in action:
                action_text = action["type"]
                if action_text == "type_message" and "message" in action:
                    msg_preview = action["message"]
                    if len(msg_preview) > 20:
                        msg_preview = msg_preview[:20] + "..."
                    action_text = f"{action_text}: '{msg_preview}'"
                elif action_text == "press_key" and "key" in action:
                    action_text = f"{action_text}: {action['key']}"
                elif action_text == "wait" and "seconds" in action:
                    action_text = f"{action_text}: {action['seconds']}s"
                
                self.actions_listbox.insert(tk.END, action_text)
            else:
                self.actions_listbox.insert(tk.END, str(action))
    
    def update_config(self):
        """Update config with changes from templates tab."""
        # If there's a template being edited, save it
        if self.current_template_index is not None and self.current_template_index >= 0 and self.current_template_index < len(self.config.get("templates", [])):
            template = self.config["templates"][self.current_template_index]
            
            # Update basic properties
            template["name"] = self.name_var.get()
            template["enabled"] = self.enabled_var.get()
            
            # Always use "paths" key for consistency, even for single path
            template["paths"] = self.paths_list
            # Remove "path" key if it exists
            if "path" in template:
                del template["path"]
            
            # Update methods - ensure self.method_vars exists
            if hasattr(self, 'method_vars') and self.method_vars:
                template["methods"] = [method for method, var in self.method_vars.items() if var.get()]
            
            # Update dependency
            dependency = self.depends_var.get()
            if dependency:
                template["depends_on"] = dependency
            else:
                if "depends_on" in template:
                    del template["depends_on"]
            
            # Update actions
            template["actions"] = self.current_actions
            
            # Update the listbox text
            self.templates_listbox.delete(self.current_template_index)
            self.templates_listbox.insert(self.current_template_index, template["name"])
            self.templates_listbox.selection_set(self.current_template_index)
        
        return True
    
    def save_template_changes(self):
        """This method is deprecated. All template changes are now saved through update_config."""
        # This method is kept as a stub for backward compatibility but doesn't do anything
        pass
    
    def add_template(self):
        """Add a new template to the configuration."""
        # Create a new template with default values
        new_template = {
            "name": "New Template",
            "path": "",
            "methods": self.config.get("default_template_methods", ["TM_CCOEFF_NORMED"]),
            "enabled": True,
            "actions": []
        }
        
        # Add to config
        if "templates" not in self.config:
            self.config["templates"] = []
        
        self.config["templates"].append(new_template)
        
        # Add to listbox and select it
        index = self.templates_listbox.size()
        self.templates_listbox.insert(tk.END, new_template["name"])
        self.templates_listbox.selection_clear(0, tk.END)
        self.templates_listbox.selection_set(index)
        self.templates_listbox.see(index)
        
        # Show the details form
        self.on_template_select(None)
    
    def remove_template(self):
        """Remove the selected template from the configuration."""
        if not self.templates_listbox.curselection():
            return
            
        index = self.templates_listbox.curselection()[0]
        template_name = self.templates_listbox.get(index)
        
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove template '{template_name}'?"):
            # Remove from config
            del self.config["templates"][index]
            
            # Remove from listbox
            self.templates_listbox.delete(index)
            
            # Clear details frame
            for widget in self.details_frame.winfo_children():
                widget.destroy()
            
            # Reset current template index
            self.current_template_index = None
            
            # Select next template if available
            if self.templates_listbox.size() > 0:
                next_index = min(index, self.templates_listbox.size() - 1)
                self.templates_listbox.selection_set(next_index)
                self.on_template_select(None)
    
    def add_template_path(self):
        """Add a new path to the selected template."""
        # Get the base directory for templates
        templates_dir = os.path.join(self.base_dir, "templates")
        
        # Open file dialog relative to the templates directory
        file_path = filedialog.askopenfilename(
            title="Select Template Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")],
            initialdir=templates_dir
        )
        
        if not file_path:
            return
            
        # Convert to relative path
        if os.path.abspath(file_path).startswith(os.path.abspath(self.base_dir)):
            rel_path = os.path.relpath(file_path, self.base_dir)
            # Convert Windows backslashes to forward slashes for JSON
            rel_path = rel_path.replace("\\", "/")
        else:
            rel_path = file_path
        
        # Add to paths list and update listbox
        self.paths_list.append(rel_path)
        self.paths_listbox.insert(tk.END, rel_path)
    
    def remove_template_path(self):
        """Remove a path from the selected template."""
        if not self.paths_listbox.curselection():
            messagebox.showwarning("Warning", "Please select a path to remove.")
            return
            
        path_index = self.paths_listbox.curselection()[0]
        
        # Remove the restriction on minimum paths - allow removing all paths
        
        # Remove from list and listbox
        del self.paths_list[path_index]
        self.paths_listbox.delete(path_index)
        
        # Select another item if available
        if len(self.paths_list) > 0:
            # Select same index or last item if we removed the last item
            new_index = min(path_index, len(self.paths_list) - 1)
            self.paths_listbox.selection_set(new_index)
    
    def action_editor_callback(self, new_action, action_index=None):
        """Callback for the action editor to add/update an action."""
        if action_index is not None:
            # Edit existing
            self.current_actions[action_index] = new_action
        else:
            # Add new
            self.current_actions.append(new_action)
        
        # Update the actions listbox
        self.update_actions_listbox()
        
        # Select the new or updated action
        if action_index is not None:
            self.actions_listbox.selection_set(action_index)
        else:
            self.actions_listbox.selection_set(len(self.current_actions) - 1)
    
    def add_template_action(self):
        """Add a new action to the selected template."""
        ActionEditor(self.parent.winfo_toplevel(), callback=self.action_editor_callback)
    
    def edit_template_action(self):
        """Edit the selected action."""
        if not self.actions_listbox.curselection():
            messagebox.showwarning("Warning", "Please select an action to edit.")
            return
            
        action_index = self.actions_listbox.curselection()[0]
        action = self.current_actions[action_index]
        
        ActionEditor(
            self.parent.winfo_toplevel(), 
            action=action, 
            action_index=action_index,
            callback=self.action_editor_callback
        )
    
    def remove_template_action(self):
        """Remove the selected action."""
        if not self.actions_listbox.curselection():
            messagebox.showwarning("Warning", "Please select an action to remove.")
            return
            
        action_index = self.actions_listbox.curselection()[0]
        
        # Remove from list and listbox
        del self.current_actions[action_index]
        self.actions_listbox.delete(action_index)
        
        # Select another action if available
        if len(self.current_actions) > 0:
            # Select same index or last item if we removed the last item
            new_index = min(action_index, len(self.current_actions) - 1)
            self.actions_listbox.selection_set(new_index)
    
    def on_path_drag_start(self, event):
        """Start dragging a path item."""
        # Get the index of the clicked item
        drag_index = self.paths_listbox.nearest(event.y)
        if drag_index >= 0 and drag_index < len(self.paths_list):
            # Store the source index
            self.drag_source_index = drag_index
            self.paths_listbox.selection_clear(0, tk.END)
            self.paths_listbox.selection_set(drag_index)
            self.dragging = True
    
    def on_path_drag_motion(self, event):
        """Handle mouse motion during drag."""
        if not self.dragging or self.drag_source_index is None:
            return
        
        # Get the current hover index
        hover_index = self.paths_listbox.nearest(event.y)
        if hover_index >= 0 and hover_index < len(self.paths_list) and hover_index != self.drag_source_index:
            # Visually highlight the target position
            self.paths_listbox.selection_clear(0, tk.END)
            self.paths_listbox.selection_set(hover_index)
    
    def on_path_drag_end(self, event):
        """End dragging and update the order."""
        if not self.dragging or self.drag_source_index is None:
            self.dragging = False
            return
        
        # Get the drop target index
        drop_index = self.paths_listbox.nearest(event.y)
        
        # Only reorder if dropping to a different position
        if drop_index != self.drag_source_index and drop_index >= 0 and drop_index < len(self.paths_list):
            # Get the path being moved
            path_item = self.paths_list[self.drag_source_index]
            
            # Remove from source position
            del self.paths_list[self.drag_source_index]
            self.paths_listbox.delete(self.drag_source_index)
            
            # Insert at target position
            self.paths_list.insert(drop_index, path_item)
            self.paths_listbox.insert(drop_index, path_item)
            
            # Keep the moved item selected
            self.paths_listbox.selection_clear(0, tk.END)
            self.paths_listbox.selection_set(drop_index)
            self.paths_listbox.see(drop_index)
        
        # Reset drag state
        self.dragging = False
        self.drag_source_index = None
    
    def on_action_drag_start(self, event):
        """Start dragging an action item."""
        # Get the index of the clicked item
        drag_index = self.actions_listbox.nearest(event.y)
        if drag_index >= 0 and drag_index < len(self.current_actions):
            # Store the source index
            self.action_drag_source_index = drag_index
            self.actions_listbox.selection_clear(0, tk.END)
            self.actions_listbox.selection_set(drag_index)
            self.action_dragging = True
    
    def on_action_drag_motion(self, event):
        """Handle mouse motion during action drag."""
        if not self.action_dragging or self.action_drag_source_index is None:
            return
        
        # Get the current hover index
        hover_index = self.actions_listbox.nearest(event.y)
        if hover_index >= 0 and hover_index < len(self.current_actions) and hover_index != self.action_drag_source_index:
            # Visually highlight the target position
            self.actions_listbox.selection_clear(0, tk.END)
            self.actions_listbox.selection_set(hover_index)
    
    def on_action_drag_end(self, event):
        """End dragging and update the action order."""
        if not self.action_dragging or self.action_drag_source_index is None:
            self.action_dragging = False
            return
        
        # Get the drop target index
        drop_index = self.actions_listbox.nearest(event.y)
        
        # Only reorder if dropping to a different position
        if drop_index != self.action_drag_source_index and drop_index >= 0 and drop_index < len(self.current_actions):
            # Get the action being moved
            action_item = self.current_actions[self.action_drag_source_index]
            
            # Remove from source position
            del self.current_actions[self.action_drag_source_index]
            self.actions_listbox.delete(self.action_drag_source_index)
            
            # Insert at target position
            self.current_actions.insert(drop_index, action_item)
            self.actions_listbox.insert(drop_index, action_item)
            
            # Keep the moved item selected
            self.actions_listbox.selection_clear(0, tk.END)
            self.actions_listbox.selection_set(drop_index)
            self.actions_listbox.see(drop_index)
        
        # Reset drag state
        self.action_dragging = False
        self.action_drag_source_index = None
    
    def on_template_drag_start(self, event):
        """Start dragging a template item."""
        # Get the index of the clicked item
        drag_index = self.templates_listbox.nearest(event.y)
        if drag_index >= 0 and drag_index < self.templates_listbox.size():
            # Only start drag if it's been a bit of movement (to allow normal selection)
            self.template_drag_start_y = event.y
            self.template_drag_source_index = drag_index
            # Selection is handled by the normal listbox click behavior
            self.template_dragging = False  # Start as False, set to True in motion if actually dragging
    
    def on_template_drag_motion(self, event):
        """Handle mouse motion during template drag."""
        if self.template_drag_source_index is None:
            return
            
        # Only consider it a drag if moved at least 5 pixels
        if not self.template_dragging and abs(event.y - self.template_drag_start_y) > 5:
            self.template_dragging = True
            
        if not self.template_dragging:
            return
        
        # Get the current hover index
        hover_index = self.templates_listbox.nearest(event.y)
        if hover_index >= 0 and hover_index < self.templates_listbox.size() and hover_index != self.template_drag_source_index:
            # Visually highlight the target position
            self.templates_listbox.selection_clear(0, tk.END)
            self.templates_listbox.selection_set(hover_index)
    
    def on_template_drag_end(self, event):
        """End dragging and update the template order."""
        if self.template_drag_source_index is None or not self.template_dragging:
            # Reset drag state without doing anything (it was just a click)
            self.template_dragging = False
            self.template_drag_source_index = None
            return
        
        # Get the drop target index
        drop_index = self.templates_listbox.nearest(event.y)
        
        # Only reorder if dropping to a different position
        if drop_index != self.template_drag_source_index and drop_index >= 0 and drop_index < self.templates_listbox.size():
            # Move the template in the config
            template = self.config["templates"].pop(self.template_drag_source_index)
            self.config["templates"].insert(drop_index, template)
            
            # Update the listbox
            template_name = self.templates_listbox.get(self.template_drag_source_index)
            self.templates_listbox.delete(self.template_drag_source_index)
            self.templates_listbox.insert(drop_index, template_name)
            
            # Keep the moved item selected
            self.templates_listbox.selection_clear(0, tk.END)
            self.templates_listbox.selection_set(drop_index)
            self.templates_listbox.see(drop_index)
            
            # Update current template index if it was the one being dragged
            if self.current_template_index == self.template_drag_source_index:
                self.current_template_index = drop_index
            # Or adjust it if needed due to the reordering
            elif self.template_drag_source_index < self.current_template_index <= drop_index:
                self.current_template_index -= 1
            elif drop_index <= self.current_template_index < self.template_drag_source_index:
                self.current_template_index += 1
        
        # Reset drag state
        self.template_dragging = False
        self.template_drag_source_index = None
    
    def open_snipping_tool(self):
        """Open Windows Snipping Tool for capturing screenshots."""
        try:
            import subprocess
            import platform
            
            # Check operating system
            if platform.system() == "Windows":
                # Windows 10/11 new Snipping Tool (or legacy Snipping Tool)
                try:
                    # Try the modern Windows 10/11 Snipping Tool first
                    subprocess.Popen(["explorer.exe", "ms-screenclip:"])
                except:
                    # Fall back to legacy Snipping Tool
                    subprocess.Popen(["SnippingTool.exe"])
                    
            elif platform.system() == "Darwin":  # macOS
                # Use macOS screenshot tool
                subprocess.Popen(["screencapture", "-i", "-c"])
                
            elif platform.system() == "Linux":
                # Try common Linux screenshot tools
                try:
                    # Try GNOME Screenshot first
                    subprocess.Popen(["gnome-screenshot", "--interactive"])
                except:
                    try:
                        # Try KDE Spectacle
                        subprocess.Popen(["spectacle", "-r"])
                    except:
                        try:
                            # Try xfce4-screenshooter
                            subprocess.Popen(["xfce4-screenshooter", "-r"])
                        except:
                            print("Could not find a screenshot tool on your Linux system.")
            
            print(f"Launched screenshot tool on {platform.system()}")
        except Exception as e:
            print(f"Error launching screenshot tool: {e}")
