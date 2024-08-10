# Telegram File Bot (Proof of Concept)

## Disclaimer

This software is provided for academic and research purposes only. The author does not endorse or encourage the use of this software in violation of the Terms of Service of any platform, including Telegram. Use of this software is at your own risk.

## Project Description

This repository contains a proof-of-concept (PoC) implementation of a Telegram bot designed to automatically upload and monitor files from a specified local directory. This project aims to demonstrate the capabilities and limitations of using Telegram as a rudimentary file storage and retrieval system. The bot is not intended for production use and might violate Telegram's Terms of Service if used inappropriately.

## Features

- **Automatic File Uploads:**  The bot monitors a designated folder and uploads any new or modified files to a specified Telegram chat. 
- **Duplicate File Prevention:**  The bot calculates MD5 hashes of files to prevent uploading duplicate content.
- **File Compression:** Files can be optionally compressed using the ZIP format before uploading. The compression level is configurable (default, fast, or no compression).
- **File Encryption:**  The bot provides the option to encrypt compressed files using a password. Encryption is performed using the AES algorithm. 
- **Large File Splitting:** Files exceeding Telegram's file size limit are automatically split into smaller parts and uploaded individually. The bot provides instructions to the user on how to reassemble the split files. 
- **File Size Caching:**  To optimize the upload process, the bot can create and use a cache of file sizes to prioritize sending smaller files first. 
- **Logging Control:** The bot and its accompanying web interface provide options to enable or disable logging, allowing for flexible control over the level of detail recorded.
- **Log Rotation:** Log files are automatically rotated to prevent them from growing too large.
- **Web Interface for Management:** A Flask-based web application provides a user interface to monitor the bot's activities, view file history, download uploaded files, and manage configuration settings.
- **Real-Time Statistics:** The web interface displays real-time statistics about the bot's performance, including the number of processed and sent files, average upload speed, and average processing time.

## Technical Implementation

**Bot (`bot.py`)**

- The bot is implemented using the `python-telegram-bot` library to interact with the Telegram Bot API.
- The `asyncio` library is used for asynchronous operations, such as file uploads and monitoring. 
- File hashing is performed using the `hashlib` library.
- Compression and encryption are handled using the `zipfile` (for standard compression) and `pyzipper` (for encrypted archives) libraries.
- Configuration settings are read from a `config.ini` file using the `configparser` library.
- Rate limiting for Telegram API calls is implemented using the `aiolimiter` library.
- Type hinting is used throughout the code for improved readability and error detection.
- The `aiohttp` library is used for making asynchronous HTTP requests to the backend. 

**Web Backend (`flask_backend.py`)**

- The web backend is implemented using the Flask web framework.
- It provides REST endpoints for:
    - Displaying the web interface (`/`)
    - Updating the bot's configuration (`/update_config`)
    - Monitoring the file history (`/monitor`)
    - Downloading uploaded files (`/download/<file_id>`)
    - Clearing log files (`/clear_logs`)
    - Clearing JSON data (`/clear_json_data`)

**Communication:**

- The bot and backend communicate through HTTP requests. The bot sends events to the backend to update the file history and other information.

## Requirements

- Python 3.9 or higher
- The following Python libraries (install using `pip install -r requirements.txt`):

```
python-telegram-bot
Flask
cryptography
certifi
httpcore
httpx
pyzipper
requests
configparser
zipfile
aiolimiter
aiohttp 
```

**Additional Installation Steps**

- If you experience issues, you might need to upgrade `Flask` and `werkzeug`:
```
    pip install --upgrade flask werkzeug
```
- If you encounter problems with the Telegram bot, upgrade `python-telegram-bot`:
```
    pip install --upgrade python-telegram-bot
```

## Installation

1. Clone the Repository:
```
   git clone https://github.com/Andrew3000s/telegram_freestorage_poc.git
   ```

2. **Navigate to the Project Directory:**
   ```
   cd telegram_freestorage_poc
   ```

3. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Configure the Bot:**
   - Open the `config/config.ini` file.
   - Replace the following placeholders with your actual values:
      - `token`: Your Telegram Bot API token.
      - `chat_id`: The ID of the Telegram chat where the bot should send files. 
      - `forward_chat_id`: (Optional) Chat ID to forward files to (set to `0` to disable forwarding).
      - `zip_password`: (Optional) Password for encrypted ZIP files. 
      - `folders_to_monitor`: Comma-separated list of folders to monitor for new or modified files.
      - **Adjust other settings** as needed.

