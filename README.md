# DhakaFlix Searcher

DhakaFlix Searcher is a web application that allows users to search for files like movies, anime, games, and more across multiple servers of [DhakaFlix](http://172.16.50.4/). This project uses Flask for the backend and multithreading to improve search speed by querying servers concurrently.

## Screenshots
<img width="1127" height="789" alt="image" src="https://github.com/user-attachments/assets/1dec7df2-6a8a-4395-9351-df3f69617a92" />
<img width="1127" height="789" alt="image" src="https://github.com/user-attachments/assets/28db422d-7e7e-4516-aff9-6341089edbed" />




## Features

- Supports file types: `.mp3`, `.mp4`, `.mkv`, `.iso`, `.zip` and so on
- Display icons based on file type (e.g., movie, archive, music)
- Smooth animations and transitions in the UI
- Multithreaded requests to improve performance
- Make video playlist to stream online using VLC or similler apps

## Why this tool?

Because It makes life easier:)

## Prerequisites

- Python 3.x
- bs4
- requests
- PyQt6

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/f4rh4d-4hmed/DhakaFlix-Searcher.git
   cd DhakaFlix-Searcher
   ```
2. Install required library
    ```bash
    pip install -r requirements.txt
    ```
3. Run the app
   ```bash
   python3 app.py
   ```
## Termux
Why would somebody use it in termux? Well I have no idea, here I found a way to ran it in termux.
1. Install Termux and Termux-X11, Setup xfce4 environment in proot-distro (Ubuntu Recommend), more information can be found in official Termux-X11 repo.
2. Install requests, bs4 manually. than install PyQt6
```bash
pip install requests bs4
apt install python3-PyQt6
```
3. Now clone this repo and setup venv
```bash
git clone https://github.com/f4rh4d-4hmed/DhakaFlix-Searcher/tree/main
cd DhakaFlix-Searcher
#You may have to use sudo but try without sudo first
python3 -m venv my_env --system-site-packages
source my_env/bin/activate
```
4. Now run the app
```
python3 app.py
```
Of course I expect you to know about the Termux-X11 first before trying this.
# EOL
