# ASCII CAM 

A real-time ASCII art generator that converts webcam feed into beautiful text-based art using Python and PySide6.

![Python](https://img.shields.io/badge/Python-3.12.4-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.7.2-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11.0.86-red.svg)

## 🌟 Features

- **Real-time ASCII conversion**: Live webcam feed transformed into ASCII art
- **Adjustable resolution**: Control the detail level with an interactive slider
- **Multiple display modes**: Toggle between camera view, ASCII grid, and overlay modes
- **Image capture**: Save snapshots of your ASCII art
- **Customizable character sets**: Multiple ASCII character ramps for different visual effects

## 🚀 Quick Start

### Prerequisites

- Python 3.12.4 or higher
- A working webcam

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd InternTask
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🎮 How to Use

1. **Launch the app** - A file dialog will appear asking you to select a directory for saving images
2. **Select save directory** - Choose where you want to save captured images (required to proceed)
3. **Adjust resolution** - Use the slider at the bottom to control ASCII art detail level
4. **Toggle display modes** - Use the display button to cycle through:
   - Camera view with ASCII overlay
   - Pure ASCII grid
   - White background with ASCII
5. **Capture images** - Click the save button to capture the current ASCII art

## 🛠️ How It Works

1. **Camera Input**: Captures live video feed from your webcam
2. **Resolution Reduction**: Downsamples the image based on slider settings
3. **Grayscale Conversion**: Converts BGR color space to grayscale
4. **Pixel Mapping**: Maps grayscale values (0-255) to ASCII characters
5. **Character Selection**: Uses lookup tables with different character densities
6. **Real-time Display**: Renders ASCII art overlay on the video feed

## 📁 Project Structure

```
InternTask/
├── main.py           # Main application with GUI and ASCII conversion logic
├── camera.py         # Camera handling and frame processing
├── requirements.txt  # Python dependencies
└── readme.md        # Project documentation
```

## 🎨 Character Sets

The application includes multiple ASCII character ramps:

- **5 chars**: `█▓▒░ ` (Simple blocks)
- **7 chars**: `█▓▒░+. ` (Blocks with symbols)
- **9 chars**: `█▓▒░+=-.` (Default - balanced detail)
- **11 chars**: `█@%#*+=-:. ` (High contrast)
- **16 chars**: `$@B%8&WM#*oahkb ` (Maximum detail)

## 🔧 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | 6.7.2 | GUI framework and Qt bindings |
| opencv-contrib-python | 4.11.0.86 | Computer vision and camera handling |

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Troubleshooting

**Camera not detected?**
- Ensure your webcam is connected and not being used by another application
- Try changing the camera source in `camera.py` (default is `src=0`)

**Performance issues?**
- Lower the resolution using the slider
- Close other applications that might be using system resources

