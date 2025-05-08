
# Staff Duty Scheduler

This project is a Python-based system designed to efficiently manage staff duty schedules for companies or organizations. It includes features for managing staff data, holidays, and automatic duty scheduling.

## 📁 Project Structure

```
├── main.py                # Entry point of the program
├── staff_manager.py       # Staff management (add, remove, view)
├── holiday_manager.py     # Holiday data management
├── duty_scheduler.py      # Automatic duty schedule generator
```

## ⚙️ Features

### 1. `staff_manager.py`
- Manages staff information.
- Features:
  - Add or remove staff
  - Save and load staff data
  - Store data in JSON format

### 2. `holiday_manager.py`
- Manages holiday data.
- Features:
  - Add or remove holidays
  - Save/load holiday list as JSON
  - Check if a date is a holiday

### 3. `duty_scheduler.py`
- Automatically creates and manages duty schedules.
- Features:
  - Fair rotation among staff
  - Skips or handles holidays specifically
  - Saves/loads schedules in JSON format

### 4. `main.py`
- Provides a CLI for users to:
  - View/add/remove staff
  - Manage holidays
  - Generate and check schedules automatically

## 💾 Example Usage

```bash
python main.py
```

Follow the menu to register staff, set holidays, and create schedules.

## 💡 Future Improvements

- Add a GUI-based interface
- Notification system via email or messenger
- Export weekly/monthly duty reports as PDF

## 🛠️ Requirements

- Python 3.8 or later
- Uses standard libraries (json, datetime, etc.)

## 📄 License

MIT License
