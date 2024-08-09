from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import time
import json
import configparser
import pyzipper
from datetime import datetime
import logging
import tempfile
import signal

# Initialize Flask app
app = Flask(__name__)

# Global variables to store events and file history
events = []
file_history = {}

# --- Configure Logging ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/flask_backend_log.txt')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- Load File History on Startup ---
try:
    with open('data/backend_file_history.json', 'r') as f:
        file_history = json.load(f)
    logger.info("File history loaded from data/backend_file_history.json")
except FileNotFoundError:
    logger.info("File history not found. Creating new file history.")
except json.JSONDecodeError:
    logger.error("Error decoding JSON from backend_file_history.json. Creating new file history.")

# --- Load Configuration ---
config = configparser.ConfigParser()
config.read('config/config.ini')
ENABLE_ENCRYPTION = config['General'].getboolean('enable_encryption', False)
ZIP_PASSWORD = config['General'].get('zip_password', '')


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page with configuration and file history."""
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    return render_template('index.html', config=config, file_history=file_history)


@app.route('/update_config', methods=['POST'])
def update_config():
    """Updates the configuration file based on form data from the web interface."""
    config = configparser.ConfigParser()
    config.read('config/config.ini')

    for section in config.sections():
        for key in config[section]:
            if key in request.form:
                config[section][key] = request.form[key]
            # Handle the disable_logs checkbox
            if key == 'disable_logs':
                config['General']['disable_logs'] = 'True' if request.form.get('disable_logs') == 'on' else 'False'

    with open('config/config.ini', 'w') as configfile:
        config.write(configfile)

    # Update the logging level
    if config['General'].getboolean('disable_logs'):
        logger.setLevel(logging.CRITICAL)  # Effectively disables most logging
    else:
        logger.setLevel(logging.DEBUG)  # Re-enable logging

    return redirect(url_for('index'))


@app.route('/monitor')
def monitor():
    """Provides file history data as JSON to the web client."""
    return jsonify(list(map(lambda item: {'file_path': item[0], **item[1]}, file_history.items())))


@app.route('/download/<file_id>')
def download(file_id):
    """Handles file downloads, including decryption for encrypted files."""
    global file_history
    found_file = None
    for file_path, file_data in file_history.items():
        if file_data['file_id'] == int(file_id):
            found_file = file_path
            break

    if found_file:
        logger.info(f"Download requested for file: {found_file}")

        hash_value = file_history[found_file]['hash']
        encrypted = file_history[found_file]['encrypted']
        encryption_algorithm = file_history[found_file]['encryption_algorithm']

        base_name = os.path.basename(found_file)
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, f'{base_name}.zip')

            # Reconstruct the ZIP file from the sent parts
            parts = [f for f in os.listdir(temp_dir) if f.startswith(base_name) and f.endswith('.zip')]
            parts.sort()  # Sort the parts by number

            with open(zip_path, 'wb') as zipf:
                for part in parts:
                    with open(os.path.join(temp_dir, part), 'rb') as chunk:
                        zipf.write(chunk.read())

            # Decrypt the ZIP file if necessary
            if encrypted:
                try:
                    with pyzipper.AESZipFile(zip_path, 'r', encryption=pyzipper.WZ_AES) as zipf:
                        zipf.setpassword(ZIP_PASSWORD.encode())
                        zipf.extractall(path=temp_dir)
                        logger.info(f"File decrypted successfully: {found_file}")
                except Exception as e:
                    logger.error(f"Error decrypting file: {found_file}, {str(e)}")
                    return "Error decrypting file. Please check the password.", 400

            # Download the ZIP file
            return send_from_directory(temp_dir, f'{base_name}.zip', as_attachment=True)
    else:
        logger.warning(f"File not found for download: {file_id}")
        return "File not found.", 404


@app.route('/file_history', methods=['POST'])
def update_file_history():
    """Updates the file history with data received from the Telegram bot."""
    global file_history
    data = request.get_json()
    if data:
        file_history = data
        with open('data/backend_file_history.json', 'w') as f:
            json.dump(file_history, f)
        return "File history updated", 200
    else:
        return "Invalid data", 400


@app.route('/event', methods=['POST'])
def handle_event():
    """Handles events sent from the bot."""
    global events, file_history
    data = request.get_json()
    if data:
        events.append(data)
        if data['type'] == 'success':
            file_history[data['file']] = {
                'hash': data['hash'],
                'last_sent': datetime.now().isoformat(),
                'send_success': True,
                'forward_success': data.get('forward_success'),
                'encrypted': ENABLE_ENCRYPTION,
                'encryption_algorithm': "AES" if ENABLE_ENCRYPTION else "None",
                'file_id': data['file_id'],
                'file_size': data.get('file_size'),
                'processing_time': data.get('processing_time'),
                'upload_speed': data.get('upload_speed')
            }
            save_file_history()
        return "Event received", 200
    else:
        return "Invalid data", 400

# Function to save file history
def save_file_history():
    """Saves the file history to a JSON file."""
    with open('data/backend_file_history.json', 'w') as f:
        json.dump(file_history, f)
    logger.info("File history saved to data/backend_file_history.json")


@app.route('/clear_logs', methods=['POST'])
def clear_logs():
    """Clears the log files for both the bot and the backend."""
    try:
        # Clear bot logs
        bot_log_path = os.path.join('logs', 'bot_log.txt')
        if os.path.exists(bot_log_path):
            with open(bot_log_path, 'w') as f:
                f.truncate(0)
            logger.info(f"Cleared bot log file: {bot_log_path}")

        # Clear backend logs
        backend_log_path = os.path.join('logs', 'flask_backend_log.txt')
        if os.path.exists(backend_log_path):
            with open(backend_log_path, 'w') as f:
                f.truncate(0)
            logger.info(f"Cleared backend log file: {backend_log_path}")

        return "Logs cleared successfully!" # Translated output
    except Exception as e:
        logger.error(f"Error clearing log files: {str(e)}")
        return f"Error clearing log files: {str(e)}", 500


@app.route('/clear_json_data', methods=['POST'])
def clear_json_data():
    """Clears all JSON data files, including bot history, backend history, and the file size cache."""
    global file_history
    try:
        # Clear bot JSON data
        bot_json_path = 'data/bot_file_history.json'
        if os.path.exists(bot_json_path):
            with open(bot_json_path, 'w') as f:
                json.dump({}, f)
            logger.info(f"Cleared bot JSON data file: {bot_json_path}")

        # Clear backend JSON data
        backend_json_path = 'data/backend_file_history.json'
        if os.path.exists(backend_json_path):
            with open(backend_json_path, 'w') as f:
                json.dump({}, f)
            logger.info(f"Cleared backend JSON data file: {backend_json_path}")

        # Clear file size cache
        cache_path = 'data/file_size_cache.json'
        if os.path.exists(cache_path):
            with open(cache_path, 'w') as f:
                json.dump({}, f)
            logger.info(f"Cleared file size cache: {cache_path}")

        file_history = {}
        return "JSON data cleared successfully!" # Translated output
    except Exception as e:
        logger.error(f"Error clearing JSON data: {str(e)}")
        return f"Error clearing JSON data: {str(e)}", 500


# Signal handler for graceful shutdown (SIGINT, SIGTERM)
def signal_handler(sig, frame):
    """Handles graceful shutdown of the Flask app, saving the file history."""
    print('Shutting down gracefully...')
    save_file_history()
    exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    app.run(debug=True)