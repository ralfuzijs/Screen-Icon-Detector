ralfuzijs: #codebase You are an expert in Jira ticket creation and our providing excelent phrasing and sentences for simplistic reading. Give this project a description. We want to create a ticket in Jira Sprint and have to fill out the description field. 

GitHub Copilot: 

ralfuzijs: #codebase  are an expert in Jira ticket creation and our providing excelent phrasing and sentences for simplistic reading. Give this project a description. We want to create a ticket in Jira Sprint and have to fill out the description field.

GitHub Copilot: **Description for Jira Ticket:**

This project aims to develop a screen icon detection system that identifies and interacts with specific UI elements, such as the Microsoft Teams icon, using template matching techniques. The system leverages OpenCV for image processing, PyAutoGUI for automation, and supports multi-monitor setups. Key features include configurable templates, action sequences (e.g., mouse movements, clicks, typing), and a visualizer for debugging matches. The solution is designed to automate repetitive tasks efficiently while providing flexibility through a JSON-based configuration.

ralfuzijs: #codebase Use all of the files in #folder:src and provide good detailed architecture, useful for a documentation about the project. 

GitHub Copilot: ### **Project Architecture: Screen Icon Detector**

The **Screen Icon Detector** is a Python-based automation tool designed to detect specific UI elements (e.g., Microsoft Teams icons) on the screen using template matching techniques. It performs actions like mouse movements, clicks, and typing based on the detected templates. Below is a detailed breakdown of the architecture and components of the project.

---

### **1. High-Level Overview**

The project is structured into modular components, each responsible for a specific functionality. The main workflow involves:

1. **Configuration Loading**: Reading the config.json file to define templates, actions, and settings.
2. **Template Matching**: Using OpenCV to locate templates in screenshots.
3. **Action Execution**: Performing actions (e.g., mouse clicks, typing) based on the matched templates.
4. **Visualization**: Displaying the results of template matching for debugging and analysis.
5. **Monitor Selection**: Supporting multi-monitor setups for precise automation.

---

### **2. Key Components**

#### **2.1 main.py**
- **Purpose**: Acts as the entry point of the application and orchestrates the overall workflow.
- **Responsibilities**:
  - Sets up a **kill switch** (`Ctrl+Esc`) for emergency termination.
  - Loads the configuration from config.json.
  - Handles monitor selection based on user preferences.
  - Initializes template matchers and action performers.
  - Executes the main loop to:
    - Capture screenshots.
    - Match templates.
    - Perform actions based on matches.
    - Visualize results.
- **Key Functions**:
  - `setup_kill_switch()`: Registers a global hotkey to stop the program.
  - `capture_screenshot(output_path)`: Captures a screenshot of the selected monitor or the entire screen.
  - `perform_actions()`: Executes actions defined in the configuration for matched templates.

---

#### **2.2 template_matcher.py**
- **Purpose**: Handles template matching using OpenCV.
- **Responsibilities**:
  - Loads template images.
  - Matches templates against screenshots using multiple methods (e.g., `TM_CCOEFF_NORMED`, `TM_SQDIFF_NORMED`).
  - Evaluates matches based on thresholds and agreement between methods.
- **Key Classes**:
  - `TemplateMatcher`: Encapsulates the logic for template matching.
    - **Methods**:
      - `load_template(template_path)`: Loads a template image in grayscale.
      - `match_template(screenshot_path)`: Matches the template against a screenshot and returns match coordinates and results.
      - `calculate_distance(point1, point2)`: Calculates the Euclidean distance between two points to evaluate match proximity.

---

#### **2.3 action_performer.py**
- **Purpose**: Executes actions (e.g., mouse movements, clicks, typing) based on matched templates.
- **Responsibilities**:
  - Moves the mouse to specified coordinates.
  - Clicks or double-clicks at the current mouse position.
  - Types messages using either clipboard pasting or character-by-character typing.
  - Presses specific keys (e.g., `Enter`).
