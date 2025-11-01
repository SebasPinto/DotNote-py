# DotNote 📟

> A simple and elegant web interface to display scrolling messages on MAX7219 LED matrix displays using Raspberry Pi

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)
![AI Enhanced](https://img.shields.io/badge/readme-AI--Enhanced-purple.svg)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Support-yellow.svg?style=flat&logo=buy-me-a-coffee)](https://buymeacoffee.com/sebaspinto)

DotNote turns your Raspberry Pi and LED matrix into a customizable message display. Perfect for door signs, notifications, reminders, and creative projects. Control it from any device on your network through a simple web interface or API.

## ✨ Features

- 🌐 **Web-Based Control** - Update messages from any browser on your network
- 📱 **Simple API** - RESTful endpoint for easy integration
- 🔊 **Audio Feedback** - Optional buzzer notification when messages update
- 📝 **Message Logging** - Automatic logging with timestamps and sender IPs
- ⚙️ **Fully Configurable** - Easy-to-customize parameters at the top of the code
- 🔄 **Smooth Scrolling** - Adjustable scroll speed for optimal readability
- 🚀 **Lightweight** - Runs efficiently on Raspberry Pi Zero 2W and above

## 📋 Requirements

### Hardware
- Raspberry Pi (Zero 2W, 3, 4, or 5)
- MAX7219 LED Matrix Display (4x 8x8 modules = 32x8 display)
- Buzzer (optional, any GPIO-compatible buzzer)
- Jumper wires
- MicroSD card with Raspberry Pi OS
- Power supply

### Software
- Raspberry Pi OS (tested on latest version)
- Python 3.12 (also works with 3.7+)
- SPI enabled on Raspberry Pi

## 🔌 Wiring

### MAX7219 LED Matrix

| MAX7219 Pin | Raspberry Pi Pin | GPIO/Function | Physical Pin |
|-------------|------------------|---------------|--------------|
| VCC         | 5V Power         | 5V            | Pin 2 or 4   |
| GND         | Ground           | GND           | Pin 6        |
| DIN         | MOSI             | GPIO 10       | Pin 19       |
| CS          | CE0              | GPIO 8        | Pin 24       |
| CLK         | SCLK             | GPIO 11       | Pin 23       |

### Buzzer (Optional)

| Buzzer Pin | Raspberry Pi Pin | GPIO     | Physical Pin |
|------------|------------------|----------|--------------|
| Positive   | GPIO 23          | GPIO 23  | Pin 16       |
| Negative   | Ground           | GND      | Pin 14       |

> **Note**: The buzzer GPIO pin can be changed in the configuration section of `dotnote.py`

## 🚀 Installation

### 1. Enable SPI

```bash
sudo raspi-config
```

Navigate to: **Interface Options** → **SPI** → **Enable**

Reboot your Raspberry Pi:
```bash
sudo reboot
```

### 2. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev git
```

### 3. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/dotnote.git
cd dotnote

# Install Python dependencies
pip3 install -r requirements.txt
```

### 4. Run DotNote

```bash
python3 dotnote.py
```

The server will start on port 5000. Access it from any device on your network:
```
http://[raspberry-pi-ip]:5000
```

To find your Raspberry Pi's IP address:
```bash
hostname -I
```

## ⚙️ Configuration

All configuration options are at the top of `dotnote.py`. Edit these parameters to customize DotNote:

```python
# LED Matrix Configuration
CASCADED_DEVICES = 4          # Number of 8x8 matrices (4 = 32x8 display)
BLOCK_ORIENTATION = -90       # Rotation: -90, 0, 90, 180
ROTATE = 0                    # Display rotation: 0, 1, 2, 3
BRIGHTNESS = 5                # Brightness: 0-15

# Display Behavior
SCROLL_SPEED = 0.05           # Seconds between scroll steps (lower = faster)
DEFAULT_MESSAGE = "Welcome to DotNote!   "
MESSAGE_SPACING = "   "       # Spacing between message loops

# Buzzer Configuration
BUZZER_ENABLED = True         # Enable/disable buzzer
BUZZER_PIN = 23               # GPIO pin for buzzer
BEEP_DURATION = 0.2           # Beep length in seconds
BEEP_COUNT = 2                # Number of beeps per update

# Server Configuration
SERVER_HOST = '0.0.0.0'       # Listen on all interfaces
SERVER_PORT = 5000            # Web server port

# Logging Configuration
LOG_FILE = "messages.log"     # Log file location
LOG_ENABLED = True            # Enable/disable logging
```

## 🌐 API Usage

### Update Message

```bash
curl "http://raspberry-pi-ip:5000/update?message=Hello%20World"
```

**Response:**
```json
{
  "message": "Message updated"
}
```

**Error Response:**
```json
{
  "error": "No valid message provided"
}
```

### Python Example

```python
import requests

response = requests.get('http://192.168.1.100:5000/update', 
                       params={'message': 'Hello from Python!'})
print(response.json())
```

## 🔧 Running as a Service

To make DotNote start automatically on boot, create a systemd service:

```bash
sudo nano /etc/systemd/system/dotnote.service
```

Add the following content (adjust paths as needed):

```ini
[Unit]
Description=DotNote LED Matrix Display
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/dotnote
ExecStart=/usr/bin/python3 /home/pi/dotnote/dotnote.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable dotnote.service
sudo systemctl start dotnote.service
```

Check service status:

```bash
sudo systemctl status dotnote.service
```

## 💡 Usage Ideas

- 📌 **Office Door Signs** - "In a Meeting", "Available", "Do Not Disturb"
- ☕ **Coffee Shop Menus** - Daily specials and announcements  
- 🏠 **Smart Home** - Display sensor data, weather, or notifications
- 🎉 **Event Spaces** - Welcome messages and event information
- 🛠️ **Workshop Status** - Equipment availability, safety reminders
- 🛒 **Retail** - Promotional messages and customer information
- 🎮 **Gaming Rooms** - Scores, status updates, and notifications
- 👶 **Kids' Rooms** - Fun messages, reminders, and countdowns

## 🐛 Troubleshooting

### SPI not enabled
If you see SPI-related errors:
```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
sudo reboot
```

### LED matrix not displaying
1. Check all wiring connections
2. Verify SPI is enabled: `lsmod | grep spi`
3. Test SPI devices: `ls /dev/spi*` (should show `/dev/spidev0.0`)
4. Try adjusting `BLOCK_ORIENTATION` and `ROTATE` parameters

### Display shows garbled text
Adjust these parameters in `dotnote.py`:
- `BLOCK_ORIENTATION`: Try -90, 0, 90, or 180
- `ROTATE`: Try values 0, 1, 2, or 3

### Can't access web interface
1. Ensure Pi and your device are on the same network
2. Check if service is running: `sudo systemctl status dotnote`
3. Verify firewall settings allow port 5000
4. Try accessing via IP instead of hostname

### Buzzer not working
1. Check buzzer wiring (positive to GPIO 23, negative to GND)
2. Verify `BUZZER_ENABLED = True` in configuration
3. Test with a different GPIO pin by changing `BUZZER_PIN`

## 📁 Project Structure

```
dotnote/
├── dotnote.py           # Main application
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html      # Web interface
└── messages.log        # Message log (generated)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) library
- Flask web framework
- Raspberry Pi community

---

**Made with ❤️ for makers and tinkerers**

If you found this project useful, please give it a ⭐ on GitHub!