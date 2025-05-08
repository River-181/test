import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QLabel
from PyQt5.QtCore import Qt
import pandas as pd

class HolidayManager(QDialog):
    def __init__(self, parent=None):
        super(HolidayManager, self).__init__(parent)
        self.setWindowTitle("휴일 관리")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.holiday_table = QTableWidget()
        self.holiday_table.setColumnCount(2)
        self.holiday_table.setHorizontalHeaderLabels(['날짜', '휴일 이름'])
        self.holiday_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.holiday_table.verticalHeader().setVisible(False)

        layout.addWidget(QLabel(f"{pd.Timestamp.now().year}년 휴일 목록"))
        layout.addWidget(self.holiday_table)

        button_layout = QHBoxLayout()
        self.load_button = QPushButton("공휴일 불러오기")
        self.add_button = QPushButton("휴일 추가")
        self.remove_button = QPushButton("휴일 삭제")
        self.apply_button = QPushButton("적용하기")
        self.save_button = QPushButton("저장하고 나가기")

        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.holiday_statistics = QLabel()
        layout.addWidget(self.holiday_statistics)

        self.setLayout(layout)

        self.load_button.clicked.connect(self.load_holidays)
        self.add_button.clicked.connect(self.add_holiday)
        self.remove_button.clicked.connect(self.remove_holiday)
        self.apply_button.clicked.connect(self.apply_changes)
        self.save_button.clicked.connect(self.save_and_exit)

        self.holidays_df = pd.DataFrame(columns=['Date', 'Holiday Name'])
        self.load_holidays()

    def load_holidays(self):
        try:
            self.holidays_df = pd.read_csv('holidays.csv', parse_dates=['Date'])
        except FileNotFoundError:
            self.holidays_df = pd.DataFrame(columns=['Date', 'Holiday Name'])
        self.update_holiday_table()

    def update_holiday_table(self):
        self.holiday_table.setRowCount(len(self.holidays_df))
        for i, row in self.holidays_df.iterrows():
            self.holiday_table.setItem(i, 0, QTableWidgetItem(row['Date'].strftime('%Y/%m/%d')))
            self.holiday_table.setItem(i, 1, QTableWidgetItem(row['Holiday Name']))
        self.update_holiday_statistics()

    def add_holiday(self):
        self.holidays_df = self.holidays_df.append({'Date': pd.Timestamp.now(), 'Holiday Name': '신규 휴일'}, ignore_index=True)
        self.update_holiday_table()

    def remove_holiday(self):
        current_row = self.holiday_table.currentRow()
        if current_row >= 0:
            self.holidays_df = self.holidays_df.drop(self.holidays_df.index[current_row])
            self.update_holiday_table()

    def apply_changes(self):
        for row in range(self.holiday_table.rowCount()):
            date_item = self.holiday_table.item(row, 0)
            name_item = self.holiday_table.item(row, 1)
            if date_item and name_item:
                self.holidays_df.at[row, 'Date'] = pd.to_datetime(date_item.text(), format='%Y/%m/%d')
                self.holidays_df.at[row, 'Holiday Name'] = name_item.text()
        self.update_holiday_statistics()

    def save_and_exit(self):
        self.apply_changes()
        self.holidays_df.to_csv('holidays.csv', index=False)
        self.close()

    def update_holiday_statistics(self):
        year = pd.Timestamp.now().year
        kr_holidays = pd.read_csv('holidays.csv', parse_dates=['Date'])
        total_holidays = len(kr_holidays)
        total_weekends = sum(1 for d in kr_holidays['Date'] if d.weekday() >= 5)
        self.holiday_statistics.setText(f"{year}년의 공휴일: {total_holidays}일, 주말: {total_weekends}일")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HolidayManager()
    window.show()
    sys.exit(app.exec_())