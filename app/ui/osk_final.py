from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import os


def resource_path_dev(relative_path: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))  # ui → app
    return os.path.join(base, relative_path)


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return resource_path_dev(relative_path)


class MiniKeyboard(QtWidgets.QFrame):
    keyPressed = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.user_moved = False

        # Load overlay image
        self.image_path = resource_path("banners/NovaTurn_OSK.png")

        self.overlay = QtWidgets.QLabel(self)
        self.overlay.setPixmap(QtGui.QPixmap(self.image_path))
        self.overlay.setScaledContents(True)
        self.overlay.setGeometry(self.rect())
        self.overlay.lower()
        self.overlay.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.setObjectName("miniKeyboard")
        self.setFixedHeight(300)

        self.setStyleSheet("""
        QPushButton {
            background-color: rgba(30, 30, 30, 160);
            color: white;
            font-size: 18px;
            border-radius: 6px;
            padding: 8px;
        }
        QPushButton:pressed {
            background-color: rgba(255, 215, 0, 180);
            color: black;
        }
        """)

        layout = QtWidgets.QGridLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)

        # ------------------------------------------------------------
        # Close button ABOVE overlay (manual position)
        # ------------------------------------------------------------
        self.close_btn = QtWidgets.QPushButton("×", self)
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setToolTip("Close Keyboard")

        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 140);
                color: white;
                font-size: 16px;
                border: 1px solid #555;
                border-radius: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 180);
            }
        """)

        self.close_btn.clicked.connect(self.hide)
        self.close_btn.raise_()

        rows = [
            list("1234567890"),
            list("QWERTYUIOP"),
            list("ASDFGHJKL"),
            list("ZXCVBNM"),
        ]

        # Letter/number rows
        for r, row in enumerate(rows):
            for c, char in enumerate(row):
                btn = QtWidgets.QPushButton(char)
                btn.clicked.connect(lambda _, ch=char: self.keyPressed.emit(ch))
                layout.addWidget(btn, r, c)

        # NovaTurn label beside the M row
        self.label = QtWidgets.QLabel("NovaTurn’s Draggable Keyboard")
        self.label.setStyleSheet("color: #CCCCCC; font-size: 12px;")
        self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.label, 3, len(rows[3]), 1, 3)

        # Space bar
        space = QtWidgets.QPushButton("SPACE")
        space.clicked.connect(lambda: self.keyPressed.emit(" "))
        layout.addWidget(space, 4, 0, 1, 6)

        # Backspace
        back = QtWidgets.QPushButton("⌫")
        back.clicked.connect(lambda: self.keyPressed.emit("\b"))
        layout.addWidget(back, 4, 6, 1, 2)

        # Enter
        enter = QtWidgets.QPushButton("ENTER")
        enter.clicked.connect(lambda: self.keyPressed.emit("\r"))
        layout.addWidget(enter, 4, 8, 1, 2)

    # ----- Drag handling -----

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() & QtCore.Qt.LeftButton:
            self.user_moved = True
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    # ----- Keep overlay and close button positioned -----

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self.overlay.setGeometry(self.rect())

        # ------------------------------------------------------------
        # Position close button above the “R” in “Keyboard”
        # ------------------------------------------------------------

        label_x = self.label.x()
        label_y = self.label.y()

        # TWEAK HERE:
        # +160 = move right/left
        # -30  = move up/down
        btn_x = label_x + 160
        btn_y = label_y - 30

        self.close_btn.move(btn_x, btn_y)
        self.close_btn.raise_()

    # ----- Block physical keyboard input -----

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        event.accept()
