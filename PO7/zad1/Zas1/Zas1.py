import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QPushButton, QVBoxLayout, QWidget, QColorDialog, QComboBox,
    QSpinBox, QFileDialog, QHBoxLayout, QGraphicsItem,
    QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPolygonItem
)
from PyQt6.QtGui import QBrush, QColor, QPainter, QImage, QPolygonF
from PyQt6.QtCore import Qt, QPointF


class VectorEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prosty edytor grafiki wektorowej")
        self.setGeometry(100, 100, 1000, 600)

        # SCENA
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # DOMYŚLNY KOLOR
        self.current_color = QColor("blue")

        # KONTROLKI
        self.shape_box = QComboBox()
        self.shape_box.addItems(["Prostokąt", "Elipsa", "Trójkąt"])

        self.color_btn = QPushButton("Wybierz kolor")
        self.color_btn.clicked.connect(self.choose_color)

        self.add_btn = QPushButton("Dodaj kształt")
        self.add_btn.clicked.connect(self.add_shape)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(10, 300)
        self.width_spin.setValue(100)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(10, 300)
        self.height_spin.setValue(100)

        self.up_btn = QPushButton("Wyżej")
        self.up_btn.clicked.connect(self.bring_forward)

        self.down_btn = QPushButton("Niżej")
        self.down_btn.clicked.connect(self.send_backward)

        self.del_btn = QPushButton("Usuń")
        self.del_btn.clicked.connect(self.delete_shape)

        self.save_btn = QPushButton("Zapisz jako PNG")
        self.save_btn.clicked.connect(self.save_as_png)

        # LEWY PANEL
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.shape_box)
        left_layout.addWidget(self.color_btn)
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.width_spin)
        left_layout.addWidget(self.height_spin)
        left_layout.addWidget(self.up_btn)
        left_layout.addWidget(self.down_btn)
        left_layout.addWidget(self.del_btn)
        left_layout.addWidget(self.save_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # GŁÓWNY LAYOUT
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.view)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color

    def add_shape(self):
        shape_type = self.shape_box.currentText()
        width = self.width_spin.value()
        height = self.height_spin.value()
        color = self.current_color

        if shape_type == "Prostokąt":
            item = QGraphicsRectItem(0, 0, width, height)
        elif shape_type == "Elipsa":
            item = QGraphicsEllipseItem(0, 0, width, height)
        elif shape_type == "Trójkąt":
            polygon = QPolygonF([
                QPointF(width / 2, 0),
                QPointF(0, height),
                QPointF(width, height)
            ])
            item = QGraphicsPolygonItem(polygon)
        else:
            return

        item.setBrush(QBrush(color))
        item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        item.setSelected(True)  # zaznacz figurę po dodaniu
        self.scene.addItem(item)

    def bring_forward(self):
        for item in self.scene.selectedItems():
            item.setZValue(item.zValue() + 1)

    def send_backward(self):
        for item in self.scene.selectedItems():
            item.setZValue(item.zValue() - 1)

    def delete_shape(self):
        for item in self.scene.selectedItems():
            self.scene.removeItem(item)

    def save_as_png(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Zapisz jako PNG", "", "PNG Files (*.png)")
        if file_path:
            image = QImage(self.view.viewport().size(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            painter = QPainter(image)
            self.view.render(painter)
            painter.end()
            image.save(file_path, "PNG")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorEditor()
    window.show()
    sys.exit(app.exec())
