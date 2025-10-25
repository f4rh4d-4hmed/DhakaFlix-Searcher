import sys
import re
import urllib.parse
from pathlib import Path
from typing import List, Dict
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QTreeWidget, 
                             QTreeWidgetItem, QLabel, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFontDatabase, QFont
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVERS = {
    "DHAKA-FLIX-7": "http://172.16.50.7/DHAKA-FLIX-7/",
    "DHAKA-FLIX-8": "http://172.16.50.8/DHAKA-FLIX-8/",
    "DHAKA-FLIX-9": "http://172.16.50.9/DHAKA-FLIX-9/",
    "DHAKA-FLIX-12": "http://172.16.50.12/DHAKA-FLIX-12/",
    "DHAKA-FLIX-14": "http://172.16.50.14/DHAKA-FLIX-14/",
}

ALLOWED_EXTENSIONS = ['.mp3', '.mp4', '.mkv', '.iso', '.zip']
TIMEOUT = 30


class SearchWorker(QThread):
    progress = pyqtSignal(str)
    result_found = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, search_term: str, servers: Dict[str, str]):
        super().__init__()
        self.search_term = search_term
        self.servers = servers
        self.stopped = False
        
    def stop(self):
        self.stopped = True
    
    def has_allowed_extension(self, filename: str) -> bool:
        return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
    
    def get_parent_folder_name(self, href: str) -> str:
        # Remove trailing filename and get parent folder
        path_parts = href.rstrip('/').split('/')
        if len(path_parts) >= 2:
            return urllib.parse.unquote(path_parts[-2])
        return "Root"
    
    def fetch_server_results(self, server_name: str, base_url: str) -> List[Dict]:
        if self.stopped:
            return []
        
        search_results = []
        request_json = {
            "action": "get",
            "search": {
                "href": f"/{server_name}/",
                "pattern": self.search_term,
                "ignorecase": True
            }
        }
        
        try:
            self.progress.emit(f"Searching {server_name}...")
            response = requests.post(base_url, json=request_json, timeout=TIMEOUT)
            response.raise_for_status()
            response_data = response.json()
            
            for item in response_data.get("search", []):
                if self.stopped:
                    break
                
                href = item.get("href")
                if not href or not self.has_allowed_extension(href):
                    continue
                
                if href.startswith(f"/{server_name}"):
                    full_link = base_url.rstrip('/') + href.replace(f"/{server_name}", '', 1)
                else:
                    full_link = base_url.rstrip('/') + href
                
                filename = urllib.parse.unquote(href.split('/')[-1])
                ext = '.' + filename.split('.')[-1].lower()
                parent_folder = self.get_parent_folder_name(href)
                
                size_text = "Unknown"
                if isinstance(item, dict):
                    size_bytes = item.get("size")
                    if size_bytes:
                        size_text = self.format_size(size_bytes)
                
                search_results.append({
                    "name": filename,
                    "url": full_link,
                    "extension": ext,
                    "size": size_text,
                    "parent_folder": parent_folder,
                    "server": server_name
                })
                
        except requests.Timeout:
            self.error.emit(f"Timeout searching {server_name}")
        except requests.RequestException as e:
            self.error.emit(f"Error searching {server_name}: {str(e)}")
        except Exception as e:
            self.error.emit(f"Unexpected error with {server_name}: {str(e)}")
        
        return search_results
    
    def format_size(self, size_bytes: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def group_results(self, all_results: List[Dict]) -> Dict[str, Dict]:
        grouped = {}
        
        for result in all_results:
            folder_key = result['parent_folder']
            
            if folder_key not in grouped:
                grouped[folder_key] = {
                    'folder_name': folder_key,
                    'files': []
                }
            
            grouped[folder_key]['files'].append({
                'name': result['name'],
                'url': result['url'],
                'size': result['size'],
                'extension': result['extension'],
                'server': result['server']
            })
        
        return grouped
    
    def run(self):
        try:
            all_results = []
            
            with ThreadPoolExecutor(max_workers=len(self.servers)) as executor:
                future_to_server = {
                    executor.submit(self.fetch_server_results, server_name, base_url): server_name
                    for server_name, base_url in self.servers.items()
                }
                
                for future in as_completed(future_to_server):
                    if self.stopped:
                        break
                    
                    server_name = future_to_server[future]
                    try:
                        results = future.result()
                        all_results.extend(results)
                        if results:
                            self.progress.emit(f"Found {len(results)} results in {server_name}")
                    except Exception as e:
                        self.error.emit(f"Error processing {server_name}: {str(e)}")
            
            grouped_results = self.group_results(all_results)
            
            for folder_key, data in grouped_results.items():
                if self.stopped:
                    break
                self.result_found.emit(data)
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Search error: {str(e)}")
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search the BDIX")
        self.setGeometry(100, 100, 900, 600)
        self.search_worker = None
        
        self.init_ui()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        
        font_id = QFontDatabase.addApplicationFont("Jaro-Regular.ttf")
        if font_id == -1:
            print("❌ Failed to load custom font.")
        else:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family, 24)

        title_label = QLabel("Search the BDIX")
        title_label.setFont(custom_font)
        title_label.setStyleSheet("""
            font-weight: bold;
            padding: 10px;
            letter-spacing: 1px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for movie, cartoons, tv series and more here")
        self.search_input.setStyleSheet("padding: 10px; font-size: 14px;")
        self.search_input.returnPressed.connect(self.start_search)
        
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("padding: 10px 20px; font-size: 14px;")
        self.search_button.clicked.connect(self.start_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { text-align: center; }")
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Name", "Size", "Action"])
        self.results_tree.setColumnWidth(0, 500)
        self.results_tree.setColumnWidth(1, 100)
        self.results_tree.setStyleSheet("""
            QTreeWidget {
                font-size: 13px;
                background-color: #2b2b2b;
                color: white;
                border: none;
            }
            QTreeWidget::item {
                padding: 5px;
            }
            QTreeWidget::item:hover {
                background-color: #3b3b3b;
            }
        """)
        layout.addWidget(self.results_tree)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QLineEdit {
                background-color: #2b2b2b;
                border: 1px solid #3b3b3b;
                border-radius: 5px;
                color: white;
            }
            QPushButton {
                background-color: #0d7377;
                border: none;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f63;
            }
        """)
    
    def start_search(self):
        search_term = self.search_input.text().strip()
        
        if not search_term:
            QMessageBox.warning(self, "Input Required", "Please enter a search term")
            return
        
        if len(search_term) < 3:
            QMessageBox.warning(self, "Search Term Too Short", "Please enter at least 3 characters")
            return
        
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait()
        
        self.results_tree.clear()
        self.status_label.setText(f"Searching for: {search_term}")
        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.search_button.setEnabled(False)
        
        self.search_worker = SearchWorker(search_term, SERVERS)
        self.search_worker.progress.connect(self.update_progress)
        self.search_worker.result_found.connect(self.add_result)
        self.search_worker.finished.connect(self.search_finished)
        self.search_worker.error.connect(self.show_error)
        self.search_worker.start()
    
    def update_progress(self, message: str):
        self.status_label.setText(message)
    
    def add_result(self, result: Dict):
        folder_name = result['folder_name']
        files = result['files']
        
        parent_item = QTreeWidgetItem(self.results_tree)
        parent_item.setText(0, f"📁 {folder_name}")
        parent_item.setText(1, f"{len(files)} files")
        parent_item.setExpanded(False)  # Start collapsed for performance
        
        from PyQt6.QtGui import QBrush, QColor
        parent_item.setForeground(0, QBrush(QColor("#4CAF50")))  # Green for folders
        parent_item.setForeground(1, QBrush(QColor("#888888")))  # Gray for count
        
        video_audio_files = [f for f in files if f['extension'] in ['.mp3', '.mp4', '.mkv']]
        
        if len(video_audio_files) > 0:
            playlist_btn = QPushButton("Download Playlist")
            playlist_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7b2cbf;
                    padding: 5px 15px;
                    font-size: 11px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #9d4edd;
                }
            """)
            playlist_btn.clicked.connect(lambda: self.create_playlist(folder_name, video_audio_files))
            self.results_tree.setItemWidget(parent_item, 2, playlist_btn)
        

        for file_info in files:
            file_item = QTreeWidgetItem(parent_item)
            
            # Add icon based on extension
            ext = file_info['extension']
            if ext in ['.mp4', '.mkv']:
                icon = "🎬"
            elif ext == '.mp3':
                icon = "🎵"
            elif ext == '.iso':
                icon = "💿"
            elif ext == '.zip':
                icon = "📦"
            else:
                icon = "📄"
            
            file_item.setText(0, f"{icon} {file_info['name']}")
            file_item.setText(1, file_info['size'])
            

            file_item.setForeground(0, QBrush(QColor("#E0E0E0")))  # Light gray for files
            file_item.setForeground(1, QBrush(QColor("#FFA726")))  # Orange for size
            

            download_btn = QPushButton("Download")
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0d7377;
                    padding: 5px 15px;
                    font-size: 11px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #14a085;
                }
            """)
            download_btn.clicked.connect(lambda checked, url=file_info['url']: self.open_download(url))
            self.results_tree.setItemWidget(file_item, 2, download_btn)
    
    def create_playlist(self, folder_name: str, files: List[Dict]):
        try:

            downloads_path = Path.home() / "Downloads"
            

            safe_name = re.sub(r'[^\w\s-]', '', folder_name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.m3u8"
            filepath = downloads_path / filename
            

            m3u_content = "#EXTM3U\n"
            for file_info in files:
                m3u_content += f"#EXTINF:-1,{file_info['name']}\n"
                m3u_content += f"{file_info['url']}\n"
            

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            QMessageBox.information(
                self, 
                "Playlist Created", 
                f"Playlist saved to:\n{filepath}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create playlist: {str(e)}"
            )
    
    def open_download(self, url: str):
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open browser: {str(e)}"
            )
    
    def search_finished(self):
        self.progress_bar.hide()
        self.search_button.setEnabled(True)
        
        result_count = self.results_tree.topLevelItemCount()
        if result_count == 0:
            self.status_label.setText("No results found")
        else:
            self.status_label.setText(f"Found {result_count} result(s)")
    
    def show_error(self, message: str):
        print(f"Error: {message}")



def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()