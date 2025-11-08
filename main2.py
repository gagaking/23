# PyQt5 Desktop Client

## Features
- Fullscreen support
- First-time entry of Gemini API Key and memory
- Local configuration auto-save
- API exception handling

## Code Example

```python
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gemini API Client')
        self.showFullScreen()  # Sets the window to fullscreen

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
```