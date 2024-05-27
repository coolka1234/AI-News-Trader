from PyQt6.QtWidgets import QMainWindow, QGridLayout, QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pandas import Period
from StockBriefing import Ui_MainMenuWindow
from StockAction import StockAction
class StockBriefingWindow(QMainWindow, Ui_MainMenuWindow):
    def __init__(self, mainWindow=None):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.fillComboBoxes()
        self.pushButtonExecute.clicked.connect(self.display_stock_data)
        self.mainwindow = mainWindow
        self.mainwindow.pushButtonStockBriefing.setEnabled(False)
        self.pushButtonClear.clicked.connect(self.clear)
    def display_stock_data(self):
        symbol = self.lineEditSymbolnput.text()
        period = self.comboBox.currentText()
        interval=self.comboBox_2.currentText()
        if self.wrong_interval(period, interval):
            self.labelSypckGraph.setText('Error: Invalid interval for selected period')
            return
        if symbol == '':
            return
        if (period == ' '):
            period = '1mo'
        # stock = StockAction(symbol)
        try:
            StockAction.graph_stock_data(symbol, period, interval=interval)
        except Exception as e:
            self.labelSypckGraph.setText(f'Error: There was trouble fetching data. Please try again later or with diffrent symbol')
        pixmap=QPixmap('plots/stock_data.png')
        self.labelSypckGraph.setPixmap(pixmap)
    
    def fillComboBoxes(self):
        periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        self.comboBox.addItems(periods)
        intervals = ['1m', '2m', '5m', '15m', '30m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        self.comboBox_2.addItems(intervals)
    
    def closeEvent(self, event):
        if self.mainwindow is not None:
            self.mainwindow.w2 = None
            self.mainwindow.pushButtonStockBriefing.setEnabled(True)
    
    def clear(self):
        self.lineEditSymbolnput.clear()
        self.comboBox.setCurrentIndex(0)
        self.comboBox_2.setCurrentIndex(0)
        self.labelSypckGraph.clear()
    
    def wrong_interval(self, period, interval):
        if period == '1d' and interval not in ['1m', '2m', '5m', '15m', '30m', '1h']:
            return True
        if period == '5d' and interval not in ['1m', '2m', '5m', '15m', '30m', '1h', '1d']:
            return True
        if period == '1mo' and interval not in ['2m', '5m', '15m', '30m', '1h', '1d', '5d']:
            return True
        if period == '3mo' and interval not in ['1h', '1d', '5d', '1wk']:
            return True
        if period == '6mo' and interval not in ['1d', '5d', '1wk', '1mo']:
            return True
        if period == '1y' and interval not in ['1d', '5d', '1wk', '1mo']:
            return True
        if period == '2y' and interval not in ['1d', '5d', '1wk', '1mo']:
            return True
        if period == '5y' and interval not in ['1d', '5d', '1wk', '1mo', '3mo', '6mo', '1y']:
            return True
        if period == '10y' and interval not in ['1wk', '1mo', '3mo', '6mo', '1y']:
            return True
        if period == 'ytd' and interval not in ['1wk', '1mo', '3mo', '6mo', '1y']:
            return True
        if period == 'max' and interval not in ['1wk', '1mo', '3mo', '6mo', '1y']:
            return True
        return False

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StockBriefingWindow()
    window.show()
    sys.exit(app.exec())