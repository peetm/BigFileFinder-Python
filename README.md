# BigFileFinder-Python

A GUI application for scanning folders and drives to find and manage large files. Built with Python and Tkinter.

## Features

- **Recursive Folder Scanning**: Scan entire directories and drives to find all files
- **Size-Based Sorting**: Files are automatically sorted by size (largest first)
- **Real-Time Progress**: Live updates showing scan progress and file count
- **File Selection**: Select individual files or all files at once
- **Safe Deletion**: Delete selected files with confirmation dialog
- **Size Statistics**: View total size of selected files and freed space
- **Error Handling**: Gracefully handles permission errors and inaccessible files

## Requirements

- Python 3.x
- Tkinter (usually included with Python)

## Installation

No installation required! Just run the script:

```bash
python BigFileFinder.py
```

Or make it executable on Unix-like systems:

```bash
chmod +x BigFileFinder.py
./BigFileFinder.py
```

## Usage

1. **Browse**: Click "Browse..." to select a folder or drive to scan
2. **Start Scan**: Click "Start Scan" to begin scanning for files
3. **Stop**: Click "Stop" at any time to halt the scan (results so far will be displayed)
4. **Select Files**: Click on files to select them, or use "Select All"
5. **Delete**: Click "Delete Selected Files" to remove unwanted files (confirmation required)

## Interface

The application displays:
- **Size (bytes)**: Exact file size in bytes
- **Size (MB)**: File size in megabytes for easier reading
- **File Path**: Full path to the file

Selected files show their total count and combined size at the bottom.

## Performance

- Scans are performed in a background thread to keep the UI responsive
- Files are periodically sorted during scanning for efficient memory usage
- Handles large directories with thousands of files

## Safety Features

- **Confirmation Dialog**: Deletion requires explicit confirmation
- **Detailed Error Reporting**: Shows which files failed to delete and why
- **Read-Only Protection**: Cannot delete files the user doesn't have permission to access

## File Size Formatting

Sizes are automatically formatted in human-readable units:
- B (Bytes)
- KB (Kilobytes)
- MB (Megabytes)
- GB (Gigabytes)
- TB (Terabytes)
- PB (Petabytes)

## License

Free to use and modify.

## Notes

- Scanning system drives may take considerable time
- Always verify files before deletion - this action cannot be undone
- Some system files may be inaccessible due to permission restrictions
