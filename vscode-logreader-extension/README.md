# vscode-logreader-extension

## Overview
The Log Reader extension for Visual Studio Code allows users to interact with a local MCP server to retrieve and view log files from specified directories. This extension provides a user-friendly interface to search for log files based on filename patterns and view their contents directly within the editor.

## Features
- Connects to a local MCP server to fetch log files.
- Search for log files using filename patterns.
- View log file contents, with support for large files (configurable).
- Easy configuration through a YAML file.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/vscode-logreader-extension.git
   ```
2. Navigate to the project directory:
   ```
   cd vscode-logreader-extension
   ```
3. Install the dependencies:
   ```
   npm install
   ```

## Usage
1. Open the command palette (Ctrl+Shift+P) in Visual Studio Code.
2. Type and select `Log Reader: Get Log Files`.
3. Enter a filename search string (optional) to filter the results.
4. View the retrieved log files in the output panel.

## Configuration
The extension uses a `config.yaml` file for configuration settings. You can modify the following parameters:
- `log_paths`: List of directories to search for log files.
- `max_file_size`: Maximum size of log files to read (in bytes).

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.


## Test the extension

To test the extension:

1. Press F5 to start debugging. This will:

* Build the extension
* Open a new VS Code window with the extension loaded
* Start watching for changes

2. In the new window:
* Press Ctrl+Shift+P to open the command palette
* Type "Get Log Files" and select the command
* Enter an optional search string
* Select a log file from the list to view its contents

The extension will:

* Start the Python MCP server when needed
* Show a progress indicator while fetching logs
* Display log files in a quick pick menu
* Show the selected log file in a new editor
* Provide error messages if something goes wrong
You can also clear the output channel using the "Clear Log Reader Output" command.