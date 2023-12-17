import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import urllib.request
import urllib.parse
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineSettings,
)
from PyQt5.QtCore import QUrl
import sys

# Define browser_window as a global variable
browser_window = None
app = None  # Declare app as a global variable


class BrowserWindow(QMainWindow):
    def __init__(self, url):
        global browser_window  # Declare as global
        super().__init__()

        self.setWindowTitle("YouTube Browser")
        self.setGeometry(100, 100, 800, 600)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(url))

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Connect the close event to a custom function
        self.browser.page().windowCloseRequested.connect(self.close_requested)

    def close_requested(self):
        # This function is called when the YouTube window is closed
        global browser_window  # Declare as global
        browser_window.hide()


class EmbeddedBrowser(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.page = QWebEnginePage()
        self.setPage(self.page)
        settings = self.page.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.loadFinished.connect(self.on_load_finished)

    def on_load_finished(self, success):
        if not success:
            print("Page failed to load. Check for errors.")
        else:
            self.page().runJavaScript(
                """
                window.onerror = function(message, source, lineno, colno, error) {
                    console.error('Error:', message, 'at', source, 'Line:', lineno, 'Column:', colno);
                };
                """,
                print,
            )


def hide_browser_window(event=None):
    # This function is called when the BrowserWindow is closed
    global browser_window  # Declare as global
    browser_window.hide()


def quit_app():
    global app, root
    app.quit()
    root.destroy()


def perform_search():
    x = entry.get().capitalize()

    # Properly encode the URL
    query_params = urllib.parse.urlencode({"term": x, "entity": "album"})
    url = f"https://itunes.apple.com/search?{query_params}"

    # Use urllib to make the request
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))

    search_results = data.get("results", [])
    if not search_results:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"No albums found for {x}")
        result_text.config(state=tk.DISABLED)
    else:
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Here are the albums for {x}:\n")
        albums = [
            result.get("collectionName", "Unknown Album") for result in search_results
        ]
        for album in albums:
            result_text.insert(tk.END, f"{album}\n")
        result_text.config(state=tk.DISABLED)

        # Enable the Combobox and "Play Album" button
        album_combobox.config(state=tk.NORMAL)
        album_combobox["values"] = albums
        album_combobox.current(0)  # Select the first album by default
        play_button.config(state=tk.NORMAL)


def play_album():
    global browser_window, app  # Declare as global

    if not app:
        # Create an instance of QApplication only if it doesn't exist
        app = QApplication(sys.argv)

    selected_album = album_combobox.get()
    album_name = selected_album.capitalize()
    youtube_url = (
        f"https://www.youtube.com/results?search_query={album_name}+full+album"
    )

    # Create an instance of EmbeddedBrowser
    embedded_browser = EmbeddedBrowser()

    # Set browser_window as a global variable
    browser_window = BrowserWindow(youtube_url)
    browser_window.show()

    # Connect the hide_browser_window function to the close event of the BrowserWindow
    browser_window.closeEvent = hide_browser_window

    # Start the PyQt5 event loop
    app.aboutToQuit.connect(app.quit)
    app.exec_()


root = tk.Tk()
root.title("YouTube Album Player")

label = tk.Label(root, text="Enter the singer's name:")
label.pack()

entry = tk.Entry(root)
entry.pack()

search_button = tk.Button(root, text="Search Albums", command=perform_search)
search_button.pack()

result_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, width=50)
result_text.pack()

# Use ttk.Combobox for better compatibility with the Tkinter theme
album_combobox = ttk.Combobox(root, state=tk.DISABLED)
album_combobox.pack()

play_button = tk.Button(root, text="Play Album", command=play_album, state=tk.DISABLED)
play_button.pack()

quit_button = tk.Button(root, text="Quit", command=quit_app)
quit_button.pack()

# Start the Tkinter event loop
root.mainloop()
