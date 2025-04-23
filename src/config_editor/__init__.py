"""
Config Editor package for Screen Icon Detector.
Provides a UI for editing configuration files.

To launch the editor, use:
    from src.config_editor import run_editor
    run_editor()
"""
import os
import sys
import traceback

def run_config_editor(config_path=None):
    """
    Run the configuration editor application.
    
    Args:
        config_path: Path to the configuration file (optional).
                    If not provided, the default scenario will be used.
    
    Returns:
        True if the editor was run successfully, False otherwise.
    """
    try:
        # Get the base directory (two levels up from this file in src/config_editor)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # If no config path provided, use the default scenario
        if not config_path:
            config_path = os.path.join(base_dir, "scenario_default.json")
        
        print(f"Starting config editor with configuration: {config_path}")
        
        # Import here to avoid circular imports
        from .editor_app import ConfigEditor
        
        # Create and run the editor
        editor = ConfigEditor(config_path)
        editor.run()
        
        return True
    except Exception as e:
        print(f"Error running config editor: {e}")
        traceback.print_exc()
        return False

# Provide a simple function to run the editor (alias for better naming)
def run_editor(config_path=None):
    """
    Launch the configuration editor with the specified config path.
    
    Args:
        config_path: Path to the configuration file to edit (optional)
                    If None, the default scenario will be used.
    """
    return run_config_editor(config_path)

# If this module is run directly
if __name__ == "__main__":
    # When run directly, add the src directory to the path
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if src_dir not in sys.path:
        sys.path.append(src_dir)
    
    # Add the project root to the path
    project_root = os.path.dirname(src_dir)
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    # Run the editor
    run_config_editor()

__all__ = [
    'run_config_editor',  # Original entry point
    'run_editor',         # Simplified launcher
]
