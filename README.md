# Telegram File Manager Bot

## Overview
This Telegram bot helps users manage files in a private channel. It allows users to upload, access, read, forward, and delete files with simple commands. The bot uses Telegram's API to handle file storage and retrieval efficiently.

## Features
- Upload files to a private channel and save their links.
- Forward files to users based on file names.
- Read file contents directly from the channel.
- Delete files using stored links.
- Prevents multiple tasks from running simultaneously.

## Requirements
- Python 3.8+
- Telegram Bot API Token
- `python-telegram-bot` library
- Firebase (for file metadata storage, optional)


## Usage
### Upload File
Users send a file to the bot, and it asks for a filename before saving it.

### Access File
Command:
```bash
/access filename
```
The bot forwards the requested file from the channel.

### Read File
Command:
```bash
/read filename
```
The bot fetches the file and reads its contents (if it's a text file).

### Delete File
Command:
```bash
/delete filename
```
The bot deletes the file from the private channel.

### Contributions
Feel free to fork the repo, make improvements, and submit a pull request.



