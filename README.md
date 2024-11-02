# DhakaFlix Searcher

DhakaFlix Searcher is a web application that allows users to search for files like movies, anime, games, and more across multiple servers of [DhakaFlix](http://172.16.50.4/). This project uses Flask for the backend and multithreading to improve search speed by querying servers concurrently.

## Screenshots
![image](https://github.com/user-attachments/assets/ba361ada-1f1a-4d3a-9582-5bdc2f3adf67)
![image](https://github.com/user-attachments/assets/c1629660-59d8-4a5a-abff-b97d67bd660d)



## Features

- Search for files across multiple servers
- Supports file types: `.mp3`, `.mp4`, `.mkv`, `.iso`, `.zip` and so on
- Display icons based on file type (e.g., movie, archive, music)
- Smooth animations and transitions in the UI
- Multithreaded requests to improve performance

## Why this tool?

Searching and finding files in the web server is super slow because of multiple directories. So, this tool can come in handy for this kind of things. Its being useful to me. So, I thought why not put it here, some people might find it useful as well.

## Prerequisites

- Python 3.x
- Flask
- Requests

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/f4rh4d-4hmed/DhakaFlix-Searcher.git
   cd DhakaFlix-Searcher
   ```
2. Install required library
    ```bash
    pip install requirements.txt
    ```
3. Run the app
   ```bash
   python3 app.py
   ```
4. Running is done. If DhakaFlix is unlocked in your area the app should work perfectly. Open http://127.0.0.1:5000/ or localhost:5000 to use the app locally.
5. If you want to use it remotly you may use [ngrok](https://download.ngrok.com/windows?tab=download)

## Builds
There is a Compiled Python and Compiled Node.js with Electron build available for Windows only. You can try it out from release page.
Tasted on x64 bit of Windows 7 and 10
