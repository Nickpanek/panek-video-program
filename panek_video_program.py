#!/usr/bin/env python3
"""
Panek Video Program - Enhanced Edition (v3.0)

This application is a video creation and editing tool built with PySide6.

Version 3.0 New Features:
- Text Overlays: Add custom text to your videos with position and style controls
- Video File Input: Use video files as input, not just images
- Fade Transitions: Add professional fade in/out effects to video and audio

Previous features:
- Modern PySide6 Framework
- Minimalist UI with a Global Dark Theme (pyqtdarktheme)
- Asynchronous Backend (FFmpegRunner with QProcess)
- Decoupled UI and Logic (Signals and Slots)
- Simplified Native Dialogs (QFileDialog)
- Overwrite protection and pre-flight validation

This software uses FFmpeg (https://ffmpeg.org) licensed under the LGPL/GPL.
"""

import sys
import os
import re
import shutil
import datetime
import subprocess
from pathlib import Path

# Import all necessary PySide6 components
from PySide6.QtCore import QObject, QProcess, Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QProgressBar, QTextEdit,
    QDialog, QDialogButtonBox, QMainWindow, QFormLayout, QMessageBox,
    QComboBox, QSpinBox, QCheckBox, QDoubleSpinBox, QGroupBox, QColorDialog
)
from PySide6.QtGui import QColor

# Import the dark theme library
# Requires: pip install pyqtdarktheme
import qdarktheme

# ---------- Constants ----------
WIDTH, HEIGHT, FPS, CRF = 1920, 1080, 30, 20
AUDIO_BITRATE = "192k"

# ---------- Core Utilities ----------

def have(cmd: str) -> bool:
    """Check if a command-line utility is available in the system's PATH."""
    return shutil.which(cmd) is not None

def ensure_ffmpeg():
    """Raise a RuntimeError if ffmpeg or ffprobe are not found."""
    if not have("ffmpeg") or not have("ffprobe"):
        raise RuntimeError("ffmpeg and/or ffprobe not found in your system's PATH.")

def sanitize_filename(name: str) -> str:
    """Clean a string to be a valid, safe filename."""
    name = name.strip()
    name = re.sub(r"[^\w\-. ]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "output"

def ffprobe_duration_seconds(path: str) -> float:
    """
    Get the duration of a media file in seconds using ffprobe.
    This is a synchronous (blocking) call, but ffprobe is fast.
    """
    # Add CREATE_NO_WINDOW flag for Windows to suppress console popup
    creation_flags = 0
    if sys.platform == 'win32':
        creation_flags = subprocess.CREATE_NO_WINDOW

    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        creationflags=creation_flags
    )
    try:
        return float(proc.stdout.strip())
    except Exception:
        return 0.0

def is_video_file(path: str) -> bool:
    """Check if a file is a video file based on extension."""
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'}
    return Path(path).suffix.lower() in video_extensions

# ---------- UI: Complete Dialog ----------

