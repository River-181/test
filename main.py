import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, QHBoxLayout, QGridLayout, QCalendarWidget
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QTextCharFormat
import datetime
from holiday_manager import HolidayManager
from duty_scheduler import DutyScheduler
import pandas as pd

# Qt platform plugin 설정
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = "/Users/river-181/Documents/RandomProgram/202406/project_directory/.venv/lib/python3.11/site-packages/PyQt5/Qt/plugins"

class CustomCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.update_calendar_format()
        self.set_custom_style()

    def update_calendar_format(self):
        # Set format for weekends
        format_saturday = QTextCharFormat()
        format_saturday.setForeground(Qt.blue)
        
        format_sunday = QTextCharFormat()
        format_sunday.setForeground(Qt.red)
        
        current_date = QDate.currentDate()
        first_day_of_month = QDate(current_date.year(), current_date.month(), 1)
        days_in_month = first_day_of_month.daysInMonth()
        
        for day in range(1, days_in_month + 1):
            date = QDate(current_date.year(), current_date.month(), day)
            if date.dayOfWeek() == Qt.Saturday:
                self.setDateTextFormat(date, format_saturday)
            elif date.dayOfWeek() == Qt.Sunday:
                self.setDateTextFormat(date, format_sunday)

    def set_custom_style(self):
        self.setStyleSheet("""
            QCalendarWidget QWidget {
                background-color: #f0f0f0;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #404040;
                background-color: #e0e0e0;
                selection-background-color: #ababab;
                selection-color: white;
            }
            QCalendarWidget QToolButton {
                height: 40px;
                width: 100px;
                color: white;
                background-color: #404040;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #606060;
            }
            QCalendarWidget QToolButton::menu-arrow {
                image: none;
            }
            QCalendarWidget QToolButton::menu-arrow:hover {
                image: none;
            }
            QCalendarWidget QSpinBox {
                margin: 5px;
            }
            QCalendarWidget QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
            }
            QCalendarWidget QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px.
            }
            QCalendarWidget QSpinBox::up-arrow {
                width: 16px;
                height: 16px;
            }
            QCalendarWidget QSpinBox::down-arrow {
                width: 16px;
                height: 16px.
            }
        """)

    def show_previous_month(self):
        current_date = self.selectedDate()
        new_date = current_date.addMonths(-1)
        self.setSelectedDate(new_date)
        self.update_calendar_format()

    def show_next_month(self):
        current_date = self.selectedDate()
        new_date = current_date.addMonths(1)
        self.setSelectedDate(new_date)
        self.update_calendar_format()

    def show_today(self):
        self.setSelectedDate(QDate.currentDate())
        self.update_calendar_format()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QGridLayout()

        # Create frames
        self.create_navigation_frame(main_layout)
        self.create_date_frame(main_layout)
        self.create_calendar_frame(main_layout)
        self.create_statistics_frame(main_layout)
        self.create_duty_employee_status_frame(main_layout)

        self.central_widget.setLayout(main_layout)

        # Initialize managers
        self.holiday_manager = HolidayManager(self)
        self.duty_scheduler = DutyScheduler(self)

    def create_navigation_frame(self, layout):
        navigation_frame = QFrame()
        navigation_frame.setFrameShape(QFrame.StyledPanel)
        nav_layout = QVBoxLayout()

        home_button = QPushButton("홈")
        home_button.clicked.connect(self.show_main_page)

        staff_manager_button = QPushButton("직원 관리")
        staff_manager_button.clicked.connect(self.show_staff_manager)

        holiday_manager_button = QPushButton("휴일 관리")
        holiday_manager_button.clicked.connect(self.show_holiday_manager)

        duty_scheduler_button = QPushButton("당직 일정 생성")
        duty_scheduler_button.clicked.connect(self.show_duty_scheduler)

        nav_layout.addWidget(home_button)
        nav_layout.addWidget(staff_manager_button)
        nav_layout.addWidget(holiday_manager_button)
        nav_layout.addWidget(duty_scheduler_button)
        nav_layout.addStretch(1)

        reset_button = QPushButton("초기화")
        exit_button = QPushButton("종료하기")

        nav_layout.addWidget(reset_button)
        nav_layout.addWidget(exit_button)

        navigation_frame.setLayout(nav_layout)
        layout.addWidget(navigation_frame, 0, 0, 3, 1)

    def create_date_frame(self, layout):
        date_frame = QFrame()
        date_frame.setFrameShape(QFrame.StyledPanel)
        date_layout = QVBoxLayout()

        current_date = datetime.datetime.now().strftime("%Y년 %m월 %d일 (%a)")
        date_label = QLabel(f"현재 날짜: {current_date}")
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        date_layout.addWidget(date_label)

        date_frame.setLayout(date_layout)
        layout.addWidget(date_frame, 0, 1, 1, 2)

    def create_calendar_frame(self, layout):
        calendar_frame = QFrame()
        calendar_frame.setFrameShape(QFrame.StyledPanel)
        cal_layout = QVBoxLayout()

        self.calendar = CustomCalendarWidget()

        nav_layout = QHBoxLayout()
        prev_button = QPushButton("<")
        next_button = QPushButton(">")
        today_button = QPushButton("오늘")

        prev_button.clicked.connect(self.calendar.show_previous_month)
        next_button.clicked.connect(self.calendar.show_next_month)
        today_button.clicked.connect(self.calendar.show_today)

        nav_layout.addWidget(prev_button)
        nav_layout.addWidget(today_button)
        nav_layout.addWidget(next_button)

        cal_layout.addLayout(nav_layout)
        cal_layout.addWidget(self.calendar)

        calendar_frame.setLayout(cal_layout)
        layout.addWidget(calendar_frame, 1, 1, 1, 2)

    def create_statistics_frame(self, layout):
        statistics_frame = QFrame()
        statistics_frame.setFrameShape(QFrame.StyledPanel)
        stat_layout = QVBoxLayout()

        stat_layout.addWidget(QLabel("당직 실시간"))
        stat_layout.addWidget(QLabel("공휴일 실시간"))
        stat_layout.addWidget(QLabel("총 휴일 실시간"))

        statistics_frame.setLayout(stat_layout)
        layout.addWidget(statistics_frame, 2, 1)

    def create_duty_employee_status_frame(self, layout):
        employee_frame = QFrame()
        employee_frame.setFrameShape(QFrame.StyledPanel)
        emp_layout = QVBoxLayout()

        emp_layout.addWidget(QLabel("당직 직원 현황"))

        # Load the staff data
        try:
            staff_df = pd.read_csv('staff.csv', parse_dates=['Last Duty Day'])
            on_duty_staff = staff_df[staff_df['On Duty'] == True]['Name'].tolist()
            on_duty_staff_str = "\n".join(on_duty_staff)
        except FileNotFoundError:
            on_duty_staff_str = "No data available"

        self.duty_staff_label = QLabel(on_duty_staff_str)
        emp_layout.addWidget(self.duty_staff_label)

        employee_frame.setLayout(emp_layout)
        layout.addWidget(employee_frame, 2, 2)

    def show_main_page(self):
        self.central_widget.show()

    def show_holiday_manager(self):
        self.holiday_manager.show()

    def show_staff_manager(self):
        from staff_manager import StaffManager
        staff_manager = StaffManager(self)
        staff_manager.exec_()

    def show_duty_scheduler(self):
        self.duty_scheduler.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())