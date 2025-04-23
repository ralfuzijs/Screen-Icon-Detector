# Screen Icon Detector - Command Line Usage

This document describes all the command line arguments available for the Screen Icon Detector application.

## Basic Usage

```
python src/launch.py [options]
```

## Available Options

### Main Actions (mutually exclusive)

| Command | Description |
|---------|-------------|
| `--check-scenario SCENARIO_NAME` | Check if a specific scenario exists |
| `--list-scenarios` | List all available scenarios |
| `--automation-only` | Launch just the automation component |
| `--editor-only` | Launch just the editor component |
