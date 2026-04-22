# graphic_equalizer.py
import json
import os

from PyQt5 import QtWidgets, QtCore, QtGui


class EqCurveWidget(QtWidgets.QWidget):
    """Widget that draws a smooth EQ curve based on band gains."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gains = [0] * 10
        self._ready = False
        self.setMinimumHeight(120)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        # Delay painting until widget has a valid size
        QtCore.QTimer.singleShot(0, self._enable_painting)

    def _enable_painting(self):
        self._ready = True
        self.update()

    def set_gains(self, gains):
        self.gains = gains[:]
        self.update()

    def paintEvent(self, event):
        if not self._ready:
            return

        super().paintEvent(event)
        if not self.gains:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        rect = self.rect().adjusted(10, 10, -10, -10)
        if rect.width() <= 0 or rect.height() <= 0:
            return

        painter.fillRect(rect, QtGui.QColor("#111111"))

        # Border
        pen = QtGui.QPen(QtGui.QColor("#D4AF37"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRoundedRect(rect, 8, 8)

        # Midline
        grid_pen = QtGui.QPen(QtGui.QColor("#444444"))
        grid_pen.setStyle(QtCore.Qt.DashLine)
        painter.setPen(grid_pen)
        mid_y = rect.center().y()
        painter.drawLine(rect.left(), mid_y, rect.right(), mid_y)

        # Map gains (-12..12) to y
        points = []
        band_count = len(self.gains)
        if band_count < 2:
            return

        for i, g in enumerate(self.gains):
            x = rect.left() + (rect.width() * i) / (band_count - 1)
            norm = (g + 12) / 24.0
            y = rect.bottom() - norm * rect.height()
            points.append(QtCore.QPointF(x, y))

        path = QtGui.QPainterPath()
        path.moveTo(points[0])

        for i in range(1, len(points) - 1):
            p0 = points[i - 1]
            p1 = points[i]
            p2 = points[i + 1]
            c1 = QtCore.QPointF((p0.x() + p1.x()) / 2.0, p0.y())
            c2 = QtCore.QPointF((p1.x() + p2.x()) / 2.0, p2.y())
            path.cubicTo(c1, c2, p2)

        curve_pen = QtGui.QPen(QtGui.QColor("#D4AF37"))
        curve_pen.setWidth(2)
        painter.setPen(curve_pen)
        painter.drawPath(path)


class GraphicEqualizer(QtWidgets.QWidget):
    """
    NovaTurn 10-Band Graphic Equalizer (crash-safe version)

    Features:
    - 10-band octave EQ with vertical sliders
    - Real-time EQ curve graph
    - Built-in presets (Rock, Jazz, Classical, Vocal Boost, Flat)
    - Save/Load user presets to eq_presets.json
    - Optional VLC integration via set_vlc_player(player)
    - Animated slider glow when moved
    - Gold neon outline via inner frame (not on window)
    - A/B comparison (Before/After) button
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NovaTurn Graphic Equalizer")
        self.setMinimumSize(980, 520)

        # Top-level: background only (no styled background attribute, no border)
        self.setStyleSheet("background-color: #1A1A1A;")

        self.frequencies = [
            "31", "62", "125", "250", "500",
            "1k", "2k", "4k", "8k", "16k"
        ]

        self.sliders = []
        self._slider_timers = {}
        self.vlc_player = None  # optional external player reference

        # Presets
        self.built_in_presets = {
            "Flat":        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Rock":        [3, 5, 4, 1, -1, -1, 2, 4, 5, 4],
            "Jazz":        [2, 3, 2, 0, 0, 1, 2, 3, 3, 2],
            "Classical":   [0, 1, 2, 3, 2, 1, 0, -1, -2, -3],
            "Vocal Boost": [-2, -1, 1, 3, 4, 4, 3, 1, -1, -2],
        }
        self.user_presets = {}
        self.presets_file = os.path.join(os.path.dirname(__file__), "eq_presets.json")

        self._ab_active = False
        self._ab_stored_gains = [0] * 10

        self._build_ui()
        self._load_user_presets()
        self._update_curve()
        self._apply_to_vlc()

    # ------------------------------------------------------------
    # PUBLIC: optional VLC integration
    # ------------------------------------------------------------
    def set_vlc_player(self, player):
        """
        Optionally attach a VLC player instance.
        This method is safe to ignore; the EQ will still work visually.
        """
        self.vlc_player = player
        self._apply_to_vlc()

    # ------------------------------------------------------------
    # BUILD UI
    # ------------------------------------------------------------
    def _build_ui(self):
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(12, 12, 12, 12)
        outer_layout.setSpacing(0)

        # Inner frame with gold border (safe, not on window)
        frame = QtWidgets.QFrame()
        frame.setObjectName("eqFrame")
        frame.setStyleSheet("""
            QFrame#eqFrame {
                background-color: #1A1A1A;
                border: 2px solid #D4AF37;
                border-radius: 6px;
            }
        """)
        outer_layout.addWidget(frame)

        main_layout = QtWidgets.QVBoxLayout(frame)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Top: EQ curve
        self.curve_widget = EqCurveWidget(frame)
        main_layout.addWidget(self.curve_widget)

        # Middle: sliders + dB scale
        mid_layout = QtWidgets.QHBoxLayout()
        mid_layout.setSpacing(25)

        sliders_layout = QtWidgets.QHBoxLayout()
        sliders_layout.setSpacing(20)

        for idx, freq in enumerate(self.frequencies):
            vbox = QtWidgets.QVBoxLayout()
            vbox.setSpacing(8)

            label = QtWidgets.QLabel(freq + " Hz")
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setStyleSheet("color: white; font-size: 13px;")
            vbox.addWidget(label)

            slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
            slider.setRange(-12, 12)
            slider.setValue(0)
            slider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
            slider.setTickInterval(3)
            slider.setFixedHeight(260)
            slider.setStyleSheet(self._slider_style(normal=True))
            slider.valueChanged.connect(self._on_slider_changed)
            self.sliders.append(slider)
            vbox.addWidget(slider)

            sliders_layout.addLayout(vbox)

        mid_layout.addLayout(sliders_layout)

        # Right side: dB scale + controls
        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(12)

        db_scale = QtWidgets.QVBoxLayout()
        db_scale.setSpacing(30)

        top = QtWidgets.QLabel("+12 dB")
        mid = QtWidgets.QLabel("0 dB")
        bot = QtWidgets.QLabel("-12 dB")

        for lbl in (top, mid, bot):
            lbl.setStyleSheet("color: white; font-size: 14px;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)

        db_scale.addWidget(top)
        db_scale.addWidget(mid)
        db_scale.addWidget(bot)

        right_layout.addLayout(db_scale)
        right_layout.addSpacing(10)

        # Preset controls
        preset_box = QtWidgets.QGroupBox("Presets")
        preset_box.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px 0 3px;
            }
        """)
        preset_layout = QtWidgets.QVBoxLayout(preset_box)
        preset_layout.setSpacing(6)

        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A1A1A;
                color: white;
                border: 1px solid #555555;
                padding: 2px 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1A1A;
                color: white;
                selection-background-color: #333333;
            }
        """)
        self._refresh_preset_combo()

        btn_apply_preset = QtWidgets.QPushButton("Apply Preset")
        btn_apply_preset.setStyleSheet(self._button_style())
        btn_apply_preset.clicked.connect(self._apply_selected_preset)

        btn_save_preset = QtWidgets.QPushButton("Save Current as Preset")
        btn_save_preset.setStyleSheet(self._button_style())
        btn_save_preset.clicked.connect(self._save_current_as_preset)

        btn_delete_preset = QtWidgets.QPushButton("Delete User Preset")
        btn_delete_preset.setStyleSheet(self._button_style())
        btn_delete_preset.clicked.connect(self._delete_selected_user_preset)

        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(btn_apply_preset)
        preset_layout.addWidget(btn_save_preset)
        preset_layout.addWidget(btn_delete_preset)

        right_layout.addWidget(preset_box)

        # A/B comparison
        self.ab_button = QtWidgets.QPushButton("A/B: Bypass OFF")
        self.ab_button.setCheckable(True)
        self.ab_button.setStyleSheet(self._button_style())
        self.ab_button.toggled.connect(self._toggle_ab)
        right_layout.addWidget(self.ab_button)

        # Reset button
        reset_btn = QtWidgets.QPushButton("Reset (Flat)")
        reset_btn.setStyleSheet(self._button_style())
        reset_btn.clicked.connect(self.reset_sliders)
        right_layout.addWidget(reset_btn)

        right_layout.addStretch()
        mid_layout.addLayout(right_layout)

        main_layout.addLayout(mid_layout)

    # ------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------
    def _slider_style(self, normal=True):
        handle_color = "#D4AF37" if normal else "#FFE680"
        return f"""
        QSlider::groove:vertical {{
            background: #333333;
            width: 6px;
            border-radius: 3px;
        }}
        QSlider::handle:vertical {{
            background: {handle_color};
            height: 18px;
            margin: -4px;
            border-radius: 4px;
        }}
        QSlider::sub-page:vertical {{
            background: #D4AF37;
        }}
        """

    def _button_style(self):
        return """
        QPushButton {
            background-color: #1A1A1A;
            border: 1px solid #D4AF37;
            color: white;
            padding: 4px 8px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #333333;
        }
        QPushButton:checked {
            background-color: #444444;
        }
        """

    # ------------------------------------------------------------
    # SLIDER HANDLING
    # ------------------------------------------------------------
    def _on_slider_changed(self, value):
        slider = self.sender()
        if slider is None:
            return

        # Animated glow: temporarily brighten handle
        slider.setStyleSheet(self._slider_style(normal=False))
        if slider not in self._slider_timers:
            timer = QtCore.QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda s=slider: s.setStyleSheet(self._slider_style(normal=True)))
            self._slider_timers[slider] = timer
        self._slider_timers[slider].start(180)

        self._update_curve()
        self._apply_to_vlc()

    def _get_gains(self):
        return [s.value() for s in self.sliders]

    def _set_gains(self, gains):
        for s, g in zip(self.sliders, gains):
            s.blockSignals(True)
            s.setValue(g)
            s.blockSignals(False)
        self._update_curve()
        self._apply_to_vlc()

    def _update_curve(self):
        self.curve_widget.set_gains(self._get_gains())

    # ------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------
    def reset_sliders(self):
        self._set_gains([0] * len(self.sliders))

    # ------------------------------------------------------------
    # PRESETS
    # ------------------------------------------------------------
    def _refresh_preset_combo(self):
        if not hasattr(self, "preset_combo"):
            return

        current = self.preset_combo.currentText()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()

        for name in sorted(self.built_in_presets.keys()):
            self.preset_combo.addItem(name)

        if self.user_presets:
            self.preset_combo.insertSeparator(self.preset_combo.count())
            for name in sorted(self.user_presets.keys()):
                self.preset_combo.addItem(name)

        self.preset_combo.blockSignals(False)
        if current:
            idx = self.preset_combo.findText(current)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)

    def _apply_selected_preset(self):
        name = self.preset_combo.currentText()
        if name in self.built_in_presets:
            gains = self.built_in_presets[name]
        else:
            gains = self.user_presets.get(name)
        if gains is None:
            return
        self._set_gains(gains)

    def _save_current_as_preset(self):
        gains = self._get_gains()
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Save Preset",
            "Preset name:"
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.built_in_presets:
            QtWidgets.QMessageBox.warning(
                self,
                "Cannot Overwrite Built-in",
                "You cannot overwrite a built-in preset. Choose another name."
            )
            return
        self.user_presets[name] = gains
        self._save_user_presets()
        self._refresh_preset_combo()

    def _delete_selected_user_preset(self):
        name = self.preset_combo.currentText()
        if name in self.user_presets:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Delete Preset",
                f"Delete user preset '{name}'?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                del self.user_presets[name]
                self._save_user_presets()
                self._refresh_preset_combo()

    def _load_user_presets(self):
        if not os.path.exists(self.presets_file):
            return
        try:
            with open(self.presets_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                cleaned = {}
                for k, v in data.items():
                    if isinstance(v, list) and len(v) == 10:
                        cleaned[k] = v
                self.user_presets = cleaned
        except Exception:
            self.user_presets = {}
        self._refresh_preset_combo()

    def _save_user_presets(self):
        try:
            with open(self.presets_file, "w", encoding="utf-8") as f:
                json.dump(self.user_presets, f, indent=2)
        except Exception:
            pass

    # ------------------------------------------------------------
    # A/B COMPARISON
    # ------------------------------------------------------------
    def _toggle_ab(self, checked):
        if checked:
            self._ab_stored_gains = self._get_gains()
            self._set_gains([0] * len(self.sliders))
            self.ab_button.setText("A/B: Bypass ON")
        else:
            self._set_gains(self._ab_stored_gains)
            self.ab_button.setText("A/B: Bypass OFF")

    # ------------------------------------------------------------
    # VLC INTEGRATION (OPTIONAL)
    # ------------------------------------------------------------
    def _apply_to_vlc(self):
        """
        Placeholder for VLC integration.

        If you later call set_vlc_player(player) with a VLC media player
        that supports equalizer bands, you can implement the mapping here.

        Out of the box, this does nothing and is completely safe.
        """
        if self.vlc_player is None:
            return
        # Example (pseudo-code, adjust to your VLC wrapper):
        # gains = self._get_gains()
        # for i, g in enumerate(gains):
        #     self.vlc_player.set_equalizer_band(i, g)
        # self.vlc_player.apply_equalizer()
        pass


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = GraphicEqualizer()
    w.show()
    sys.exit(app.exec_())

