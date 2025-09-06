
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import QThread, pyqtSignal
import os

class FileProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object, str)
    
    def __init__(self, file_path, operation_type):
        super().__init__()
        self.file_path = file_path
        self.operation_type = operation_type
        
    def run(self):
        start_time = time.time()
        emails = set()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                total_lines = len(lines)
                
                for i, line in enumerate(lines):
                    email = line.strip()
                    if email:
                        emails.add(email)
                    
                    # Update progress every 1000 lines or at the end
                    if i % 1000 == 0 or i == total_lines - 1:
                        progress_percent = int((i + 1) / total_lines * 100)
                        self.progress.emit(progress_percent)
                        
            elapsed_time = time.time() - start_time
            result_msg = f"Loaded {len(emails)} emails in {elapsed_time:.2f} seconds"
            self.finished.emit(emails, result_msg)
            
        except Exception as e:
            self.finished.emit(None, f"Error: {str(e)}")

class SeparatorProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object, str)
    
    def __init__(self, main_emails, unwanted_emails):
        super().__init__()
        self.main_emails = main_emails
        self.unwanted_emails = unwanted_emails
        
    def run(self):
        start_time = time.time()
        
        try:
            # Set difference operation is very fast
            self.progress.emit(50)
            remaining = self.main_emails - self.unwanted_emails
            self.progress.emit(100)
            
            elapsed_time = time.time() - start_time
            result_msg = f"Separated {len(self.unwanted_emails)} emails. {len(remaining)} remain. Completed in {elapsed_time:.2f} seconds"
            self.finished.emit(remaining, result_msg)
            
        except Exception as e:
            self.finished.emit(None, f"Error: {str(e)}")

class ExportProcessor(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    
    def __init__(self, emails, file_path):
        super().__init__()
        self.emails = emails
        self.file_path = file_path
        
    def run(self):
        start_time = time.time()
        
        try:
            sorted_emails = sorted(self.emails)
            total_emails = len(sorted_emails)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                for i, email in enumerate(sorted_emails):
                    f.write(email + '\n')
                    
                    # Update progress every 1000 emails or at the end
                    if i % 1000 == 0 or i == total_emails - 1:
                        progress_percent = int((i + 1) / total_emails * 100)
                        self.progress.emit(progress_percent)
                        
            elapsed_time = time.time() - start_time
            file_size = os.path.getsize(self.file_path) / (1024 * 1024)  # Size in MB
            result_msg = f"✅ Export Successful!\n\nSaved {total_emails} emails to:\n{os.path.basename(self.file_path)}\n\nFile size: {file_size:.2f} MB\nTime taken: {elapsed_time:.2f} seconds"
            self.finished.emit(result_msg)
            
        except Exception as e:
            self.finished.emit(f"❌ Export Failed: {str(e)}")

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

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

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
            self.load_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText('Loading main email list...')
            
            self.file_processor = FileProcessor(file_path, 'main')
            self.file_processor.progress.connect(self.progress_bar.setValue)
            self.file_processor.finished.connect(self.on_main_list_loaded)
            self.file_processor.start()
        else:
            self.status_label.setText('No file selected.')
            
    def on_main_list_loaded(self, emails, message):
        if emails is not None:
            self.main_emails = emails
            self.main_file = self.file_processor.file_path
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)

    def load_unwanted_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Unwanted Email List', '', 'Text Files (*.txt)')
        if file_path:
            self.load_unwanted_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText('Loading unwanted email list...')
            
            self.file_processor = FileProcessor(file_path, 'unwanted')
            self.file_processor.progress.connect(self.progress_bar.setValue)
            self.file_processor.finished.connect(self.on_unwanted_list_loaded)
            self.file_processor.start()
        else:
            self.status_label.setText('No unwanted file selected.')
            
    def on_unwanted_list_loaded(self, emails, message):
        if emails is not None:
            self.unwanted_emails = emails
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.load_unwanted_btn.setEnabled(True)

    def separate_emails(self):
        if not self.main_emails:
            QMessageBox.critical(self, 'Error', 'Please load the main email list first.')
            return
        pasted_emails = set(email.strip() for email in self.text_area.toPlainText().splitlines() if email.strip())
        total_unwanted = pasted_emails | self.unwanted_emails
        if not total_unwanted:
            QMessageBox.critical(self, 'Error', 'Please provide emails to remove (paste or load a file).')
            return
            
        self.separate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText('Processing separation...')
        
        self.separator_processor = SeparatorProcessor(self.main_emails, total_unwanted)
        self.separator_processor.progress.connect(self.progress_bar.setValue)
        self.separator_processor.finished.connect(self.on_separation_finished)
        self.separator_processor.start()
        
    def on_separation_finished(self, remaining, message):
        if remaining is not None:
            self.result_emails = remaining
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.separate_btn.setEnabled(True)

    def export_result(self):
        if not self.result_emails:
            QMessageBox.critical(self, 'Error', 'No result to export. Run separation first.')
            return
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Result', '', 'Text Files (*.txt)')
        if file_path:
            self.export_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText('Exporting results...')
            
            self.export_processor = ExportProcessor(self.result_emails, file_path)
            self.export_processor.progress.connect(self.progress_bar.setValue)
            self.export_processor.finished.connect(self.on_export_finished)
            self.export_processor.start()
        else:
            self.status_label.setText('Export cancelled.')
            
    def on_export_finished(self, message):
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        
        # Show success/failure message in a popup
        if "✅" in message:
            QMessageBox.information(self, 'Export Complete', message)
            self.status_label.setText('Export completed successfully.')
        else:
            QMessageBox.critical(self, 'Export Failed', message)
            self.status_label.setText('Export failed.')

def main():
    app = QApplication(sys.argv)
    window = EmailSeparatorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
