#!/usr/bin/env python3
# Panek Video Program - Qt edition (tutorial + gray->green render state)
# Deps: ffmpeg, ffprobe, python3-pyqt5
# Optional deps for native dialogs: kdialog, zenity, osascript

import os, re, sys, shutil, datetime, subprocess
from pathlib import Path

from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QProgressBar, QTextEdit,
    QDialog, QDialogButtonBox
)

WIDTH, HEIGHT, FPS, CRF = 1920, 1080, 30, 20
AUDIO_BITRATE = "192k"

# ---------- utilities ----------

def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def ensure_ffmpeg():
    if not have("ffmpeg") or not have("ffprobe"):
        raise RuntimeError("ffmpeg or ffprobe not found in PATH")

def sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\-. ]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "output"

# ---------- native dialog helpers (cascade: kdialog -> zenity -> osascript -> Qt) ----------

# kdialog (KDE/Plasma)
def kde_getopenfilename(title: str, filters: list) -> str:
    if have("kdialog"):
        flt = " | ".join(filters)
        proc = subprocess.run(
            ["kdialog", "--getopenfilename", os.path.expanduser("~"), flt, "--title", title],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return proc.stdout.strip()
    return ""

def kde_getexistingdirectory(title: str, start_dir: str) -> str:
    if have("kdialog"):
        proc = subprocess.run(
            ["kdialog", "--getexistingdirectory", start_dir, "--title", title],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return proc.stdout.strip()
    return ""

# zenity (GNOME, XFCE, Cinnamon, MATE, many Linux distros)
def zenity_getopenfilename(title: str, patterns: list) -> str:
    if not have("zenity"):
        return ""
    # Build one or more --file-filter entries like: "Images | *.jpg *.jpeg *.png *.webp"
    args = ["zenity", "--file-selection", "--title", title]
    if patterns:
        args += ["--file-filter", f"Supported | {' '.join(patterns)}",
                 "--file-filter", "All files | *"]
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.stdout.strip()

def zenity_getexistingdirectory(title: str, start_dir: str) -> str:
    if not have("zenity"):
        return ""
    args = ["zenity", "--file-selection", "--directory", "--title", title]
    if start_dir:
        args += ["--filename", os.path.join(start_dir, "")]
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.stdout.strip()

# osascript (macOS)
def osascript_choose_file(title: str) -> str:
    if sys.platform != "darwin" or not have("osascript"):
        return ""
    # Use System Events for a standard macOS dialog. No filetype filter to avoid fragility.
    script = f'''tell application "System Events"
set f to choose file with prompt "{title}"
POSIX path of f
end tell'''
    proc = subprocess.run(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.stdout.strip()

def osascript_choose_folder(title: str, start_dir: str) -> str:
    if sys.platform != "darwin" or not have("osascript"):
        return ""
    start_clause = ""
    if start_dir:
        start_clause = f' default location POSIX file "{start_dir}"'
    script = f'''tell application "System Events"
set f to choose folder with prompt "{title}"{start_clause}
POSIX path of f
end tell'''
    proc = subprocess.run(["osascript", "-e", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return proc.stdout.strip()

# Qt generic fallback
def qt_getopenfilename(parent: QWidget, title: str, name_filter: str) -> str:
    path, _ = QFileDialog.getOpenFileName(parent, title, str(Path.home()), name_filter)
    return path or ""

def qt_getexistingdirectory(parent: QWidget, title: str, start_dir: str) -> str:
    path = QFileDialog.getExistingDirectory(parent, title, start_dir)
    return path or ""

# High level cascade
def cascade_get_open_file(parent: QWidget, title: str, kdialog_filters: list, zenity_patterns: list, qt_name_filter: str) -> str:
    return (
        kde_getopenfilename(title, kdialog_filters) or
        zenity_getopenfilename(title, zenity_patterns) or
        osascript_choose_file(title) or
        qt_getopenfilename(parent, title, qt_name_filter)
    )

def cascade_get_directory(parent: QWidget, title: str, start_dir: str) -> str:
    return (
        kde_getexistingdirectory(title, start_dir) or
        zenity_getexistingdirectory(title, start_dir) or
        osascript_choose_folder(title, start_dir) or
        qt_getexistingdirectory(parent, title, start_dir)
    )

# ---------- media ----------

def ffprobe_duration_seconds(path: str) -> float:
    proc = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        return float(proc.stdout.strip())
    except Exception:
        return 0.0

def build_ffmpeg_cmd(image_path: str, audio_path: str, out_path: str, title: str) -> list:
    vf = f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2"
    return [
        "ffmpeg","-y","-loop","1","-i",image_path,"-i",audio_path,
        "-c:v","libx264","-preset","medium","-crf",str(CRF),"-tune","stillimage",
        "-vf",vf,"-r",str(FPS),"-pix_fmt","yuv420p",
        "-c:a","aac","-b:a",AUDIO_BITRATE,"-shortest",
        "-movflags","+faststart",
        "-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709",
        "-metadata",f"title={title}",
        "-progress","pipe:2","-nostats",
        out_path,
    ]

# ---------- UI ----------

class CompleteDialog(QDialog):
    def __init__(self, out_path: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Render complete")
        self.setModal(True)
        self.resize(520, 220)

        self.timer = QTimer(self); self.timer.timeout.connect(self._tick)
        self.seconds = 30

        lay = QVBoxLayout(self)
        self.msg = QLabel(self)
        self.msg.setTextFormat(Qt.RichText)
        self.msg.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.msg.setOpenExternalLinks(True)
        self.out_path = out_path
        lay.addWidget(self.msg)

        btns = QDialogButtonBox(self)
        self.again_btn = btns.addButton("Render another", QDialogButtonBox.AcceptRole)
        self.close_btn = btns.addButton("Close now", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

        self._refresh_text()
        self.timer.start(1000)

    def _refresh_text(self):
        self.msg.setText(
            f"Video created:<br><code>{self.out_path}</code><br><br>"
            f"Auto closing in <b>{self.seconds}</b> seconds.<br><br>"
            '<a href="https://buymeacoffee.com/prompternick">Buy Me a Coffee</a>  •  '
            '<a href="https://www.patternripple.com/lab">PatternRipple Lab</a>'
        )

    def _tick(self):
        self.seconds -= 1
        if self.seconds <= 0:
            self.reject()
            return
        self._refresh_text()

class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panek Video Program")
        self.setMinimumWidth(680)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16,16,16,16); lay.setSpacing(10)

        header = QLabel("Panek Video Program"); header.setAlignment(Qt.AlignHCenter)
        header.setStyleSheet("font-size:20px;font-weight:600;")
        sub = QLabel("Create a 16:9 MP4 from an image and an MP3/WAV"); sub.setAlignment(Qt.AlignHCenter)
        sub.setStyleSheet("color:#666;")

        # One-line tutorial
        tutorial = QLabel("Choose image and audio, optionally set title and output, then click Render.")
        tutorial.setAlignment(Qt.AlignHCenter)
        tutorial.setStyleSheet("color:#777;")

        # Output folder
        out_row = QHBoxLayout()
        self.output_dir = os.getcwd()
        self.output_dir_edit = QLineEdit(self.output_dir); self.output_dir_edit.setReadOnly(True)
        out_btn = QPushButton("Choose Output Folder"); out_btn.clicked.connect(self.on_choose_output_dir)
        out_row.addWidget(self.output_dir_edit,1); out_row.addWidget(out_btn)

        # Title
        title_row = QHBoxLayout()
        self.title_input = QLineEdit(); self.title_input.setPlaceholderText("Optional title. Blank uses timestamp.")
        title_row.addWidget(self.title_input,1)

        # Choose buttons
        choose_row = QHBoxLayout()
        self.choose_img_btn = QPushButton("Choose Image")
        self.choose_img_btn.clicked.connect(self.on_choose_image)
        self.choose_aud_btn = QPushButton("Choose Audio")
        self.choose_aud_btn.clicked.connect(self.on_choose_audio)
        choose_row.addWidget(self.choose_img_btn)
        choose_row.addWidget(self.choose_aud_btn)

        # Selected paths preview
        self.img_label = QLabel("Image: not selected"); self.img_label.setStyleSheet("color:#555;")
        self.aud_label = QLabel("Audio: not selected"); self.aud_label.setStyleSheet("color:#555;")

        # Render button with dynamic style
        self.make_btn = QPushButton("Render Video")
        self._apply_render_style(enabled=False)
        self.make_btn.setEnabled(False)
        self.make_btn.clicked.connect(self.on_render_clicked)

        # Progress + log
        self.progress = QProgressBar(); self.progress.setRange(0,100); self.progress.setValue(0)
        self.status = QLabel("Idle"); self.status.setStyleSheet("color:#555;")
        self.log = QTextEdit(); self.log.setReadOnly(True); self.log.setMinimumHeight(180); self.log.setStyleSheet("font-family:monospace;")

        # Footer links
        footer = QLabel(
            '<div style="text-align:center;">'
            '<a href="https://buymeacoffee.com/prompternick" style="color:#0077cc;">Buy Me a Coffee</a>'
            '  •  '
            '<a href="https://www.patternripple.com/lab" style="color:#0077cc;">PatternRipple Lab</a>'
            '</div>'
        )
        footer.setOpenExternalLinks(True); footer.setAlignment(Qt.AlignHCenter)

        # Layout
        lay.addWidget(header); lay.addWidget(sub); lay.addWidget(tutorial)
        lay.addLayout(out_row); lay.addLayout(title_row)
        lay.addLayout(choose_row)
        lay.addWidget(self.img_label); lay.addWidget(self.aud_label)
        lay.addWidget(self.make_btn)
        lay.addWidget(self.progress); lay.addWidget(self.status); lay.addWidget(self.log); lay.addWidget(footer)

        # State
        self.image_path = ""; self.audio_path = ""; self.out_path = ""; self.audio_duration = 0.0; self.proc = None

    # Styling helper
    def _apply_render_style(self, enabled: bool):
        if enabled:
            self.make_btn.setStyleSheet(
                "QPushButton { background-color:#2ecc71; color:white; font-weight:600; padding:8px 14px; }"
                "QPushButton:hover { background-color:#28b862; }"
            )
        else:
            self.make_btn.setStyleSheet(
                "QPushButton { background-color:#e0e0e0; color:#444; padding:8px 14px; }"
            )

    def append_log(self, s: str): self.log.append(s)

    def _maybe_enable_render(self):
        ready = bool(self.image_path and self.audio_path)
        self.make_btn.setEnabled(ready)
        self._apply_render_style(enabled=ready)

    # -------- dialog entry points using cascade --------

    def on_choose_output_dir(self):
        path = cascade_get_directory(self, "Choose output folder", self.output_dir)
        if path:
            self.output_dir = path.rstrip("/")  # normalize macOS path from osascript
            self.output_dir_edit.setText(self.output_dir)
            self.append_log(f"Output folder: {self.output_dir}")

    def on_choose_image(self):
        # Filters for each layer
        kdlg_filters = ["Images (*.jpg *.jpeg *.png *.webp)", "All files (*.*)"]
        zen_patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
        qt_filter = "Images (*.jpg *.jpeg *.png *.webp);;All files (*.*)"
        path = cascade_get_open_file(self, "Choose 16:9 image", kdlg_filters, zen_patterns, qt_filter)
        if path:
            self.image_path = path
            self.img_label.setText(f"Image: {path}")
            self.append_log(f"Image: {path}")
            self._maybe_enable_render()

    def on_choose_audio(self):
        kdlg_filters = ["Audio (*.mp3 *.wav)", "All files (*.*)"]
        zen_patterns = ["*.mp3", "*.wav"]
        qt_filter = "Audio (*.mp3 *.wav);;All files (*.*)"
        path = cascade_get_open_file(self, "Choose audio MP3 or WAV", kdlg_filters, zen_patterns, qt_filter)
        if path:
            self.audio_path = path
            self.aud_label.setText(f"Audio: {path}")
            self.append_log(f"Audio: {path}")
            self._maybe_enable_render()

    # -------- render pipeline --------

    def on_render_clicked(self):
        try:
            ensure_ffmpeg()
        except RuntimeError as e:
            self.append_log(str(e)); self.status.setText("ffmpeg not found"); return

        if not (self.image_path and self.audio_path):
            self.status.setText("Choose image and audio"); return

        title = self.title_input.text().strip() or datetime.datetime.now().strftime("panek-video-%Y%m%d-%H%M%S")
        title = sanitize_filename(title)

        self.audio_duration = ffprobe_duration_seconds(self.audio_path)
        self.progress.setRange(0,100); self.progress.setValue(0)

        self.out_path = os.path.abspath(os.path.join(self.output_dir, f"{title}.mp4"))
        cmd = build_ffmpeg_cmd(self.image_path, self.audio_path, self.out_path, title)
        self.append_log("Starting ffmpeg:"); self.append_log(" ".join(cmd)); self.status.setText("Rendering...")

        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.readyReadStandardError.connect(self.on_ffmpeg_output)
        self.proc.readyReadStandardOutput.connect(self.on_ffmpeg_output)
        self.proc.finished.connect(self.on_ffmpeg_finished)
        self.proc.start(cmd[0], cmd[1:])

    def on_ffmpeg_output(self):
        if not self.proc: return
        data = (bytes(self.proc.readAllStandardError()) + bytes(self.proc.readAllStandardOutput())).decode("utf-8", errors="replace")
        for line in data.strip().splitlines():
            self.append_log(line)
            m = re.search(r"out_time_ms=(\d+)", line)
            if m and self.audio_duration > 0:
                pct = int(min(100, (int(m.group(1)) / 1_000_000 / self.audio_duration) * 100))
                self.progress.setValue(pct); self.status.setText(f"Rendering {pct}%")

    def on_ffmpeg_finished(self, code: int, _status):
        if code == 0:
            self.progress.setValue(100); self.status.setText(f"Done: {self.out_path}")
            self._post_success_prompt()
        else:
            self.status.setText(f"ffmpeg failed (code {code})")

    def _post_success_prompt(self):
        dlg = CompleteDialog(self.out_path, self)
        result = dlg.exec_()  # Accepted: render another. Rejected or timeout: close.
        if result == QDialog.Accepted:
            self._reset_for_next()
        else:
            QApplication.instance().quit()

    def _reset_for_next(self):
        self.image_path = ""; self.audio_path = ""; self.out_path = ""
        self.img_label.setText("Image: not selected")
        self.aud_label.setText("Audio: not selected")
        self.progress.setValue(0); self.status.setText("Idle")
        self.make_btn.setEnabled(False)
        self._apply_render_style(enabled=False)

# ---------- app ----------

def main():
    app = QApplication(sys.argv)
    ui = MainUI(); ui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
