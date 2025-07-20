# ASCII CAM 

A real-time ASCII art generator that converts webcam feed into beautiful text-based art using Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.12.4-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.7.2-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0.86-red.svg)
![PyInstaller](https://img.shields.io/badge/PyInstaller-6.14.2-orange.svg)

## Features

- **Real-time ASCII conversion**: Live webcam feed transformed into ASCII art with 3x5 aspect ratio blocks
- **Adjustable block size**: Fine-grained control over ASCII art detail level
- **Multiple character sets**: 5 different ASCII character ramps for varying visual effects
- **Image upload support**: Process static images in addition to live camera feed
- **Camera controls**: Freeze/unfreeze camera feed for static viewing
- **Flexible display modes**: Toggle between camera view and white background
- **Image capture**: Save snapshots with automatic timestamping
- **ASCII text export**: Copy ASCII art directly to clipboard
- **Threaded processing**: Smooth performance with background image processing
- **Hardware-aware camera control**: Efficient camera resource management

## Quick Start

### Prerequisites

- Python 3.12.4 or higher
- A working webcam

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Taylor-Nilsen/ASCII-CAM.git
   cd ASCII-CAM
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## How to Use

1. **Launch the application** - Run `python main.py` to start the ASCII camera
2. **Camera controls** - The application will automatically start capturing from your webcam
3. **Adjust block size** - Use the top slider to control ASCII art detail level (larger values = more detail)
4. **Select character set** - Use the bottom slider to choose between 5 different ASCII character ramps
5. **Toggle display** - Use the display button to switch between camera feed and white background
6. **Freeze frame** - Click "Freeze" to pause the camera feed for static viewing
7. **Upload images** - Use "Upload Image" to process static images instead of camera feed
8. **Save captures** - Click "Save Image" to save the current view (directory selection on first save)
9. **Copy ASCII** - Use "Copy ASCII Text" to copy the text representation to clipboard

## Technical Details

**3x5 Aspect Ratio Blocks**: Each ASCII character represents a 3-pixel wide by 5-pixel tall block, providing optimal character proportions for text-based art.

**Threading Architecture**: Heavy image processing operations run in background threads to maintain responsive UI performance.

**Camera Management**: Automatic camera resource management with proper pause/resume functionality to prevent hardware conflicts.

## How It Works

1. **Camera Input**: Captures live video feed from webcam using OpenCV
2. **Block Processing**: Divides image into 3x5 pixel blocks for optimal ASCII character mapping
3. **Grayscale Conversion**: Converts color image to grayscale for brightness analysis
4. **Brightness Mapping**: Maps average block brightness to ASCII characters by intensity
5. **Character Selection**: Uses predefined character ramps with varying density levels
6. **Real-time Rendering**: Updates display at ~30 FPS with threaded processing for smooth performance
7. **Resource Management**: Automatically pauses camera when not needed to conserve system resources

## Project Structure

```
ASCII-CAM/
├── main.py           # Main GUI application with threading and controls
├── camera.py         # Camera class with 3x5 block processing
├── requirements.txt  # Python dependencies
├── readme.md        # Project documentation
└── .gitignore       # Git ignore rules
```

## Character Sets

The application includes multiple ASCII character ramps for different visual effects:

- **5 characters**: `█▓▒░ ` (Simple blocks - high contrast)
- **7 characters**: `█▓▒░+. ` (Blocks with basic symbols)
- **9 characters**: `█▓▒░+=-.` (Balanced detail level)
- **11 characters**: `█@%#*+=-:. ` (Default - high contrast with symbols)
- **16 characters**: `$@B%8&WM#*oahkb ` (Maximum detail and variation)

## License

This project is open source and available under the MIT License.

## Troubleshooting

**Camera not detected?**
- Ensure your webcam is connected and not being used by another application
- Try changing the camera source in `camera.py` (default is `src=0`)
- Check camera permissions in your system settings

**Performance issues?**
- Use a smaller block size setting (lower slider value)
- Close other resource-intensive applications
- Ensure adequate system memory is available

**Threading errors?**
- Restart the application if worker threads become unresponsive
- Check that camera hardware supports the requested resolution

