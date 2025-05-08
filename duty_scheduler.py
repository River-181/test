import sys
import datetime
import calendar
import pandas as pd
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTreeView, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QAbstractItemView, QFrame
from PyQt5.QtCore import Qt, QAbstractTableModel, QDate
import plotly.figure_factory as ff
import math

class DutyTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data.columns)

    def data(self, index, role):
        if role == Qt.DisplayRole or role == Qt.EditRole:
            value = self._data.iloc[index.row(), index.column()]
            if isinstance(value, pd.Timestamp):
                return value.strftime("%Y-%m-%d (%a)")
            return str(value)
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._data.columns[section]
            if orientation == Qt.Vertical:
                return str(self._data.index[section])
        return None

class DutyScheduler(QDialog):
    def __init__(self, parent=None):
        super(DutyScheduler, self).__init__(parent)
        self.setWindowTitle("당직 일정 생성")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()
        content_layout = QVBoxLayout()

        self.create_date_selection(content_layout)
        self.create_duty_management_frame(content_layout)
        self.create_statistics_frame(content_layout)
        main_layout.addLayout(content_layout)
        self.create_vacation_frame(main_layout)

        self.setLayout(main_layout)

    def create_date_selection(self, layout):
        date_selection_frame = QFrame()
        date_selection_frame.setFrameShape(QFrame.StyledPanel)
        date_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())

        date_layout.addWidget(QLabel("시작 날짜:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("종료 날짜:"))
        date_layout.addWidget(self.end_date_edit)

        date_selection_frame.setLayout(date_layout)
        layout.addWidget(date_selection_frame)

    def create_duty_management_frame(self, layout):
        self.duty_df = self.load_duties()
        self.model = DutyTableModel(self.duty_df)

        self.duty_tree = QTreeView()
        self.duty_tree.setModel(self.model)
        self.duty_tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.duty_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.duty_tree.setSortingEnabled(True)
        self.duty_tree.header().setStretchLastSection(True)
        self.duty_tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        layout.addWidget(QLabel("당직 일정 목록"))
        layout.addWidget(self.duty_tree)

        button_layout = QHBoxLayout()
        generate_button = QPushButton("이번 달 당번 일정 생성하기")
        gantt_button = QPushButton("간트 차트 생성하기")
        export_button = QPushButton("생성한 일정 내보내기")
        apply_button = QPushButton("적용하기")
        save_button = QPushButton("저장하고 나가기")

        button_layout.addWidget(generate_button)
        button_layout.addWidget(gantt_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(apply_button)
        button_layout.addWidget(save_button)

        layout.addLayout(button_layout)

        generate_button.clicked.connect(self.generate_duty_schedule)
        gantt_button.clicked.connect(self.create_gantt_chart)
        export_button.clicked.connect(self.export_duties)
        apply_button.clicked.connect(self.apply_changes)
        save_button.clicked.connect(self.save_and_exit)

    def create_statistics_frame(self, layout):
        statistics_frame = QFrame()
        statistics_frame.setFrameShape(QFrame.StyledPanel)
        stat_layout = QVBoxLayout()

        self.total_workdays_label = QLabel("YYYY년 MM월의 당번 가능한 평일 수: ")
        stat_layout.addWidget(self.total_workdays_label)

        self.duty_counts_df = pd.DataFrame(columns=['Name', 'Duty Count'])
        self.duty_counts_model = DutyTableModel(self.duty_counts_df)
        self.duty_counts_view = QTableWidget()
        self.duty_counts_view.setModel(self.duty_counts_model)
        self.duty_counts_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        stat_layout.addWidget(QLabel("직원 당번 횟수"))
        stat_layout.addWidget(self.duty_counts_view)

        statistics_frame.setLayout(stat_layout)
        layout.addWidget(statistics_frame)

    def create_vacation_frame(self, layout):
        vacation_frame = QFrame()
        vacation_frame.setFrameShape(QFrame.StyledPanel)
        vac_layout = QVBoxLayout()

        self.vacation_df = self.load_vacations()
        self.vacation_model = DutyTableModel(self.vacation_df)
        self.vacation_view = QTableWidget()
        self.vacation_view.setModel(self.vacation_model)
        self.vacation_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.vacation_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.vacation_view.setSortingEnabled(True)

        vac_layout.addWidget(QLabel("이번 달 직원 휴가 일정"))
        vac_layout.addWidget(self.vacation_view)

        vacation_frame.setLayout(vac_layout)
        layout.addWidget(vacation_frame)

    def load_duties(self):
        try:
            df = pd.read_csv('duties.csv', parse_dates=['Date'])
            if 'Employee 1' not in df.columns or 'Employee 2' not in df.columns:
                df['Employee 1'] = ""
                df['Employee 2'] = ""
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=['Date', 'Employee 1', 'Employee 2'])

    def load_vacations(self):
        try:
            df = pd.read_csv('vacations.csv', parse_dates=['Start Date', 'End Date'])
            return df
        except FileNotFoundError:
            return pd.DataFrame(columns=['Name', 'Start Date', 'End Date'])

    def generate_duty_schedule(self):
        year = self.start_date_edit.date().year()
        month = self.start_date_edit.date().month()
        workdays = self.get_workdays(year, month)
        duty_schedule = []
        today = datetime.datetime(year, month, 1)

        # Load staff data
        try:
            self.staff_df = pd.read_csv('staff.csv', parse_dates=['Last Duty Day'])
            self.staff_df['Last Duty Day'] = pd.to_datetime(self.staff_df['Last Duty Day']).fillna(pd.Timestamp('1900-01-01'))
            if 'Duty Count' not in self.staff_df.columns:
                self.staff_df['Duty Count'] = 0
        except FileNotFoundError:
            self.staff_df = pd.DataFrame(columns=['Name', 'On Duty', 'Duty Count', 'Last Duty Day'])
            self.staff_df['Duty Count'] = 0

        # Load vacation data
        try:
            vacation_df = pd.read_csv('vacations.csv', parse_dates=['Start Date', 'End Date'])
        except FileNotFoundError:
            vacation_df = pd.DataFrame(columns=['Name', 'Start Date', 'End Date'])

        for day in workdays:
            today = today.replace(day=day)
            available_staff = self.staff_df[(self.staff_df['On Duty']) & ((today - self.staff_df['Last Duty Day']) > datetime.timedelta(days=3))]
            if len(available_staff) < 2:
                available_staff = self.staff_df[self.staff_df['On Duty']]

            # Remove staff who are on vacation
            vacation_today = vacation_df[(vacation_df['Start Date'] <= today) & (vacation_df['End Date'] >= today)]
            available_staff = available_staff[~available_staff['Name'].isin(vacation_today['Name'])]

            selected_staff = available_staff.sample(n=2, replace=False)
            duty_schedule.append({'Date': today.strftime("%Y-%m-%d (%a)"), 'Employee 1': selected_staff.iloc[0]['Name'], 'Employee 2': selected_staff.iloc[1]['Name']})

            # Update duty count and last duty day
            self.staff_df.loc[selected_staff.index, 'Duty Count'] += 1
            self.staff_df.loc[selected_staff.index, 'Last Duty Day'] = today

        self.duty_df = pd.DataFrame(duty_schedule)
        self.model._data = self.duty_df
        self.model.layoutChanged.emit()
        self.update_duty_counts()

    def get_workdays(self, year, month):
        num_days = calendar.monthrange(year, month)[1]
        weekdays = [
            day for day in range(1, num_days + 1)
            if calendar.weekday(year, month, day) < 5  # 주말 제외
            and datetime.date(year, month, day) not in self.holidays_df['Date'].dt.date.tolist()  # 공휴일 제외
        ]
        self.total_workdays_label.setText(f"{year}년 {month}월의 당번 가능한 평일 수: {len(weekdays)}")
        return weekdays

    def update_duty_counts(self):
        duty_counts = self.duty_df['Employee 1'].append(self.duty_df['Employee 2']).value_counts().reset_index()
        duty_counts.columns = ['Name', 'Duty Count']
        self.duty_counts_df = duty_counts
        self.duty_counts_model._data = self.duty_counts_df
        self.duty_counts_model.layoutChanged.emit()

    def apply_changes(self):
        self.model.layoutChanged.emit()
        self.update_duty_counts()

    def save_and_exit(self):
        self.apply_changes()
        self.duty_df.to_csv('duties.csv', index=False)
        self.close()

    def create_gantt_chart(self):
        year = self.start_date_edit.date().year()
        month = self.start_date_edit.date().month()
        df = []
        for _, row in self.duty_df.iterrows():
            duty_date = datetime.datetime.strptime(row['Date'], "%Y-%m-%d (%a)")
            df.append(dict(Task=row['Employee 1'], Start=duty_date, Finish=duty_date + datetime.timedelta(days=1), Resource='Duty'))
            df.append(dict(Task=row['Employee 2'], Start=duty_date, Finish=duty_date + datetime.timedelta(days=1), Resource='Duty'))

        # Calculate the number of weeks in the month
        num_weeks = math.ceil(calendar.monthrange(year, month)[1] / 7.0)
        week_dates = [(datetime.datetime(year, month, 1) + datetime.timedelta(days=7 * i)).strftime("%Y-%m-%d") for i in range(num_weeks)]

        fig = ff.create_gantt(df, index_col='Resource', show_colorbar=False, group_tasks=True, title=f'{year}년 {month}월의 당직 일정표')

        # Define weekend and weekday for grid color reference
        weekend_color = 'rgb(255,000,051)'
        weekday_color = 'rgb(230,230,230)'

        # Add background color for weekends and vertical lines for each day
        days_in_month = calendar.monthrange(year, month)[1]
        start_date = datetime.datetime(year, month, 1)
        end_date = datetime.datetime(year, month, days_in_month)
        shapes = []
        for single_date in (start_date + datetime.timedelta(n) for n in range(days_in_month)):
            if single_date.weekday() == 5:  # 토요일
                fillcolor = 'blue'
            elif single_date.weekday() == 6:  # 일요일
                fillcolor = 'red'
            else:
                fillcolor = weekday_color

            shape = {
                'type': 'rect',
                'x0': single_date,
                'x1': single_date + datetime.timedelta(days=1),
                'y0': 0,
                'y1': 1,
                'xref': 'x',
                'yref': 'paper',
                'fillcolor': fillcolor,
                'opacity': 0.3,
                'line': {
                    'width': 0,
                }
            }
            shapes.append(shape)

        fig.update_layout(
            shapes=shapes,
            xaxis={
                'tickvals': [date.strftime('%Y-%m-%d') for date in pd.date_range(start=start_date, end=end_date)],
                'ticktext': [date.strftime('%-d(%a)') for date in pd.date_range(start=start_date, end=end_date)],
                'tickangle': 45,
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'gray'
            },
            yaxis={
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': 'gray'
            },
            height=50 * len(self.staff_df) # Adjust height to number of staff
        )

        # Add annotations for week numbers
        annotations = []
        for i, week_date in enumerate(week_dates):
            annotations.append({
                'x': week_date,
                'y': 1.05,
                'xref': 'x',
                'yref': 'paper',
                'text': f'{i+1}주',
                'showarrow': False,
                'font': {'color': 'black', 'size': 12},
                'bgcolor': 'white'
            })

        fig.update_layout(annotations=annotations)

        fig.show()

    def export_duties(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getSaveFileName(self, "Save Duty Schedule", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file:
            self.duty_df.to_csv(file, index=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DutyScheduler()
    window.show()
    sys.exit(app.exec_())