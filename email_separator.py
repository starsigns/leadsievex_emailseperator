
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, 
    QFileDialog, QMessageBox, QProgressBar, QGroupBox, QGridLayout, QFrame,
    QMenuBar, QAction, QMainWindow, QShortcut, QDialog, QTextBrowser, QTabWidget
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent, QKeySequence, QIcon
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

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📧 About LeadSieveX")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📧 LeadSieveX Email Separator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_info = QTextBrowser()
        version_info.setMaximumHeight(200)
        version_info.setHtml("""
        <div style="font-family: Arial; font-size: 12px; line-height: 1.5;">
            <p><b>Version:</b> 2.0.0</p>
            <p><b>Release Date:</b> September 2025</p>
            <p><b>Developer:</b> Star Signs</p>
            
            <h3 style="color: #4CAF50;">Features:</h3>
            <ul>
                <li>📂 Load and process large email lists (millions of emails)</li>
                <li>🗑️ Remove unwanted emails by file or manual input</li>
                <li>✂️ High-performance email separation using Python sets</li>
                <li>📊 Real-time statistics and performance monitoring</li>
                <li>🎯 Drag & drop file support</li>
                <li>💾 Export results with detailed success confirmation</li>
                <li>🎨 Modern, professional user interface</li>
            </ul>
            
            <h3 style="color: #FF5722;">Technology Stack:</h3>
            <ul>
                <li>Python 3.6+</li>
                <li>PyQt5 for GUI</li>
                <li>Multi-threading for responsive UI</li>
                <li>Git version control</li>
            </ul>
            
            <p style="margin-top: 15px; color: #666;">
                <b>GitHub:</b> 
                <a href="https://github.com/starsigns/leadsievex_emailseperator">
                    github.com/starsigns/leadsievex_emailseperator
                </a>
            </p>
        </div>
        """)
        layout.addWidget(version_info)
        
        # Close button
        close_btn = QPushButton("✅ Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class EmailSeparatorMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('📧 LeadSieveX - Email Separator')
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        self.central_widget = EmailSeparatorWidget()
        self.setCentralWidget(self.central_widget)
        
        self.setAcceptDrops(True)  # Enable drag and drop
        self.setup_menu_bar()
        self.setup_shortcuts()
        
    def setup_menu_bar(self):
        """Create the menu bar with File, Edit, View, and Help menus"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('📁 &File')
        
        # Load Main List
        load_main_action = QAction('📂 &Load Main List...', self)
        load_main_action.setShortcut(QKeySequence.Open)
        load_main_action.setStatusTip('Load main email list from file (Ctrl+O)')
        load_main_action.triggered.connect(self.central_widget.load_main_list)
        file_menu.addAction(load_main_action)
        
        # Load Unwanted List
        load_unwanted_action = QAction('🗑️ Load &Unwanted List...', self)
        load_unwanted_action.setShortcut('Ctrl+U')
        load_unwanted_action.setStatusTip('Load unwanted email list from file (Ctrl+U)')
        load_unwanted_action.triggered.connect(self.central_widget.load_unwanted_list)
        file_menu.addAction(load_unwanted_action)
        
        file_menu.addSeparator()
        
        # Export Results
        export_action = QAction('💾 &Export Results...', self)
        export_action.setShortcut(QKeySequence.Save)
        export_action.setStatusTip('Export filtered email list (Ctrl+S)')
        export_action.triggered.connect(self.central_widget.export_result)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction('🚪 E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.setStatusTip('Exit application (Ctrl+Q)')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu('✏️ &Edit')
        
        # Clear Text Area
        clear_action = QAction('🧹 &Clear Text Area', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.setStatusTip('Clear the manual input text area (Ctrl+L)')
        clear_action.triggered.connect(self.central_widget.clear_text_area)
        edit_menu.addAction(clear_action)
        
        # Process Menu
        process_menu = menubar.addMenu('⚡ &Process')
        
        # Preview Emails
        preview_action = QAction('👁️ &Preview Emails to Remove', self)
        preview_action.setShortcut('Ctrl+P')
        preview_action.setStatusTip('Preview emails that will be removed (Ctrl+P)')
        preview_action.triggered.connect(self.central_widget.preview_emails)
        process_menu.addAction(preview_action)
        
        process_menu.addSeparator()
        
        # Separate Emails
        separate_action = QAction('✂️ &Separate Emails', self)
        separate_action.setShortcut('Ctrl+R')
        separate_action.setStatusTip('Process email separation (Ctrl+R)')
        separate_action.triggered.connect(self.central_widget.separate_emails)
        process_menu.addAction(separate_action)
        
        # View Menu
        view_menu = menubar.addMenu('👁️ &View')
        
        # Refresh Statistics
        refresh_stats_action = QAction('🔄 &Refresh Statistics', self)
        refresh_stats_action.setShortcut('F5')
        refresh_stats_action.setStatusTip('Refresh statistics panel (F5)')
        refresh_stats_action.triggered.connect(self.central_widget.update_statistics)
        view_menu.addAction(refresh_stats_action)
        
        # Help Menu
        help_menu = menubar.addMenu('❓ &Help')
        
        # Keyboard Shortcuts
        shortcuts_action = QAction('⌨️ &Keyboard Shortcuts', self)
        shortcuts_action.setShortcut('F1')
        shortcuts_action.setStatusTip('Show keyboard shortcuts (F1)')
        shortcuts_action.triggered.connect(self.show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        # About
        about_action = QAction('📧 &About LeadSieveX', self)
        about_action.setStatusTip('About this application')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Status bar
        self.statusBar().showMessage('🟢 Ready - Use File menu or drag & drop to get started')
    
    def setup_shortcuts(self):
        """Setup additional keyboard shortcuts"""
        # Focus shortcuts
        focus_text_shortcut = QShortcut(QKeySequence('Ctrl+T'), self)
        focus_text_shortcut.activated.connect(lambda: self.central_widget.text_area.setFocus())
        
    def show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        msg = QMessageBox()
        msg.setWindowTitle('⌨️ Keyboard Shortcuts')
        msg.setText("""
<h3>📁 File Operations:</h3>
<b>Ctrl+O</b> - Load Main List<br>
<b>Ctrl+U</b> - Load Unwanted List<br>
<b>Ctrl+S</b> - Export Results<br>
<b>Ctrl+Q</b> - Exit Application<br>

<h3>✏️ Editing:</h3>
<b>Ctrl+L</b> - Clear Text Area<br>
<b>Ctrl+T</b> - Focus Text Area<br>

<h3>⚡ Processing:</h3>
<b>Ctrl+P</b> - Preview Emails to Remove<br>
<b>Ctrl+R</b> - Separate Emails<br>

<h3>👁️ View:</h3>
<b>F5</b> - Refresh Statistics<br>
<b>F1</b> - Show This Help<br>

<h3>🎯 Tips:</h3>
• Drag & drop .txt files onto the window<br>
• All buttons have tooltips for guidance<br>
• Statistics update in real-time<br>
        """)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    def show_about(self):
        """Show about dialog"""
        about_dialog = AboutDialog(self)
        about_dialog.exec_()
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        self.central_widget.dragEnterEvent(event)
        
    def dragLeaveEvent(self, event):
        """Handle drag leave events"""
        self.central_widget.dragLeaveEvent(event)
        
    def dropEvent(self, event: QDropEvent):
        """Handle file drop events"""
        self.central_widget.dropEvent(event)

class EmailSeparatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.main_emails = set()
        self.result_emails = set()
        self.main_file = None
        self.unwanted_emails = set()
        self.setAcceptDrops(True)  # Enable drag and drop
        self.setup_styles()
        self.init_ui()

    def clear_text_area(self):
        """Clear the text area and update statistics"""
        self.text_area.clear()
        self.update_statistics()

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
        self.load_btn.setToolTip('📂 Load your main email list from a .txt file\n• Supports files with millions of emails\n• One email per line format\n• Keyboard shortcut: Ctrl+O\n• Drag & drop supported')
        self.load_btn.clicked.connect(self.load_main_list)
        file_ops_layout.addWidget(self.load_btn)

        self.load_unwanted_btn = QPushButton('🗑️ Load Unwanted List from File')
        self.load_unwanted_btn.setToolTip('🗑️ Load emails to remove from a .txt file\n• These emails will be excluded from the main list\n• One email per line format\n• Keyboard shortcut: Ctrl+U\n• Drag & drop supported')
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
        self.text_area.setPlaceholderText("📝 Paste emails here...\n\nExample:\nemail1@example.com\nemail2@example.com\nemail3@example.com\n\n💡 Tip: Use Ctrl+L to clear this area")
        self.text_area.setMaximumHeight(150)
        self.text_area.textChanged.connect(self.update_statistics)  # Update stats when text changes
        self.text_area.setToolTip('✏️ Manual email input area\n• Paste emails to remove (one per line)\n• Combines with file-loaded emails\n• Real-time statistics update\n• Keyboard shortcut: Ctrl+T to focus\n• Ctrl+L to clear')
        text_input_layout.addWidget(self.text_area)
        
        text_input_group.setLayout(text_input_layout)
        left_panel.addWidget(text_input_group)
        
        # Action buttons
        actions_group = QGroupBox("⚡ Actions")
        actions_layout = QVBoxLayout()
        
        # Preview button
        self.preview_btn = QPushButton('👁️ Preview Emails to Remove')
        self.preview_btn.setToolTip('👁️ Preview emails that will be removed\n• Shows up to 100 sample emails\n• No changes are made to your data\n• Keyboard shortcut: Ctrl+P')
        self.preview_btn.clicked.connect(self.preview_emails)
        actions_layout.addWidget(self.preview_btn)
        
        self.separate_btn = QPushButton('✂️ Separate Emails')
        self.separate_btn.setToolTip('✂️ Remove unwanted emails from main list\n• Process and filter the email list\n• Creates a new clean list\n• Keyboard shortcut: Ctrl+R')
        self.separate_btn.clicked.connect(self.separate_emails)
        actions_layout.addWidget(self.separate_btn)

        self.export_btn = QPushButton('💾 Export Result')
        self.export_btn.setToolTip('💾 Save the filtered email list to a file\n• Predefined filename: "separated_YYYYMMDD_HHMMSS.txt"\n• Customize filename as needed\n• Export the processed results\n• Keyboard shortcut: Ctrl+S')
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
        
        # Get current timestamp for unique filename
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Set predefined filename with timestamp
        default_filename = f"separated_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            'Save Separated Email List', 
            default_filename,  # Predefined filename
            'Text Files (*.txt);;All Files (*)'
        )
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

    def preview_emails(self):
        """Preview emails that will be removed before separation"""
        # Get emails from text area
        pasted_emails = set(email.strip() for email in self.text_area.toPlainText().splitlines() if email.strip())
        
        # Combine with file-loaded unwanted emails
        total_unwanted = pasted_emails | self.unwanted_emails
        
        if not total_unwanted:
            QMessageBox.information(self, 'Preview', 
                '📭 No emails to remove found.\n\n'
                'Please either:\n'
                '• Load an unwanted list file, or\n'
                '• Paste emails in the text area')
            return
        
        # Check which emails actually exist in main list (if loaded)
        if self.main_emails:
            emails_to_remove = total_unwanted & self.main_emails
            emails_not_found = total_unwanted - self.main_emails
        else:
            emails_to_remove = total_unwanted
            emails_not_found = set()
        
        # Show preview dialog
        preview_dialog = EmailPreviewDialog(
            emails_to_remove, 
            emails_not_found, 
            len(self.main_emails) if self.main_emails else 0,
            self
        )
        preview_dialog.exec_()

class EmailPreviewDialog(QDialog):
    """Dialog to preview emails that will be removed"""
    
    def __init__(self, emails_to_remove, emails_not_found, main_list_size, parent=None):
        super().__init__(parent)
        self.emails_to_remove = emails_to_remove
        self.emails_not_found = emails_not_found
        self.main_list_size = main_list_size
        self.setWindowTitle('👁️ Email Preview')
        self.setWindowIcon(self.parent().windowIcon() if parent else None)
        self.resize(700, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preview dialog UI"""
        layout = QVBoxLayout()
        
        # Header with statistics
        header = QLabel()
        header.setWordWrap(True)
        header.setAlignment(Qt.AlignCenter)
        
        if self.main_list_size > 0:
            removal_percentage = (len(self.emails_to_remove) / self.main_list_size) * 100 if self.main_list_size > 0 else 0
            remaining_count = self.main_list_size - len(self.emails_to_remove)
            remaining_percentage = (remaining_count / self.main_list_size) * 100 if self.main_list_size > 0 else 0
            
            header.setText(f"""
            <div style="font-size: 14px; margin: 10px;">
                <h3 style="color: #4CAF50;">📊 Preview Summary</h3>
                <p><b>📧 Main List Size:</b> {self.main_list_size:,} emails</p>
                <p><b>🗑️ Emails to Remove:</b> {len(self.emails_to_remove):,} emails ({removal_percentage:.1f}%)</p>
                <p><b>✅ Emails Remaining:</b> {remaining_count:,} emails ({remaining_percentage:.1f}%)</p>
                {f'<p><b>❌ Not Found in Main List:</b> {len(self.emails_not_found):,} emails</p>' if self.emails_not_found else ''}
            </div>
            """)
        else:
            header.setText(f"""
            <div style="font-size: 14px; margin: 10px;">
                <h3 style="color: #FF9800;">⚠️ No Main List Loaded</h3>
                <p><b>🗑️ Emails to Remove:</b> {len(self.emails_to_remove):,} emails</p>
                <p><i>Load a main list to see detailed removal statistics</i></p>
            </div>
            """)
        
        layout.addWidget(header)
        
        # Tabs for different email lists
        tab_widget = QTabWidget()
        
        # Tab 1: Emails to remove (found in main list)
        if self.emails_to_remove:
            remove_tab = QWidget()
            remove_layout = QVBoxLayout()
            
            remove_info = QLabel(f'📧 These {len(self.emails_to_remove):,} emails will be removed from your main list:')
            remove_info.setStyleSheet("font-weight: bold; color: #d32f2f; margin: 5px;")
            remove_layout.addWidget(remove_info)
            
            remove_text = QTextEdit()
            remove_text.setReadOnly(True)
            remove_text.setFont(QFont("Consolas", 10))
            
            # Show sample of emails (limit to 100 for performance)
            sample_emails = list(self.emails_to_remove)[:100]
            email_text = '\n'.join(sample_emails)
            
            if len(self.emails_to_remove) > 100:
                email_text += f'\n\n... and {len(self.emails_to_remove) - 100:,} more emails'
            
            remove_text.setText(email_text)
            remove_layout.addWidget(remove_text)
            
            remove_tab.setLayout(remove_layout)
            tab_widget.addTab(remove_tab, f'🗑️ To Remove ({len(self.emails_to_remove):,})')
        
        # Tab 2: Emails not found in main list
        if self.emails_not_found:
            not_found_tab = QWidget()
            not_found_layout = QVBoxLayout()
            
            not_found_info = QLabel(f'⚠️ These {len(self.emails_not_found):,} emails are not in your main list:')
            not_found_info.setStyleSheet("font-weight: bold; color: #ff9800; margin: 5px;")
            not_found_layout.addWidget(not_found_info)
            
            not_found_text = QTextEdit()
            not_found_text.setReadOnly(True)
            not_found_text.setFont(QFont("Consolas", 10))
            
            # Show sample of emails (limit to 100 for performance)
            sample_not_found = list(self.emails_not_found)[:100]
            not_found_email_text = '\n'.join(sample_not_found)
            
            if len(self.emails_not_found) > 100:
                not_found_email_text += f'\n\n... and {len(self.emails_not_found) - 100:,} more emails'
            
            not_found_text.setText(not_found_email_text)
            not_found_layout.addWidget(not_found_text)
            
            not_found_tab.setLayout(not_found_layout)
            tab_widget.addTab(not_found_tab, f'❌ Not Found ({len(self.emails_not_found):,})')
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton('📋 Close Preview')
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        if self.emails_to_remove and self.main_list_size > 0:
            proceed_btn = QPushButton('✂️ Proceed with Separation')
            proceed_btn.clicked.connect(self.proceed_separation)
            proceed_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    font-size: 12px;
                    font-weight: bold;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            button_layout.addWidget(proceed_btn)
        
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def proceed_separation(self):
        """Close preview and trigger separation"""
        self.accept()
        if self.parent():
            self.parent().separate_emails()

def main():
    app = QApplication(sys.argv)
    window = EmailSeparatorMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
