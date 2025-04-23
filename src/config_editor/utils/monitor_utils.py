"""
Utilities for detecting and handling multiple monitors.
"""
from mss import mss

def get_available_monitors():
    """Get a list of available monitors."""
    try:
        with mss() as sct:
            # Get all monitors, excluding the "all monitors" first entry
            return sct.monitors[1:]
    except Exception as e:
        print(f"Error getting monitors: {e}")
        return []
