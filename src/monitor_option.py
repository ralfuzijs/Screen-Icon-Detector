from mss import mss

def get_monitors():
    """Get a list of available monitors"""
    with mss() as sct:
        monitors = sct.monitors
    
    # First entry is a combined view of all monitors
    all_monitors = monitors[1:]
    
    return all_monitors

def select_monitor():
    """Let the user select which monitor to use"""
    monitors = get_monitors()
    
    print("\nAvailable monitors:")
    for i, monitor in enumerate(monitors):
        print(f"{i+1}. Monitor {i+1}: {monitor['width']}x{monitor['height']} at position ({monitor['left']}, {monitor['top']})")
    
    selection = 0
    while selection < 1 or selection > len(monitors):
        try:
            selection = int(input(f"\nSelect a monitor (1-{len(monitors)}): "))
        except ValueError:
            print("Please enter a valid number")
    
    # Return the selected monitor (0-based index)
    return monitors[selection-1]
