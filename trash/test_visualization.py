from src.scheduler import schedule_all
from src.visualizer import generate_html, generate_excel, console_display
import pandas as pd

# Sample Data
courses = pd.DataFrame({
    'SubjectCode': ['AE29202', 'AE21202', 'AE31004', 'AE40023'],
    'SubjectName': ['Aero Lab', 'Low Speed Aero', 'Aircraft Stability', 'Avionics'],
    'Type': ['Lab', 'Core', 'Core', 'Elective'],
    'Batches': ['2nd', '2nd', '3rd', '2nd,3rd'],
    'Faculty': ['MK,SMD', 'SG', 'MS', 'SB'],
    'Duration': [3, 4, 4, 3],
    'LabRoom': ['AeroLab', None, None, None]
})

faculty = pd.DataFrame({
    'Name': ['SG', 'MS', 'MK,SMD', 'SB'],
    'UnavailableSlots': ['F41', None, 'L', None]
})

# Generate Schedule
schedule, _ = schedule_all(
    courses_df=courses,
    faculty_df=faculty,
    slot_master_path='data/slot_master.xlsx'
)

# Visualize
console_display(schedule)
generate_html(schedule)
generate_excel(schedule)