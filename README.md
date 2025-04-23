# Teams Icon Detector

This project is designed to detect the Microsoft Teams icon in screenshots using template matching with OpenCV. It provides a simple interface to load a screenshot, match the template, and visualize the results.

## Project Structure

```
teams-icon-detector
├── src
│   ├── main.py               # Entry point of the application
│   ├── template_matcher.py    # Contains the TemplateMatcher class for template matching
│   └── visualizer.py          # Contains the display_results function for visualizing matches
├── templates
│   └── teams_icon.png         # Template image of the MS Teams icon
├── screenshots
│   └── sample_screenshot.png   # Sample screenshot for testing
├── tests
│   └── test_template_matcher.py # Unit tests for the TemplateMatcher class
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/teams-icon-detector.git
   cd teams-icon-detector
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:
```
python src/main.py
```

This will load the sample screenshot, perform template matching with the MS Teams icon, and display the results.

## Testing

To run the unit tests for the TemplateMatcher class, use:
```
pytest tests/test_template_matcher.py
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.