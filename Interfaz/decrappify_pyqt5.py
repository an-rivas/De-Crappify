"""
Referencias
1. https://stackoverflow.com/questions/6444548/how-do-i-get-the-picture-size-with-pil Gary S

2. https://stackoverflow.com/questions/43486077/how-to-get-image-from-imagedraw-in-pil Claudio

3. https://stackoverflow.com/questions/18675592/how-to-use-imageqt ekhumoro

4. https://www.geeksforgeeks.org/python-pil-imagedraw-draw-line/

5. https://pillow.readthedocs.io/en/3.1.x/reference/ImageDraw.html Line

6. https://www.geeksforgeeks.org/python-pil-image-save-method/ Save

7. https://python-forum.io/Thread-PYQT5-Crashing-when-using-hide-and-show Hide, Show

8. https://www.learnpyqt.com/courses/start/layouts/ Layout

9. https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py Inspo

10. https://gist.github.com/acbetter/32c575803ec361c3e82064e60db4e3e0 Inspo

11. https://www.learnpyqt.com/courses/custom-widgets/bitmap-graphics/ principal

12. https://github.com/shkolovy/simple-photo-editor/blob/404be876848ce86bd871f1d6f7992c4679eb9e0f/photo_editor.py#L460 principal
"""

import sys
import ntpath

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5 import QtGui

from functools import partial

from PIL import Image, ImageQt

from functions import _apply_img_changes , redneuronal

# original img, can't be modified
_img_original = None
_img_preview = None

BTN_MIN_WIDTH = 120

class tuGfa (QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.main_layout = QVBoxLayout()
        self.btn_layout = QHBoxLayout()

        self.setWindowTitle('Decrapify')

        self.img_lbl = QLabel()
        #self.img_lbl.setAlignment(Qt.AlignCenter)
        self.file_name = None
        
        self.last_x, self.last_y = None, None
        
        # Botones
        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.upload_btn.clicked.connect(self.on_upload)
        self.upload_btn.setEnabled(True)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.reset_btn.clicked.connect(self.on_reset)
        self.reset_btn.setEnabled(False)
        self.reset_btn.hide()
        
        self.process_btn = QPushButton("Process")
        self.process_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.process_btn.clicked.connect(self.on_process)
        self.process_btn.setEnabled(False)
        self.process_btn.hide()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setMinimumWidth(BTN_MIN_WIDTH)
        self.save_btn.clicked.connect(self.on_save)
        self.save_btn.setEnabled(False)
        self.save_btn.hide()
        
        self.main_layout.addWidget(self.img_lbl)
        
        self.btn_layout.setAlignment(Qt.AlignCenter)
        self.btn_layout.addWidget(self.upload_btn)
        self.btn_layout.addWidget(self.reset_btn)
        self.btn_layout.addWidget(self.process_btn)
        self.btn_layout.addWidget(self.save_btn)
        
        
        self.main_layout.addLayout( self.btn_layout )
        widget = QWidget()
        widget.setLayout(self.main_layout)
        self.setCentralWidget(widget)
        
        self.points = []
        self.img_path = None
    
    def on_upload(self):
        self.img_path, _ = QFileDialog.getOpenFileName(self, "Open image", "/Users", "Images (*.png *jpg)")

        if self.img_path:
            global _img_original
            _img_original = Image.open(self.img_path)

            global _img_preview
            _img_preview = _img_original.copy()

            self.file_name = ntpath.basename(self.img_path)

            pix = QPixmap(self.img_path)
            self.img_lbl.setPixmap(pix)

            self.reset_btn.setEnabled(True)
            self.reset_btn.show()
            self.process_btn.setEnabled(True)
            self.process_btn.show()
            self.upload_btn.setEnabled(False)
            self.upload_btn.hide()

    def mouseMoveEvent(self, e):
        if self.last_x is None: # First event.
            self.last_x = e.x()
            self.last_y = e.y()
            return # Ignore the first time.
        
        global _img_original
        size = _img_original.size
        painter = QtGui.QPainter(self.img_lbl.pixmap())
        
        pen = QtGui.QPen()
        pen.setColor(QtGui.QColor('white'))
        painter.setPen(pen)
        
        self.points.append((e.x(), e.y()))
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()

        # Update the origin for next time.
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None 
        
        global _img_preview
        _img_preview = _apply_img_changes(_img_preview, self.points)
        self.points = []

    def on_save(self):
        new_img_path, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", f"{self.file_name}_decrapify.jpg", "Images (*.png *.jpg)")

        if new_img_path:
            _img_preview.save(new_img_path)

    def on_process(self):
        global _img_preview
        _img_preview = redneuronal(self.img_path)
        self.place_preview_img()
        
        self.reset_btn.setEnabled(False)
        self.reset_btn.hide()
        self.process_btn.setEnabled(False)
        self.process_btn.hide()
        
        self.save_btn.setEnabled(True)
        self.save_btn.show()

    def place_preview_img(self):#***
        preview_pix = ImageQt.toqpixmap(_img_preview)
        self.img_lbl.setPixmap(preview_pix)

    def on_reset(self):#***
        global _img_preview
        _img_preview = _img_original.copy()

        self.place_preview_img()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = tuGfa()
    window.show()
    sys.exit(app.exec_())
    
