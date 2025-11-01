#!/usr/bin/env python3
"""
DotNote - LED Matrix Message Display
A simple web-based interface to display scrolling messages on MAX7219 LED matrix displays
"""

import time
import threading
from flask import Flask, request, jsonify, render_template
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.legacy import show_message
from luma.core.legacy.font import CP437_FONT, proportional
from gpiozero import Buzzer

# ============================================================================
# CONFIGURATION PARAMETERS - Customize these to fit your setup
# ============================================================================

# LED Matrix Configuration
CASCADED_DEVICES = 4          # Number of 8x8 LED matrices connected in series
BLOCK_ORIENTATION = -90       # Rotation of individual blocks (-90, 0, 90, 180)
ROTATE = 0                    # Overall display rotation (0, 1, 2, 3)
BRIGHTNESS = 5                # LED brightness level (0-15, where 15 is brightest)

# Display Behavior
SCROLL_SPEED = 0.05           # Scroll delay in seconds (lower = faster scrolling)
DEFAULT_MESSAGE = "Welcome to DotNote!   "  # Message shown on startup
MESSAGE_SPACING = "   "       # Spaces added at the end of messages for separation

# Buzzer Configuration
BUZZER_ENABLED = True         # Set to False to disable buzzer functionality
BUZZER_PIN = 23               # GPIO pin number for the buzzer
BEEP_DURATION = 0.2           # Duration of each beep in seconds
BEEP_COUNT = 2                # Number of beeps when message is updated

# Server Configuration
SERVER_HOST = '0.0.0.0'       # Listen on all network interfaces
SERVER_PORT = 5000            # Port for the web server

# Logging Configuration
LOG_FILE = "messages.log"     # File where messages will be logged
LOG_ENABLED = True            # Set to False to disable message logging

# ============================================================================
# APPLICATION INITIALIZATION
# ============================================================================

app = Flask(__name__)

# Initialize LED matrix device
serial = spi(port=0, device=0, gpio=noop())
device = max7219(
    serial, 
    cascaded=CASCADED_DEVICES, 
    block_orientation=BLOCK_ORIENTATION, 
    rotate=ROTATE
)
device.contrast(BRIGHTNESS)

# Initialize buzzer if enabled
buzzer = Buzzer(BUZZER_PIN) if BUZZER_ENABLED else None

# Global variable for current message and thread lock to prevent race conditions
current_message = DEFAULT_MESSAGE
message_lock = threading.Lock()

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def display_loop():
    """
    Continuous loop that displays the current message on the LED matrix.
    Runs in a separate thread and handles character encoding errors gracefully.
    """
    global current_message
    while True:
        with message_lock:
            msg = current_message
        try:
            # Display the message with scrolling effect using lower scroll_delay for faster scrolling
            show_message(
                device, 
                msg, 
                fill="white", 
                font=proportional(CP437_FONT), 
                scroll_delay=SCROLL_SPEED
            )
        except Exception as e:
            print(f"Error displaying message: {e}")
            # Set error message if display fails (e.g., unsupported character)
            with message_lock:
                current_message = "Error: Unsupported character   "
        time.sleep(0.1)


def beep():
    """
    Emits a beep pattern using the buzzer.
    Two short beeps (0.2s on and 0.2s off between them)
    """
    if BUZZER_ENABLED and buzzer:
        buzzer.beep(
            on_time=BEEP_DURATION, 
            off_time=BEEP_DURATION, 
            n=BEEP_COUNT, 
            background=False
        )


def log_message(message, ip):
    """
    Logs the received message along with timestamp and sender's IP address.
    Saves to the log file specified in configuration.
    
    Args:
        message (str): The message to log
        ip (str): IP address of the sender
    """
    if not LOG_ENABLED:
        return
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"{timestamp} - {ip} - {message.strip()}\n"
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error writing to log: {e}")


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Render the main DotNote web interface"""
    return render_template('index.html')


@app.route('/update', methods=['GET'])
def update_message():
    """
    API endpoint to update the displayed message via URL parameter.
    
    Usage: /update?message=Your%20Message%20Here
    
    Returns:
        JSON response with success/error status
        - On success: {'message': 'Message updated'}, HTTP 200
        - On error: {'error': 'No valid message provided'}, HTTP 400
    
    Side effects:
        - Updates the global current_message variable
        - Logs the message with timestamp and sender IP
        - Triggers buzzer beep pattern (if enabled)
    """
    global current_message
    
    new_message = request.args.get('message')
    
    # Validate message
    if not new_message or new_message.strip() == "":
        return jsonify({'error': 'No valid message provided'}), 400
    
    # Add spacing at the end for smooth scrolling separation
    new_message = new_message + MESSAGE_SPACING
    
    # Update the message thread-safely
    with message_lock:
        current_message = new_message
    
    # Log the message with sender's IP
    ip = request.remote_addr
    log_message(new_message, ip)
    
    # Trigger beep notification in separate thread to avoid blocking response
    if BUZZER_ENABLED:
        threading.Thread(target=beep, daemon=True).start()
    
    return jsonify({'message': 'Message updated'}), 200


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    # Start the display loop in a daemon thread
    display_thread = threading.Thread(target=display_loop, daemon=True)
    display_thread.start()
    
    # Start the Flask web server
    app.run(host=SERVER_HOST, port=SERVER_PORT)