class CompleteDialog(QDialog):
    """
    A dialog shown on successful render.
    """
    def __init__(self, out_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Render Complete")
        self.setModal(True)
        self.resize(520, 250)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.seconds = 30

        lay = QVBoxLayout(self)
        self.msg = QLabel(self)
        self.msg.setTextFormat(Qt.TextFormat.RichText)
        self.msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.msg.setOpenExternalLinks(True)
        self.out_path = out_path
        lay.addWidget(self.msg)

        btns = QDialogButtonBox(self)
        self.again_btn = btns.addButton("Render Another", QDialogButtonBox.ButtonRole.AcceptRole)
        self.close_btn = btns.addButton(f"Close (in {self.seconds})", QDialogButtonBox.ButtonRole.RejectRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        self._refresh_text()
        self.timer.start(1000)

    def _refresh_text(self):
        """Update the label text."""
        self.msg.setText(
            f"Video created successfully:<br><code>{self.out_path}</code><br><br>"
            f"<small>Powered by <a href='https://ffmpeg.org'>FFmpeg</a> (LGPL/GPL)</small>"
        )
        self.close_btn.setText(f"Close (in {self.seconds})")

    def _tick(self):
        """Handle the 1-second timer tick."""
        self.seconds -= 1
        self._refresh_text()
        if self.seconds <= 0:
            self.timer.stop()
            self.reject() # Auto-reject (close) when timer hits zero

# ---------- Core: FFmpeg Runner ----------

class FFmpegRunner(QObject):
    """
    Runs ffmpeg in a non-blocking QProcess, decoupling it from the UI.
    This class is based on the architecture from the guide.
    """
    # Signals to communicate with the main UI thread
    process_started = Signal()
    process_finished = Signal(int, str)  # Emits exit_code, output_path
    log_message = Signal(str)            # Emits log lines
    progress_updated = Signal(int)       # Emits progress percentage (0-100)

    def __init__(self):
        super().__init__()
        self.process = QProcess()
        
        # We will read progress from stdout and logs from stderr
        self.process.readyReadStandardOutput.connect(self._read_progress)
        self.process.readyReadStandardError.connect(self._read_logs)
        self.process.finished.connect(self._on_finished)
        self.process.started.connect(self.process_started.emit)

        self.audio_duration = 0.0
        self.output_path = ""

    def _read_progress(self):
        """Read and parse progress data from ffmpeg's stdout."""
        if not self.process:
            return
        output = self.process.readAllStandardOutput().data().decode(errors='ignore').strip()
        
        for line in output.splitlines():
            # Parse progress lines like 'out_time_ms=12345000'
            m = re.search(r"out_time_ms=(\d+)", line)
            if m and self.audio_duration > 0:
                current_ms = int(m.group(1)) / 1_000_000.0
                pct = int(min(100, (current_ms / self.audio_duration) * 100))
                self.progress_updated.emit(pct)

    def _read_logs(self):
        """Read log data from ffmpeg's stderr."""
        if not self.process:
            return
        output = self.process.readAllStandardError().data().decode(errors='ignore').strip()
        if output:
            self.log_message.emit(output)

    def _on_finished(self, exit_code, exit_status):
        """
        Handle the QProcess.finished signal.
        Emits the custom process_finished signal for the UI.
        """
        if exit_code == 0:
            self.log_message.emit(f"--- PROCESS COMPLETE ---")
            self.log_message.emit(f"Output file: {self.output_path}")
            self.progress_updated.emit(100)
        else:
            self.log_message.emit(f"--- PROCESS FAILED (Code: {exit_code}) ---")
        
        self.process_finished.emit(exit_code, self.output_path)

    def _build_ffmpeg_cmd(self, media_path: str, audio_path: str, out_path: str, title: str,
                          text_overlay: str = "", text_position: str = "center", text_size: int = 48,
                          text_color: str = "white", fade_in: float = 0.0, fade_out: float = 0.0,
                          media_duration: float = 0.0) -> list:
        """Build the ffmpeg command list with support for video input, text overlays, and fades."""

        # Build video filter chain
        vf_filters = []

        # Scaling and padding filter (works for both image and video)
        vf_filters.append(f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2")

        # Add fade filters if requested
        if fade_in > 0:
            vf_filters.append(f"fade=t=in:st=0:d={fade_in}")
        if fade_out > 0:
            fade_start = max(0, media_duration - fade_out)
            vf_filters.append(f"fade=t=out:st={fade_start}:d={fade_out}")

        # Add text overlay if provided
        if text_overlay:
            # Escape text for FFmpeg
            safe_text = text_overlay.replace(":", "\\:").replace("'", "\\'")

            # Calculate position
            if text_position == "top":
                x_pos, y_pos = "(w-text_w)/2", "50"
            elif text_position == "bottom":
                x_pos, y_pos = "(w-text_w)/2", "h-th-50"
            else:  # center
                x_pos, y_pos = "(w-text_w)/2", "(h-text_h)/2"

            vf_filters.append(f"drawtext=text='{safe_text}':fontsize={text_size}:fontcolor={text_color}:x={x_pos}:y={y_pos}")

        # Combine all video filters
        vf = ",".join(vf_filters)

        # Build audio filter chain
        af_filters = []
        if fade_in > 0:
            af_filters.append(f"afade=t=in:st=0:d={fade_in}")
        if fade_out > 0:
            fade_start = max(0, media_duration - fade_out)
            af_filters.append(f"afade=t=out:st={fade_start}:d={fade_out}")

        # Check if input is video or image
        is_video = is_video_file(media_path)

        # Build command
        cmd = ["ffmpeg", "-y"]

        # Input handling: video vs image
        if is_video:
            cmd.extend(["-i", media_path])
        else:
            cmd.extend(["-loop", "1", "-i", media_path])

        # Audio input
        cmd.extend(["-i", audio_path])

        # Video encoding settings
        if is_video:
            cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", str(CRF)])
        else:
            cmd.extend(["-c:v", "libx264", "-preset", "medium", "-crf", str(CRF), "-tune", "stillimage"])

        # Video filters
        cmd.extend(["-vf", vf, "-r", str(FPS), "-pix_fmt", "yuv420p"])

        # Audio encoding and filters
        cmd.extend(["-c:a", "aac", "-b:a", AUDIO_BITRATE])
        if af_filters:
            cmd.extend(["-af", ",".join(af_filters)])

        cmd.extend(["-shortest"])

        # Optimization and metadata
        cmd.extend([
            "-movflags", "+faststart",
            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
            "-metadata", f"title={title}",
            "-progress", "pipe:1",
            out_path
        ])

        return cmd

    def start_processing(self, media_path: str, audio_path: str, output_path: str, title: str,
                        text_overlay: str = "", text_position: str = "center", text_size: int = 48,
                        text_color: str = "white", fade_in: float = 0.0, fade_out: float = 0.0):
        """
        Start the ffmpeg process. This is the main entry point.
        Path and title are now calculated and validated by the UI.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            self.log_message.emit("Error: A process is already running.")
            return

        # 1. Get audio duration (blocking, but fast)
        try:
            self.audio_duration = ffprobe_duration_seconds(audio_path)
            if self.audio_duration == 0.0:
                self.log_message.emit("Error: Could not determine audio duration or audio is 0s long.")
                self.process_finished.emit(-1, "") # Emit failure
                return
        except Exception as e:
            self.log_message.emit(f"Error running ffprobe: {e}")
            self.process_finished.emit(-1, "") # Emit failure
            return

        # 2. Store the output path for later reference
        self.output_path = output_path

        # 3. Build and run command
        cmd_list = self._build_ffmpeg_cmd(
            media_path, audio_path, self.output_path, title,
            text_overlay, text_position, text_size, text_color,
            fade_in, fade_out, self.audio_duration
        )

        self.log_message.emit(f"Executing command: {' '.join(cmd_list)}")

        # Use start() which is non-blocking
        self.process.start("ffmpeg", cmd_list[1:])

    def cancel_process(self):
        """Public method to cancel the running process."""
        if self.process.state() == QProcess.ProcessState.Running:
            self.log_message.emit("--- CANCELLING PROCESS ---")
            self.process.terminate()

# ---------- UI: Main Window ----------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panek Video Program - Enhanced Edition v3.0")
        self.setMinimumSize(700, 900)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # --- Asynchronous Runner ---
        self.ffmpeg_runner = FFmpegRunner()

        # --- UI Sections ---
        self._create_io_widgets()
        self._create_text_overlay_widgets()
        self._create_fade_widgets()
        self._create_action_widgets()
        self._create_status_widgets()
        self._create_footer()
        self._connect_signals()

        # --- State ---
        self.media_path = ""
        self.audio_path = ""
        self.output_dir = str(Path.home()) # Default to user's home directory
        self.output_dir_edit.setText(self.output_dir)
        self.text_color = "white"  # Default text color
        self._check_inputs_ready() # Set initial button state

    def _create_io_widgets(self):
        """Create the input/output widgets using a clean form layout."""
        io_layout = QFormLayout()
        io_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)

        # --- Media Path (Image or Video) ---
        self.media_path_edit = QLineEdit()
        self.media_path_edit.setReadOnly(True)
        self.media_path_edit.setPlaceholderText("Select an image or video file...")
        self.media_browse_btn = QPushButton("Browse...")

        # --- Audio Path ---
        self.audio_path_edit = QLineEdit()
        self.audio_path_edit.setReadOnly(True)
        self.audio_path_edit.setPlaceholderText("Select an audio file...")
        self.audio_browse_btn = QPushButton("Browse...")

        # --- Output Dir ---
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        self.output_dir_browse_btn = QPushButton("Browse...")

        # --- Title ---
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Optional (defaults to timestamp)")

        # Use helper to create the [LineEdit] [Button] widgets
        io_layout.addRow("Media File:", self._create_browse_widget(self.media_path_edit, self.media_browse_btn))
        io_layout.addRow("Audio File:", self._create_browse_widget(self.audio_path_edit, self.audio_browse_btn))
        io_layout.addRow("Output Folder:", self._create_browse_widget(self.output_dir_edit, self.output_dir_browse_btn))
        io_layout.addRow("Video Title:", self.title_edit)

        self.main_layout.addLayout(io_layout)

    def _create_browse_widget(self, line_edit, button):
        """Helper to create the LineEdit + Button combo."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        return widget

    def _create_text_overlay_widgets(self):
        """Create text overlay controls in a group box."""
        group_box = QGroupBox("Text Overlay (Optional)")
        layout = QFormLayout()

        # Text content
        self.text_overlay_edit = QLineEdit()
        self.text_overlay_edit.setPlaceholderText("Enter text to overlay on video...")
        layout.addRow("Text:", self.text_overlay_edit)

        # Text position
        self.text_position_combo = QComboBox()
        self.text_position_combo.addItems(["Top", "Center", "Bottom"])
        self.text_position_combo.setCurrentText("Center")
        layout.addRow("Position:", self.text_position_combo)

        # Text size
        self.text_size_spin = QSpinBox()
        self.text_size_spin.setRange(12, 200)
        self.text_size_spin.setValue(48)
        self.text_size_spin.setSuffix(" pt")
        layout.addRow("Size:", self.text_size_spin)

        # Text color button
        self.text_color_btn = QPushButton("Choose Color")
        self.text_color_btn.clicked.connect(self._choose_text_color)
        color_widget = QWidget()
        color_layout = QHBoxLayout(color_widget)
        color_layout.setContentsMargins(0, 0, 0, 0)
        self.text_color_preview = QLabel("      ")
        self.text_color_preview.setStyleSheet("background-color: white; border: 1px solid gray;")
        color_layout.addWidget(self.text_color_preview)
        color_layout.addWidget(self.text_color_btn)
        color_layout.addStretch()
        layout.addRow("Color:", color_layout)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _create_fade_widgets(self):
        """Create fade transition controls in a group box."""
        group_box = QGroupBox("Fade Transitions (Optional)")
        layout = QFormLayout()

        # Fade in duration
        self.fade_in_spin = QDoubleSpinBox()
        self.fade_in_spin.setRange(0, 10)
        self.fade_in_spin.setValue(0)
        self.fade_in_spin.setSingleStep(0.5)
        self.fade_in_spin.setSuffix(" sec")
        layout.addRow("Fade In:", self.fade_in_spin)

        # Fade out duration
        self.fade_out_spin = QDoubleSpinBox()
        self.fade_out_spin.setRange(0, 10)
        self.fade_out_spin.setValue(0)
        self.fade_out_spin.setSingleStep(0.5)
        self.fade_out_spin.setSuffix(" sec")
        layout.addRow("Fade Out:", self.fade_out_spin)

        group_box.setLayout(layout)
        self.main_layout.addWidget(group_box)

    def _choose_text_color(self):
        """Open color picker dialog for text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_color = color.name()
            self.text_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid gray;")

    def _create_action_widgets(self):
        """Create the Start and Cancel buttons."""
        action_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Processing")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        
        action_layout.addStretch()
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.cancel_btn)
        self.main_layout.addLayout(action_layout)

    def _create_status_widgets(self):
        """Create the status label, progress bar, and log view."""
        self.status_label = QLabel("Idle")
        self.status_label.setStyleSheet("font-style: italic;")
        self.main_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)
        
        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setStyleSheet("font-family: monospace;")
        self.main_layout.addWidget(self.status_log)

    def _create_footer(self):
        """Create footer with FFmpeg attribution."""
        footer = QLabel()
        footer.setText(
            '<div style="text-align: center; color: #888; font-size: 11px; padding: 5px;">'
            'This software uses <a href="https://ffmpeg.org">FFmpeg</a> licensed under the '
            '<a href="https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html">LGPL v2.1</a> or later'
            '</div>'
        )
        footer.setTextFormat(Qt.TextFormat.RichText)
        footer.setOpenExternalLinks(True)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(footer)

    def _connect_signals(self):
        """Connect all widget and runner signals to their slots."""
        # Button signals
        self.media_browse_btn.clicked.connect(self._on_browse_media)
        self.audio_browse_btn.clicked.connect(self._on_browse_audio)
        self.output_dir_browse_btn.clicked.connect(self._on_browse_output_dir)

        self.start_btn.clicked.connect(self._start_processing)
        self.cancel_btn.clicked.connect(self.ffmpeg_runner.cancel_process)

        # FFmpegRunner signals
        self.ffmpeg_runner.process_started.connect(self._on_process_started)
        self.ffmpeg_runner.process_finished.connect(self._on_process_finished)
        self.ffmpeg_runner.log_message.connect(self.status_log.append)
        self.ffmpeg_runner.progress_updated.connect(self._on_progress_update)

    # --- File Dialog Slots ---

    def _on_browse_media(self):
        """Open a native file dialog to select an image or video."""
        qt_filter = "Media Files (*.jpg *.jpeg *.png *.webp *.mp4 *.mov *.avi *.mkv *.webm *.flv *.wmv *.m4v *.mpg *.mpeg);;Images (*.jpg *.jpeg *.png *.webp);;Videos (*.mp4 *.mov *.avi *.mkv *.webm);;All files (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Choose Media File", self.output_dir, qt_filter)
        if path:
            self.media_path = path
            self.media_path_edit.setText(path)
            self._check_inputs_ready()

    def _on_browse_audio(self):
        """Open a native file dialog to select audio."""
        qt_filter = "Audio (*.mp3 *.wav);;All files (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Choose Audio", self.output_dir, qt_filter)
        if path:
            self.audio_path = path
            self.audio_path_edit.setText(path)
            self._check_inputs_ready()
    
    def _on_browse_output_dir(self):
        """Open a native directory dialog."""
        path = QFileDialog.getExistingDirectory(self, "Choose Output Folder", self.output_dir)
        if path:
            self.output_dir = path
            self.output_dir_edit.setText(path)
            self._check_inputs_ready()

    def _check_inputs_ready(self):
        """Enable the start button only if all inputs are valid."""
        ready = bool(self.media_path and self.audio_path and self.output_dir)
        self.start_btn.setEnabled(ready)

    # --- FFmpegRunner Slots ---

    def _start_processing(self):
        """
        Trigger the runner to start processing.
        Includes validation and overwrite checks.
        """
        # --- 1. Pre-flight validation checks ---
        if not os.path.exists(self.media_path):
            QMessageBox.warning(self, "Input Error", f"Media file not found:\n{self.media_path}")
            return

        if not os.path.exists(self.audio_path):
            QMessageBox.warning(self, "Input Error", f"Audio file not found:\n{self.audio_path}")
            return

        if not os.path.isdir(self.output_dir):
            QMessageBox.warning(self, "Input Error", f"Output directory not found:\n{self.output_dir}")
            return

        # --- 2. Calculate output path and title ---
        title_text = self.title_edit.text()
        title = title_text.strip() or datetime.datetime.now().strftime("panek-video-%Y%m%d-%H%M%S")
        title = sanitize_filename(title)
        output_path = os.path.abspath(os.path.join(self.output_dir, f"{title}.mp4"))

        # --- 3. Implement overwrite check ---
        if os.path.exists(output_path):
            reply = QMessageBox.question(self, "Overwrite Confirmation",
                f"The file already exists:\n{output_path}\n\nDo you want to overwrite it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) # Default to No

            if reply == QMessageBox.StandardButton.No:
                self.status_label.setText("Idle. Overwrite cancelled by user.")
                return

        # --- 4. Collect text overlay and fade parameters ---
        text_overlay = self.text_overlay_edit.text().strip()
        text_position = self.text_position_combo.currentText().lower()
        text_size = self.text_size_spin.value()
        text_color = self.text_color
        fade_in = self.fade_in_spin.value()
        fade_out = self.fade_out_spin.value()

        # --- 5. Start the runner with all parameters ---
        self.ffmpeg_runner.start_processing(
            self.media_path,
            self.audio_path,
            output_path,
            title,
            text_overlay,
            text_position,
            text_size,
            text_color,
            fade_in,
            fade_out
        )

    def _on_process_started(self):
        """Update UI to reflect the "running" state."""
        self.status_log.clear()
        self.status_label.setText("Processing...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self._set_inputs_enabled(False)

    def _on_process_finished(self, exit_code, output_path):
        """Update UI to reflect the "finished" state."""
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self._set_inputs_enabled(True)
        self.progress_bar.setVisible(False)

        if exit_code == 0:
            self.status_label.setText("Process complete.")
            self.progress_bar.setValue(100)
            self._show_complete_dialog(output_path)
        else:
            self.status_label.setText(f"Process failed (Code: {exit_code})")
            self.progress_bar.setValue(0)
    
    def _on_progress_update(self, pct):
        """Update the progress bar and status label."""
        self.progress_bar.setValue(pct)
        self.status_label.setText(f"Processing... {pct}%")

    def _set_inputs_enabled(self, enabled):
        """Enable or disable all input widgets to prevent errors during render."""
        self.media_browse_btn.setEnabled(enabled)
        self.audio_browse_btn.setEnabled(enabled)
        self.output_dir_browse_btn.setEnabled(enabled)
        self.title_edit.setEnabled(enabled)
        self.text_overlay_edit.setEnabled(enabled)
        self.text_position_combo.setEnabled(enabled)
        self.text_size_spin.setEnabled(enabled)
        self.text_color_btn.setEnabled(enabled)
        self.fade_in_spin.setEnabled(enabled)
        self.fade_out_spin.setEnabled(enabled)
    
    def _show_complete_dialog(self, output_path):
        """Show the custom "Complete" dialog."""
        dlg = CompleteDialog(output_path, self)
        result = dlg.exec()
        
        # Use QDialog.Accepted enum
        if result == QDialog.Accepted:
            self._reset_for_next()
        else:
            QApplication.instance().quit()

    def _reset_for_next(self):
        """Clear inputs to prepare for the next render."""
        self.media_path = ""
        self.audio_path = ""
        self.media_path_edit.clear()
        self.audio_path_edit.clear()
        self.title_edit.clear()
        self.text_overlay_edit.clear()
        self.text_position_combo.setCurrentText("Center")
        self.text_size_spin.setValue(48)
        self.text_color = "white"
        self.text_color_preview.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.fade_in_spin.setValue(0)
        self.fade_out_spin.setValue(0)
        self.status_log.clear()
        self.status_label.setText("Idle")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.start_btn.setEnabled(False)

# ---------- Application Entry Point ----------

if __name__ == "__main__":
    # Ensure ffmpeg/ffprobe exist before launching the app
    try:
        ensure_ffmpeg()
    except RuntimeError as e:
        # If app fails to init, show a critical error before the main loop
        app_temp = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, "Fatal Error", f"{e}\nPlease install ffmpeg and ensure it is in your system's PATH.")
        sys.exit(1)

    # Initialize the Qt Application
    app = QApplication(sys.argv)

    # Apply the dark theme globally
    qdarktheme.setup_theme("dark") 

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Start the Qt event loop
    sys.exit(app.exec())
