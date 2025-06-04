import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QFileDialog, QPushButton, QVBoxLayout, QWidget, QMainWindow
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPointF, QRectF


class PuzzlePiece(QGraphicsPixmapItem):
    def __init__(self, pixmap, correct_pos):
        super().__init__(pixmap)
        self.setFlags(
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.correct_pos = correct_pos
        self.locked = False

    def mouseReleaseEvent(self, event):
        if not self.locked:
            dist = (self.pos() - self.correct_pos).manhattanLength()
            if dist < 20:
                self.setPos(self.correct_pos)
                self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable, False)
                self.locked = True
        super().mouseReleaseEvent(event)


class RectPuzzleGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Puzzle - Prostokąty")
        self.setGeometry(100, 100, 1000, 800)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)

        self.load_button = QPushButton("Wczytaj obrazek")
        self.load_button.clicked.connect(self.load_image)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.load_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Wybierz obrazek", "", "Obrazy (*.png *.jpg *.jpeg)")
        if not file_path:
            return

        original_pixmap = QPixmap(file_path)
        self.scene.clear()

        rows, cols = 4, 4
        piece_width = original_pixmap.width() // cols
        piece_height = original_pixmap.height() // rows

        for row in range(rows):
            for col in range(cols):
                rect = QRectF(col * piece_width, row * piece_height, piece_width, piece_height)
                piece = original_pixmap.copy(rect.toRect())
                correct_pos = QPointF(col * piece_width, row * piece_height)
                item = PuzzlePiece(piece, correct_pos)
                item.setPos(random.randint(600, 900), random.randint(100, 700))
                self.scene.addItem(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RectPuzzleGame()
    window.show()
    sys.exit(app.exec())
