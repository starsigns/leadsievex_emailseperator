
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, 
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QGridLayout, QFrame
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent
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
        self.setWindowTitle('📧 LeadSieveX - Email Separator')
        self.setGeometry(100, 100, 1000, 700)
        self.main_emails = set()
        self.result_emails = set()
        self.main_file = None
        self.unwanted_emails = set()
        self.setAcceptDrops(True)  # Enable drag and drop
        self.setup_styles()
        self.init_ui()

    def setup_styles(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLabel {
                color: #333333;
                font-size: 13px;
                margin: 4px;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 6px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin: 8px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #333333;
            }
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin: 4px;
                padding: 8px;
            }
        """)

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Left panel - Main controls
        left_panel = QVBoxLayout()
        
        # Status and progress section
        status_group = QGroupBox("📊 Status & Progress")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel('🟢 Ready - Drag & drop files or use buttons below')
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        status_group.setLayout(status_layout)
        left_panel.addWidget(status_group)
        
        # File operations section
        file_ops_group = QGroupBox("📁 File Operations")
        file_ops_layout = QVBoxLayout()
        
        self.load_btn = QPushButton('📂 Load Main Email List')
        self.load_btn.setToolTip('Load your main email list (supports drag & drop)')
        self.load_btn.clicked.connect(self.load_main_list)
        file_ops_layout.addWidget(self.load_btn)

        self.load_unwanted_btn = QPushButton('🗑️ Load Unwanted List from File')
        self.load_unwanted_btn.setToolTip('Load emails to remove from file (supports drag & drop)')
        self.load_unwanted_btn.clicked.connect(self.load_unwanted_list)
        file_ops_layout.addWidget(self.load_unwanted_btn)
        
        file_ops_group.setLayout(file_ops_layout)
        left_panel.addWidget(file_ops_group)
        
        # Text input section
        text_input_group = QGroupBox("✏️ Manual Input")
        text_input_layout = QVBoxLayout()
        
        self.text_label = QLabel('Paste emails to remove (one per line):')
        text_input_layout.addWidget(self.text_label)

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("email1@example.com\nemail2@example.com\n...")
        self.text_area.setMaximumHeight(150)
        self.text_area.textChanged.connect(self.update_statistics)  # Update stats when text changes
        text_input_layout.addWidget(self.text_area)
        
        text_input_group.setLayout(text_input_layout)
        left_panel.addWidget(text_input_group)
        
        # Action buttons
        actions_group = QGroupBox("⚡ Actions")
        actions_layout = QVBoxLayout()
        
        self.separate_btn = QPushButton('✂️ Separate Emails')
        self.separate_btn.setToolTip('Remove unwanted emails from main list')
        self.separate_btn.clicked.connect(self.separate_emails)
        actions_layout.addWidget(self.separate_btn)

        self.export_btn = QPushButton('💾 Export Result')
        self.export_btn.setToolTip('Save the filtered email list')
        self.export_btn.clicked.connect(self.export_result)
        actions_layout.addWidget(self.export_btn)
        
        actions_group.setLayout(actions_layout)
        left_panel.addWidget(actions_group)
        
        left_panel.addStretch()
        
        # Right panel - Statistics
        right_panel = QVBoxLayout()
        self.stats_group = QGroupBox("📈 Statistics")
        self.setup_statistics_panel()
        right_panel.addWidget(self.stats_group)
        right_panel.addStretch()
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)  # Left panel takes 2/3 of space
        main_layout.addLayout(right_panel, 1)  # Right panel takes 1/3 of space
        
        self.setLayout(main_layout)
        
    def setup_statistics_panel(self):
        """Create the statistics panel with data visualization"""
        stats_layout = QGridLayout()
        
        # Main list stats
        self.main_count_label = QLabel("📧 Main List: 0 emails")
        self.main_count_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        stats_layout.addWidget(self.main_count_label, 0, 0, 1, 2)
        
        # Unwanted stats
        self.unwanted_count_label = QLabel("🗑️ To Remove: 0 emails")
        self.unwanted_count_label.setStyleSheet("font-weight: bold; color: #FF5722;")
        stats_layout.addWidget(self.unwanted_count_label, 1, 0, 1, 2)
        
        # Result stats
        self.result_count_label = QLabel("✅ Remaining: 0 emails")
        self.result_count_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        stats_layout.addWidget(self.result_count_label, 2, 0, 1, 2)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        stats_layout.addWidget(line, 3, 0, 1, 2)
        
        # Performance stats
        self.perf_label = QLabel("⏱️ Performance")
        self.perf_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        stats_layout.addWidget(self.perf_label, 4, 0, 1, 2)
        
        self.load_time_label = QLabel("Load Time: --")
        stats_layout.addWidget(self.load_time_label, 5, 0, 1, 2)
        
        self.process_time_label = QLabel("Process Time: --")
        stats_layout.addWidget(self.process_time_label, 6, 0, 1, 2)
        
        self.export_time_label = QLabel("Export Time: --")
        stats_layout.addWidget(self.export_time_label, 7, 0, 1, 2)
        
        # File info
        self.file_info_label = QLabel("📁 File Info")
        self.file_info_label.setStyleSheet("font-weight: bold; margin-top: 8px;")
        stats_layout.addWidget(self.file_info_label, 8, 0, 1, 2)
        
        self.main_file_label = QLabel("Main: No file loaded")
        self.main_file_label.setWordWrap(True)
        stats_layout.addWidget(self.main_file_label, 9, 0, 1, 2)
        
        self.stats_group.setLayout(stats_layout)
        
    def update_statistics(self):
        """Update the statistics panel with current data"""
        main_count = len(self.main_emails)
        unwanted_count = len(self.unwanted_emails)
        
        # Count pasted emails
        pasted_emails = set(email.strip() for email in self.text_area.toPlainText().splitlines() if email.strip())
        total_unwanted = len(pasted_emails | self.unwanted_emails)
        
        result_count = len(self.result_emails) if self.result_emails else max(0, main_count - total_unwanted)
        
        # Update labels
        self.main_count_label.setText(f"📧 Main List: {main_count:,} emails")
        self.unwanted_count_label.setText(f"🗑️ To Remove: {total_unwanted:,} emails")
        self.result_count_label.setText(f"✅ Remaining: {result_count:,} emails")
        
        # Update file info
        if self.main_file:
            filename = os.path.basename(self.main_file)
            self.main_file_label.setText(f"Main: {filename}")
        else:
            self.main_file_label.setText("Main: No file loaded")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.txt'):
                event.acceptProposedAction()
                self.status_label.setText("🎯 Drop the file to load it")
            else:
                self.status_label.setText("❌ Please drop a single .txt file")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self.status_label.setText("🟢 Ready - Drag & drop files or use buttons below")

    def dropEvent(self, event: QDropEvent):
        """Handle file drop events"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if len(files) == 1 and files[0].endswith('.txt'):
            file_path = files[0]
            
            # Show dialog to ask which type of file this is
            msg = QMessageBox()
            msg.setWindowTitle('📁 File Type Selection')
            msg.setText(f'What type of email list is this?\n\n📄 {os.path.basename(file_path)}')
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            # Customize button text
            yes_button = msg.button(QMessageBox.Yes)
            yes_button.setText('📧 Main List')
            no_button = msg.button(QMessageBox.No)
            no_button.setText('🗑️ Unwanted List')
            cancel_button = msg.button(QMessageBox.Cancel)
            cancel_button.setText('❌ Cancel')
            
            reply = msg.exec_()
            
            if reply == QMessageBox.Yes:
                # Main list
                self.load_file_as_main(file_path)
            elif reply == QMessageBox.No:
                # Unwanted list
                self.load_file_as_unwanted(file_path)
            # Cancel does nothing
                
        self.status_label.setText("🟢 Ready - Drag & drop files or use buttons below")

    def load_file_as_main(self, file_path):
        """Load a file as the main email list"""
        self.load_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText('Loading main email list...')
        
        self.file_processor = FileProcessor(file_path, 'main')
        self.file_processor.progress.connect(self.progress_bar.setValue)
        self.file_processor.finished.connect(self.on_main_list_loaded)
        self.file_processor.start()

    def load_file_as_unwanted(self, file_path):
        """Load a file as the unwanted email list"""
        self.load_unwanted_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText('Loading unwanted email list...')
        
        self.file_processor = FileProcessor(file_path, 'unwanted')
        self.file_processor.progress.connect(self.progress_bar.setValue)
        self.file_processor.finished.connect(self.on_unwanted_list_loaded)
        self.file_processor.start()

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
            # Extract timing info from message
            if "in " in message:
                time_part = message.split("in ")[1]
                self.load_time_label.setText(f"Load Time: {time_part}")
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.update_statistics()

    def load_unwanted_list(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Unwanted Email List', '', 'Text Files (*.txt)')
        if file_path:
            self.load_file_as_unwanted(file_path)
        else:
            self.status_label.setText('No unwanted file selected.')
            
    def on_unwanted_list_loaded(self, emails, message):
        if emails is not None:
            self.unwanted_emails = emails
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.load_unwanted_btn.setEnabled(True)
        self.update_statistics()

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
            # Extract timing info from message
            if "Completed in " in message:
                time_part = message.split("Completed in ")[1]
                self.process_time_label.setText(f"Process Time: {time_part}")
        self.status_label.setText(message)
        self.progress_bar.setVisible(False)
        self.separate_btn.setEnabled(True)
        self.update_statistics()

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
        
        # Extract timing info from message
        if "Time taken: " in message:
            time_part = message.split("Time taken: ")[1].split("\n")[0]
            self.export_time_label.setText(f"Export Time: {time_part}")
        
        # Show success/failure message in a popup
        if "✅" in message:
            QMessageBox.information(self, 'Export Complete', message)
            self.status_label.setText('Export completed successfully.')
        else:
            QMessageBox.critical(self, 'Export Failed', message)
            self.status_label.setText('Export failed.')
        
        self.update_statistics()

def main():
    app = QApplication(sys.argv)
    window = EmailSeparatorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
