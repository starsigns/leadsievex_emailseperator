
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox
)
import os

class EmailSeparatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Email Separator App')
        self.setGeometry(100, 100, 800, 600)
        self.main_emails = set()
        self.result_emails = set()
        self.main_file = None
        self.unwanted_emails = set()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.status_label = QLabel('Ready.')
        layout.addWidget(self.status_label)

        self.load_btn = QPushButton('Load Main Email List')
        self.load_btn.clicked.connect(self.load_main_list)
        layout.addWidget(self.load_btn)

        self.load_unwanted_btn = QPushButton('Load Unwanted List from File')
        self.load_unwanted_btn.clicked.connect(self.load_unwanted_list)
        layout.addWidget(self.load_unwanted_btn)

        self.text_label = QLabel('Paste emails to remove (one per line, each email must be on a new line):')
        layout.addWidget(self.text_label)

        self.text_area = QTextEdit()
        layout.addWidget(self.text_area)

        self.separate_btn = QPushButton('Separate')
        self.separate_btn.clicked.connect(self.separate_emails)
        layout.addWidget(self.separate_btn)

        self.export_btn = QPushButton('Export Result')
        self.export_btn.clicked.connect(self.export_result)
        layout.addWidget(self.export_btn)

        self.setLayout(layout)

    def load_main_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Main Email List', '', 'Text Files (*.txt)')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                emails = set(line.strip() for line in f if line.strip())
            self.main_emails = emails
            self.main_file = file_path
            self.status_label.setText(f"Loaded {len(emails)} emails from {os.path.basename(file_path)}")
        else:
            self.status_label.setText('No file selected.')

    def load_unwanted_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Unwanted Email List', '', 'Text Files (*.txt)')
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                emails = set(line.strip() for line in f if line.strip())
            self.unwanted_emails = emails
            self.status_label.setText(f"Loaded {len(emails)} unwanted emails from {os.path.basename(file_path)}")
        else:
            self.status_label.setText('No unwanted file selected.')

    def separate_emails(self):
        if not self.main_emails:
            QMessageBox.critical(self, 'Error', 'Please load the main email list first.')
            return
        pasted_emails = set(email.strip() for email in self.text_area.toPlainText().splitlines() if email.strip())
        to_remove = pasted_emails | self.unwanted_emails
        if not to_remove:
            QMessageBox.critical(self, 'Error', 'Please provide emails to remove (paste or load a file).')
            return
        remaining = self.main_emails - to_remove
        self.result_emails = remaining
        self.status_label.setText(f"Separated {len(to_remove)} emails. {len(remaining)} remain.")

    def export_result(self):
        if not self.result_emails:
            QMessageBox.critical(self, 'Error', 'No result to export. Run separation first.')
            return
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Result', '', 'Text Files (*.txt)')
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                for email in sorted(self.result_emails):
                    f.write(email + '\n')
            self.status_label.setText(f"Exported {len(self.result_emails)} emails to {os.path.basename(file_path)}")
        else:
            self.status_label.setText('Export cancelled.')

def main():
    app = QApplication(sys.argv)
    window = EmailSeparatorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
