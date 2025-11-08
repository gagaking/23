import sys
import os
import json
import requests
from PyQt5 import QtWidgets, QtCore

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ai_app_config.json")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def load_api_key():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            cfg = json.load(f)
        return cfg.get("api_key", "")
    return ""

def save_api_key(api_key):
    with open(CONFIG_PATH, "w") as f:
        json.dump({"api_key": api_key}, f)

class ApiKeyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("首次启动请输入Gemini API Key")
        self.setModal(True)
        self.resize(400, 150)
        layout = QtWidgets.QVBoxLayout(self)
        self.input = QtWidgets.QLineEdit(self)
        self.input.setPlaceholderText("请输入Gemini API Key")
        layout.addWidget(QtWidgets.QLabel("请输入你的 Gemini API Key"))
        layout.addWidget(self.input)
        btn = QtWidgets.QPushButton("保存并进入")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
    def get_api_key(self):
        return self.input.text().strip()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, api_key):
        super().__init__()
        self.setWindowTitle("Gemini AI 客户端 (全屏)")
        self.showFullScreen()
        central = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(central)
        self.api_key = api_key
        self.input = QtWidgets.QLineEdit(central)
        self.input.setPlaceholderText("输入你的问题 ...")
        self.btn = QtWidgets.QPushButton("发送", central)
        self.resp = QtWidgets.QTextEdit(central)
        self.resp.setReadOnly(True)
        self.info = QtWidgets.QLabel("API Key已加载 | 网络调用有异常会提示")
        self.info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.info)
        layout.addWidget(self.input)
        layout.addWidget(self.btn)
        layout.addWidget(self.resp)
        self.btn.clicked.connect(self.ask_gemini)
        self.setCentralWidget(central)

    def ask_gemini(self):
        query = self.input.text().strip()
        if not query:
            self.info.setText("请输入问题后再发送")
            return
        self.info.setText("正在调用Gemini API，请稍候...")
        payload = {
            "contents": [{"parts": [{"text": query}]}]
        }
        params = {"key": self.api_key}
        try:
            resp = requests.post(
                GEMINI_API_URL,
                params=params,
                json=payload,
                timeout=15 # 超时处理
            )
            resp.raise_for_status()
            data = resp.json()
            # Gemini响应内容解析
            result = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "没有返回内容")
            self.resp.setText(result)
            self.info.setText("API调用成功")
        except requests.exceptions.Timeout:
            self.info.setText("网络请求超时，请检查网络后重试")
        except requests.exceptions.ConnectionError:
            self.info.setText("无法连接到Gemini服务，请检查网络")
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 401:
                self.info.setText("API Key无效，请重新输入")
            else:
                self.info.setText(f"HTTP错误: {resp.status_code}")
        except Exception as e:
            self.info.setText(f"其他错误: {str(e)}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    api_key = load_api_key()
    if not api_key:
        dlg = ApiKeyDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            api_key = dlg.get_api_key()
            if api_key:
                save_api_key(api_key)
            else:
                QtWidgets.QMessageBox.warning(None, "提示", "API Key不能为空！")
                sys.exit(1)
        else:
            sys.exit(0)
    window = MainWindow(api_key)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()