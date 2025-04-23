# Updates Log

## 31.03.2025
- Added monitor choosing option function to the program, allowing users to select which display to use for automation
- The ActionPerformer class now supports coordinate adjustments based on the selected monitor
- Added template enabling/disabling feature in config.json with "enabled" property

## 07.04.2025
- Added a modern user interface for scenario management using customtkinter, making it easier to create, edit, and switch between different automation scenarios
- Added an info tooltip feature next to the template paths to provide additional guidance in the UI

## 08.04.2025
- Added scrollbar to every frame in editor: Templates Configuration
- Made launch file to open both automation and editor 
- Configured monitor settings to run automation and editor based on single or dual monitor setups, with the editor opening on the opposite monitor or running in the background

## 09.04.2025
- Added command lines for all kinds of usage
- Sorted the template folder, gave each scenario each template folder

## 22.04.2025
- Removed "Reset to Saves" button in editor
- Added 3 second delay before taking a screenshot
- Simplified the terminal interface by removing the monitor selection prompt in launch.py
- Automation now automatically uses the first monitor without requiring user input
- Fixed issue with output window not correctly using the opposite monitor from automation
- Enhanced monitor selection logic in launch.py to properly read monitor settings from the specific scenario file being used
- Improved multi-monitor detection to ensure output window is properly positioned on the correct monitor (if automation uses monitor 0, output uses monitor 1, and vice versa)
- Added improved handling for single-monitor setups to minimize the output window when needed

## 23.04.2025
- Removed "Save Template Changes" button in editor so there could be only one save button
- Fixed critical issue with template dependency checking that was preventing multi-path templates from working properly
- Changed dependency tracking to use template names instead of file paths
- Improved the multiple template path handling to correctly try alternative paths when the first path fails to match
- Enhanced template dependency resolution to properly recognize when template dependencies are satisfied
- Added better error messages that clearly show which template dependencies are not satisfied