5. **Run the Flask Backend:**
   ```
   python flask_server.py
   ```

6. **Run the Telegram Bot:** 
   ```
   python bot.py
   ```

## Configuration

1. **Obtain a Telegram Bot Token:**
   - Go to the [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
   - Send the `/newbot` command to create a new bot.
   - Follow the BotFather's instructions to provide a name and username for your bot.
   - The BotFather will provide you with a unique API **token** for your bot. Save this token securely, as it's essential for your bot to authenticate with the Telegram API.

2. **Determine the Chat ID:**
   - There are a couple of ways to find the Chat ID:
     - **Add your bot to the target group or channel.** Then, use the Telegram API method `getUpdates` (see [https://core.telegram.org/bots/api#getupdates](https://core.telegram.org/bots/api#getupdates)).  Send a message in the group, and the `getUpdates` method will return JSON data that includes the chat ID.
     - **Use a dedicated bot to get Chat IDs**. There are bots like [@getidsbot](https://t.me/getidsbot) that can provide you with the ID of a chat.

3. **Create the Configuration File (`config.ini`):**
   - Create a file named `config.ini` in the `config` directory of the project.
   - Add the following sections and settings, replacing the placeholders with your actual values:

   ```ini
   [Telegram]
   token = YOUR_TELEGRAM_BOT_TOKEN 
   chat_id = YOUR_TELEGRAM_CHAT_ID
   forward_chat_id = 0  ; Optional: Chat ID to forward messages to (0 to disable forwarding)
   enable_forward = False ; Set to True to enable forwarding

   [General]
   folders_to_monitor = /path/to/your/folder1, /path/to/your/folder2  ; Comma-separated paths
   check_interval = 60 ; Check for new files every 60 seconds
   log_retention_days = 7 ; Keep log files for 7 days
   enable_encryption = False ; Set to True to enable encryption for zipped files
   zip_password = YOUR_PASSWORD  ; Password for encrypted ZIP files (if enabled)
   allowed_extensions = .exe, .pdf, .txt ; Comma-separated allowed extensions (leave blank for all)
   compression_level = default ; Compression level for ZIP files (default, fast, none)
   enable_cache = True ; Set to False to disable file size caching
   disable_logs = False ; Set to True to disable logging
   ```

   - **Explanation of Settings:**
     - **`token`:** Your Telegram Bot API token obtained from the BotFather.
     - **`chat_id`:** The ID of the Telegram chat where the bot should send files.
     - **`forward_chat_id`:**  (Optional) Chat ID to forward files to. Set to `0` to disable forwarding.
     - **`enable_forward`:** Set to `True` to enable forwarding of files.
     - **`folders_to_monitor`:**  Comma-separated list of folder paths that the bot should monitor for new or modified files.
     - **`check_interval`:** How often (in seconds) the bot checks for new files in the monitored folders.
     - **`log_retention_days`:** The number of days to keep log files before they are automatically deleted.
     - **`enable_encryption`:** Set to `True` to enable encryption for zipped files.
     - **`zip_password`:** The password used to encrypt zipped files (only if `enable_encryption` is `True`).
     - **`allowed_extensions`:** (Optional) Comma-separated list of allowed file extensions. Leave blank to allow all file extensions.
     - **`compression_level`:** The compression level used for zipping files (`default`, `fast`, or `none`).
     - **`enable_cache`:** Set to `True` to enable the file size cache for prioritizing smaller file uploads. 
     - **`disable_logs`:** Set to `True` to disable logging for both the bot and the backend.

**Important Notes:**

- Use forward slashes (/) for file paths, even on Windows.
- Ensure that the folders specified in `folders_to_monitor` exist and are accessible to the bot. 
- Choose a strong and unique password for `zip_password` if you enable encryption.  **It's highly recommended to store this password in an environment variable or use a secrets management system instead of hardcoding it in the `config.ini` file.** 

## Usage

1. **Start the bot and backend:** Follow the installation instructions above.
2. **Add files to the monitored folders:** The bot will automatically detect, process, and upload any new or modified files in the specified directories.
3. **Access the Web Interface:** Open a web browser and go to `http://127.0.0.1:5000/` (or the address where your Flask backend is running) to monitor the bot's activity, view file history, download files, and manage settings.


## API Documentation

The Telegram File Bot exposes several API endpoints through its Flask backend. These endpoints allow for interaction with the bot's functionality and retrieval of information.

### 1. Update Configuration

- **Endpoint:** `/update_config`
- **Method:** POST
- **Description:** Updates the bot's configuration based on form data.
- **Request Body:** Form data containing configuration key-value pairs
- **Response:** Redirects to the index page on success

### 2. Monitor File History

- **Endpoint:** `/monitor`
- **Method:** GET
- **Description:** Retrieves the current file history.
- **Response:** JSON array of file history objects
  ```json
  [
    {
      "file_path": "/path/to/file",
      "hash": "file_hash",
      "last_sent": "2023-08-09T12:34:56",
      "send_success": true,
      "encrypted": false,
      "file_id": 1,
      "file_size": 1024,
      "processing_time": 1.5,
      "upload_speed": 512
    },
    // ... more file entries
  ]
  ```

### 3. Download File

- **Endpoint:** `/download/<file_id>`
- **Method:** GET
- **Description:** Initiates download of a specific file.
- **Parameters:** 
  - `file_id`: The ID of the file to download
- **Response:** File download or error message

### 4. Clear Logs

- **Endpoint:** `/clear_logs`
- **Method:** POST
- **Description:** Clears both bot and backend log files.
- **Response:** Success message or error details

### 5. Clear JSON Data

- **Endpoint:** `/clear_json_data`
- **Method:** POST
- **Description:** Clears all JSON data files including bot history, backend history, and file size cache.
- **Response:** Success message or error details

### 6. File History Update

- **Endpoint:** `/file_history`
- **Method:** POST
- **Description:** Updates the file history with data received from the Telegram bot.
- **Request Body:** JSON object containing file history data
- **Response:** Success message or error status

### 7. Handle Event

- **Endpoint:** `/event`
- **Method:** POST
- **Description:** Handles events sent from the bot, such as successful file uploads.
- **Request Body:** JSON object containing event data
  ```json
  {
    "type": "success",
    "file": "filename.ext",
    "hash": "file_hash",
    "file_id": 1,
    "file_size": 1024,
    "processing_time": 1.5,
    "upload_speed": 512
  }
  ```
- **Response:** Success message or error status

Note: All endpoints except for `/monitor` and `/download/<file_id>` require authentication in a production environment. Ensure proper security measures are implemented before exposing these endpoints publicly.


## Security Considerations

**Bot Token:** 

- Keep your Telegram Bot token **confidential**. 
- **Never share it publicly** or commit it to version control systems like GitHub. 
- If you suspect your token has been compromised, **regenerate it immediately** using the BotFather.

**Encryption Password:**

- If you enable file encryption, choose a **strong, unique password**. 
- **Do not reuse passwords** from other services. 
- **Instead of hardcoding the password in the `config.ini` file, store it securely using an environment variable or a secrets management system.**

**Monitored Folders:**

- Be cautious about which folders you choose to monitor. 
- **Avoid monitoring folders containing sensitive personal or business information** unless absolutely necessary.

**Access Control:**

- **Limit access to the chat or channel** where the bot sends files. 
- Remember that anyone with access to this chat can potentially download the files sent by the bot.

**Web Interface:**

- The Flask backend is set up for **local use by default**. 
- If you plan to make the web interface accessible over a network:
    - **Implement proper authentication.**
    - **Use HTTPS to encrypt traffic.**

**Regular Audits:**

- **Periodically review the bot's activities and the contents of the monitored folders** to ensure no unauthorized access or unexpected behavior.

Remember, this is a proof-of-concept project and may not implement all security best practices required for a production environment. Use caution when deploying this bot, especially in scenarios involving sensitive data.


## Images

![image](https://github.com/Andrew3000s/telegram_freestorage_poc/blob/main/images/bot_in_action.png)
![image](https://github.com/Andrew3000s/telegram_freestorage_poc/blob/main/images/server_in_action.png)
![image](https://github.com/Andrew3000s/telegram_freestorage_poc/blob/main/images/telegram.png)
![image](https://github.com/Andrew3000s/telegram_freestorage_poc/blob/main/images/web_interface.png)

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, please feel free to submit a pull request.

## License

MIT License

Copyright (c) [2024] [Andrea Paone]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