- **Key Classes**:
  - `ActionPerformer`: Encapsulates the logic for performing actions.
    - **Methods**:
      - `move_mouse(x, y)`: Moves the mouse to specified coordinates.
      - `click(button, clicks)`: Performs a mouse click.
      - `type_message(message)`: Types a message using the configured method (`clipboard` or `character`).
      - `press_key(key)`: Presses a specific key.

---

#### **2.4 visualizer.py**
- **Purpose**: Provides a visual representation of template matching results for debugging and analysis.
- **Responsibilities**:
  - Displays the screenshot with rectangles drawn around matched templates.
  - Shows a bar chart of match values for different methods.
  - Highlights the best match and agreement between methods.
- **Key Functions**:
  - `display_results(screenshot, match_coordinates, match_results, template_name, monitor)`: Visualizes the template matching results using Matplotlib and OpenCV.

---

#### **2.5 monitor_option.py**
- **Purpose**: Manages multi-monitor setups.
- **Responsibilities**:
  - Retrieves a list of available monitors.
  - Allows the user to select a specific monitor for automation.
- **Key Functions**:
  - `get_monitors()`: Returns a list of available monitors using the `mss` library.
  - `select_monitor()`: Prompts the user to select a monitor from the list.

---

### **3. Configuration File (`config.json`)**
- **Purpose**: Defines templates, actions, and settings for the application.
- **Structure**:
  - **Templates**:
    - `path`: Path to the template image.
    - `methods`: List of template matching methods to use.
    - `enabled`: Boolean flag to enable/disable the template.
    - `depends_on`: Specifies dependencies between templates.
    - `actions`: List of actions to perform when the template is matched.
  - **Settings**:
    - `screenshot_interval`: Interval (in seconds) between screenshots.
    - `max_loops`: Maximum number of iterations (0 for infinite).
    - `visualizer_enabled`: Enables/disables visualization.
    - `monitor_settings`: Configures monitor selection.
    - `action_settings`: Configures action parameters (e.g., mouse movement duration, typing method).

---

### **4. Workflow**

1. **Initialization**:
   - Load configuration from config.json.
   - Initialize template matchers and action performers.
   - Select the monitor for automation.

2. **Main Loop**:
   - Capture a screenshot of the selected monitor.
   - For each template:
     - Check if the template is enabled and its dependencies are satisfied.
     - Perform template matching.
     - If a match is found:
       - Visualize the results (if enabled).
       - Execute the associated actions.
   - Wait for the configured interval before the next iteration.

3. **Termination**:
   - The program stops when the kill switch is activated or the maximum number of loops is reached.

---

### **5. Dependencies**

The project relies on the following Python libraries:
- **OpenCV**: For image processing and template matching.
- **Matplotlib**: For visualizing template matching results.
- **NumPy**: For numerical operations.
- **PyAutoGUI**: For mouse and keyboard automation.
- **Pyperclip**: For clipboard operations.
- **Keyboard**: For registering the kill switch.
- **MSS**: For capturing screenshots of specific monitors.

---

### **6. Features**

- **Template Matching**:
  - Supports multiple methods for robust detection.
  - Configurable thresholds and distance checks.
  - Dependency management between templates.

- **Action Automation**:
  - Smooth mouse movements with randomness for human-like behavior.
  - Flexible typing methods (clipboard or character-by-character).
  - Configurable delays between actions.

- **Visualization**:
  - Highlights matched templates with rectangles.
  - Displays agreement between methods.
  - Provides a bar chart of match values.

- **Multi-Monitor Support**:
  - Allows users to select a specific monitor for automation.
  - Adjusts coordinates based on the selected monitor.

- **Kill Switch**:
  - Ensures safe termination of the program using a global hotkey.

---

### **7. Folder Structure**

```
screen-icon-detector
├── src
│   ├── main.py               # Entry point of the application
│   ├── template_matcher.py    # Template matching logic
│   ├── action_performer.py    # Action execution logic
│   ├── visualizer.py          # Visualization of results
│   ├── monitor_option.py      # Multi-monitor support
├── templates                  # Template images for matching
├── screenshots                # Captured screenshots
├── tests                      # Unit tests
├── config.json                # Configuration file
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

---

This architecture ensures modularity, flexibility, and ease of maintenance, making the project suitable for various automation tasks.