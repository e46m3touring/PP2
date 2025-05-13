import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QWidget, QVBoxLayout, QSplitter, QLabel
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
import pyqtgraph as pg

# Model danych do wyświetlania DataFrame w QTableView
class PandasModel(QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        super().__init__(parent)
        self._df = df

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)
        return QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            else:
                return str(self._df.index[section])
        return QVariant()

# Główne okno aplikacji
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather Data Analysis")
        # Wczytaj dane z pliku CSV i ustaw datę jako indeks
        self.df = pd.read_csv("weather_2024.csv", parse_dates=["date"]).set_index("date")
        self.preprocess()  # Wykonaj analizy
        self.initUI()      # Zbuduj interfejs graficzny

    def preprocess(self):
        # Dodanie średniej kroczącej 7-dniowej
        self.df["temp_roll"] = self.df["temperature"].rolling(window=7).mean()

        # Wykrywanie anomalii (odchylenie >2σ w obrębie miesiąca)
        self.df["month"] = self.df.index.month
        monthly_mean = self.df.groupby("month")["temperature"].transform("mean")
        monthly_std = self.df.groupby("month")["temperature"].transform("std")
        self.df["anomaly"] = ((self.df["temperature"] - monthly_mean).abs() > 2 * monthly_std)

        # Sumowanie miesięcznych opadów
        self.monthly_precip = self.df["precipitation"].resample("ME").sum()

        # Obliczenie korelacji
        self.corr_temp_hum = self.df["temperature"].corr(self.df["humidity"])
        self.corr_temp_prec = self.df["temperature"].corr(self.df["precipitation"])

        # Interpolacja brakujących danych (co 3 pomiar usunięty + interpolacja)
        df_missing = self.df.copy()
        df_missing.iloc[::3, df_missing.columns.get_loc("temperature")] = np.nan
        self.df["temp_interp"] = df_missing["temperature"].interpolate()

    def initUI(self):
        central = QWidget()
        layout = QVBoxLayout()
        splitter = QSplitter(Qt.Vertical)

        # Tabela z danymi
        table = QTableView()
        model = PandasModel(self.df.reset_index())
        table.setModel(model)
        splitter.addWidget(table)

        # Wykres temperatury + średnia krocząca + anomalia
        plot1 = pg.PlotWidget(title="Temperature & 7-Day Rolling Avg")
        x = np.arange(len(self.df))
        plot1.plot(x, self.df["temperature"].values, pen=pg.mkPen('b'), name="Temp")
        plot1.plot(x, self.df["temp_roll"].values, pen=pg.mkPen('r'), name="Rolling Avg")
        anom_idx = x[self.df["anomaly"].values]
        anom_vals = self.df.loc[self.df["anomaly"], "temperature"].values
        scatter = pg.ScatterPlotItem(x=anom_idx, y=anom_vals, size=8, brush=pg.mkBrush('k'))
        plot1.addItem(scatter)
        splitter.addWidget(plot1)

        # Wykres słupkowy miesięcznych opadów
        plot2 = pg.PlotWidget(title="Monthly Precipitation")
        months = np.arange(len(self.monthly_precip))
        bars = pg.BarGraphItem(x=months, height=self.monthly_precip.values, width=0.6)
        plot2.addItem(bars)
        ticks = [(i, m.strftime("%b")) for i, m in enumerate(self.monthly_precip.index)]
        plot2.getAxis('bottom').setTicks([ticks])
        splitter.addWidget(plot2)

        # Etykieta z wynikami korelacji
        corr_label = QLabel(f"Corr Temp vs Humidity: {self.corr_temp_hum:.2f}    Temp vs Precipitation: {self.corr_temp_prec:.2f}")
        corr_label.setAlignment(Qt.AlignCenter)

        # Ułożenie elementów w oknie
        layout.addWidget(splitter)
        layout.addWidget(corr_label)
        central.setLayout(layout)
        self.setCentralWidget(central)

# Uruchomienie aplikacji
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


