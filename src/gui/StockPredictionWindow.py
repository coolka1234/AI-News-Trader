import csv
from PyQt6.QtWidgets import QMainWindow, QApplication
from src.gui.StockPrediction import Ui_MainMenuWindow
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import logging
from src.utility_functions import resource_path_gp
from src.utility_functions import get_company_name
from tensorflow.keras.models import Sequential, load_model # type: ignore (this has to be here, its a known keras bug)
from random import randint
from datetime import  datetime
from src.database.NewsFeature import NewsFeature
from src.StockAction import StockAction
from src.loadin_test import load_predict
from src.database.database_create import create_temp_news_database, create_temp_stock_database, delete_temp_news_database, delete_temp_stock_database
from src.database.fetch_and_store import fetch_and_store_articles_to_temporary_db
from src.database.non_api_fetch_and_store_stocks import fetch_and_store_stock_data_to_temporary_db
import nltk
nltk.download('punkt')
import sys

def np_news():
    news_array=np.array([])
    conn = sqlite3.connect('src/database/temporary_news.db')
    cursor = conn.cursor()
    table_name = 'articles'
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    row_count = result[0]
    for i in range(1, row_count+1):
        curr_news= NewsFeature(i, Temp=True)
        news_array=np.append(news_array,curr_news)
    conn.close()
    return news_array

def np_stock():
    stock_array=np.array([])
    conn = sqlite3.connect('src/database/temporary_stocks.db')
    cursor = conn.cursor()
    table_name = 'stock_prices'
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchone()
    row_count = result[0]
    for i in range(1, row_count+1):
        curr_stock= StockAction(i, temp=True)
        stock_array=np.append(stock_array,curr_stock)
        break
    conn.close()
    return stock_array

def append_if_not_exists(file_path, data):
    with open(file_path, 'r', newline='') as file:
        reader = csv.reader(file)
        if data in reader:
            return 
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)
    
def generate_raport(stock, prediction, name):
    raport=f'<html>Predicted stock price for {name} is {prediction}$ <br> \n'
    raport+= f'Current stock price is {stock}$ <br> \n'
    if prediction>stock:
        raport+='Recommendation: <font color="green">Buy!</font></html>'
    else:
        raport+='Recommendation: <font color="red">Sell!</font></html>'
    return raport

class StockPredictionWindow(QMainWindow, Ui_MainMenuWindow):
    def __init__(self, main_menu_window):
        logging.basicConfig(level=logging.INFO, filename='docs/logs.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
        super().__init__()
        self.setupUi(self)
        self.show()
        self.model=load_model(resource_path_gp('src/models/stock_prediction_model.h5'))
        self.pushButtonExecute.clicked.connect(self.display_prediction)
        self.main_window = main_menu_window
        self.main_window.pushButtonStockPrediction.setDisabled(True)
        
    
    def display_prediction(self):
        logging.info('Stock prediction started')
        self.progressBar.setValue(0)
        if self.lineEditSymbolnput.text() == '':
            self.labelRaport.setText('Error: Please provide a symbol')
            return
        create_temp_news_database()
        create_temp_stock_database()
        try:
            name=get_company_name(self.lineEditSymbolnput.text())
        except:
            self.labelRaport.setText('Error: Please provide a valid symbol')
            return
        symbol = self.lineEditSymbolnput.text()
        try:
            append_if_not_exists(resource_path_gp('res/companies_of_interest.csv'), name)
        except Exception as e:
            logging.error(f'Error: {e}')
            self.labelRaport.setText('Error: There was trouble fetching data. Please try again later or with diffrent symbol')
            delete_temp_news_database()
            delete_temp_stock_database()
            return
        date_today=datetime.now()
        date_yesterday=date_today-timedelta(days=1)
        date_today=str(date_today.date())
        date_yesterday=str(date_yesterday.date())
        # date_yesterday=date_to_ISO_8601(str(date_yesterday.date()))
        # date_today=date_to_ISO_8601(str(date_today.date()))
        self.progressBar.setValue(10+randint(1, 6))
        try:
            fetch_and_store_articles_to_temporary_db(keyword=symbol, from_date=date_yesterday, to_date=date_today, language='en', sort_by='publishedAt')
            fetch_and_store_stock_data_to_temporary_db(symbol, symbol, period='1d')
        except Exception as e:
            logging.error(f'Error: {e}')
            self.labelRaport.setText(f'Error: There was trouble fetching data. Please try again later or with diffrent symbol')
            delete_temp_news_database()
            delete_temp_stock_database()
            return
        news=np_news()
        stock=np_stock()

        delete_temp_news_database()
        delete_temp_stock_database()
        all_articles=[entry.content for entry in news]
        string = ' '.join(all_articles)
        self.progressBar.setValue(30+randint(1, 6))
        numpy_string=np.array([string])
        try:
            result=load_predict(numpy_string, stock[0].opening_price)
        except Exception as e:
            logging.error('errror 141')
            logging.error(f'Error: {e}')
            logging.error(f'Stack trace: {e.with_traceback()}')
            self.labelRaport.setText(f'Error: There was trouble predicting the stock price. Please try again later or with diffrent symbol')
            return
        self.progressBar.setValue(100)
        self.labelRaport.setText(generate_raport(stock[0].opening_price, result[0][0], name))
        QApplication.processEvents()
        
    def closeEvent(self, event):
        if self.main_window is not None:
            self.main_window.pushButtonStockPrediction.setDisabled(False)
            self.main_window.w1 = None
        # event.accept()
    def clear(self):
        self.labelRaport.setText('')
        self.lineEditSymbolnput.setText('')
        self.progressBar.setValue(0)


if __name__ == '__main__':
    app=QApplication(sys.argv)
    window=StockPredictionWindow()
    window.show()
    sys.exit(app.exec())

