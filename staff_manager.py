import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QLabel, QLineEdit, QComboBox, QCheckBox, QFileDialog
from PyQt5.QtCore import Qt
import pandas as pd

class StaffManager(QDialog):
    def __init__(self, parent=None):
        super(StaffManager, self).__init__(parent)
        self.setWindowTitle("직원 관리")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.staff_table = QTableWidget()
        self.staff_table.setColumnCount(5)
        self.staff_table.setHorizontalHeaderLabels(['번호', '이름', '성별', '당직 여부', '마지막 당직일'])
        self.staff_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.staff_table.verticalHeader().setVisible(False)

        layout.addWidget(QLabel("직원 목록"))
        layout.addWidget(self.staff_table)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("직원 추가")
        self.remove_button = QPushButton("직원 삭제")
        self.apply_button = QPushButton("적용하기")
        self.save_button = QPushButton("저장하고 나가기")
        self.load_button = QPushButton("파일 불러오기")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)

        layout.addLayout(button_layout)

        self.staff_statistics = QLabel()
        layout.addWidget(self.staff_statistics)

        self.setLayout(layout)

        self.add_button.clicked.connect(self.add_staff)
        self.remove_button.clicked.connect(self.remove_staff)
        self.apply_button.clicked.connect(self.apply_changes)
        self.save_button.clicked.connect(self.save_and_exit)
        self.load_button.clicked.connect(self.load_staff_data)

        self.staff_df = pd.DataFrame(columns=['Name', 'Gender', 'On Duty', 'Last Duty Day'])
        self.load_staff_data()

    def load_staff_data(self):
        try:
            self.staff_df = pd.read_csv('staff.csv', parse_dates=['Last Duty Day'])
        except FileNotFoundError:
            self.staff_df = pd.DataFrame(columns=['Name', 'Gender', 'On Duty', 'Last Duty Day'])
        self.update_staff_table()

    def update_staff_table(self):
        self.staff_table.setRowCount(len(self.staff_df))
        for i, row in self.staff_df.iterrows():
            self.staff_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.staff_table.setItem(i, 1, QTableWidgetItem(row['Name']))
            gender_combo = QComboBox()
            gender_combo.addItems(['남자', '여자', '그 외'])
            gender_combo.setCurrentText(row['Gender'])
            self.staff_table.setCellWidget(i, 2, gender_combo)
            on_duty_checkbox = QCheckBox()
            on_duty_checkbox.setChecked(row['On Duty'])
            self.staff_table.setCellWidget(i, 3, on_duty_checkbox)
            last_duty_day = row['Last Duty Day'].strftime('%Y/%m/%d') if pd.notnull(row['Last Duty Day']) else ''
            self.staff_table.setItem(i, 4, QTableWidgetItem(last_duty_day))
        self.update_staff_statistics()

    def add_staff(self):
        self.staff_df = self.staff_df.append({'Name': '신규 직원', 'Gender': '남자', 'On Duty': False, 'Last Duty Day': pd.NaT}, ignore_index=True)
        self.update_staff_table()

    def remove_staff(self):
        current_row = self.staff_table.currentRow()
        if current_row >= 0:
            self.staff_df = self.staff_df.drop(self.staff_df.index[current_row])
            self.update_staff_table()

    def apply_changes(self):
        for row in range(self.staff_table.rowCount()):
            name_item = self.staff_table.item(row, 1)
            gender_combo = self.staff_table.cellWidget(row, 2)
            on_duty_checkbox = self.staff_table.cellWidget(row, 3)
            last_duty_day_item = self.staff_table.item(row, 4)
            if name_item and gender_combo and on_duty_checkbox and last_duty_day_item:
                self.staff_df.at[row, 'Name'] = name_item.text()
                self.staff_df.at[row, 'Gender'] = gender_combo.currentText()
                self.staff_df.at[row, 'On Duty'] = on_duty_checkbox.isChecked()
                self.staff_df.at[row, 'Last Duty Day'] = pd.to_datetime(last_duty_day_item.text(), format='%Y/%m/%d', errors='coerce')
        self.update_staff_statistics()

    def save_and_exit(self):
        self.apply_changes()
        self.staff_df.to_csv('staff.csv', index=False)
        self.close()

    def update_staff_statistics(self):
        total_staff = len(self.staff_df)
        on_duty_staff = len(self.staff_df[self.staff_df['On Duty']])
        on_duty_staff_names = ', '.join(self.staff_df[self.staff_df['On Duty']]['Name'])
        self.staff_statistics.setText(f"총 직원 수: {total_staff}, 당직 직원 수: {on_duty_staff}, 당직 직원 목록: {on_duty_staff_names}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StaffManager()
    window.show()
    sys.exit(app.exec_())