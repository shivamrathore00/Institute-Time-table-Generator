"""
Test timetable visualization
"""
from src.scheduler import schedule_courses
from src.visualizer import generate_html_timetable, generate_console_timetable, export_to_excel
import pandas as pd

# Sample Data
courses = pd.DataFrame({
    'SubjectCode': ['AE29202', 'AE21202', 'AE20202'],
    'SubjectName': ['Aero Lab', 'Low Speed Aero', 'Flight Controls'],
    'Type': ['Lab', 'Theory', 'Theory'],
    'Faculty': ['Prof. Dash', 'Prof. Ghosh', 'Prof. Hota'],
    'AllowedSlots': ['J,K', 'C31,C32', 'A31,A32'],
    'RoomPref': ['AeroLab', '', '']
})

faculty = pd.DataFrame({
    'Name': ['Prof. Dash', 'Prof. Ghosh', 'Prof. Hota'],
    'AvailableSlots': ['J,L', 'C31,C33', 'A31,B31']
})

lab_rooms = pd.DataFrame({
    'RoomID': ['AeroLab', 'StructLab'],
    'BookedSlots': ['', 'L']
})

# Generate schedule
full_schedule, _, _, _ = schedule_courses(courses, faculty, lab_rooms)

# Add course names to schedule
for code in full_schedule:
    full_schedule[code]['name'] = courses.loc[courses['SubjectCode'] == code, 'SubjectName'].iloc[0]

# Visualize
generate_console_timetable(full_schedule)
generate_html_timetable(full_schedule)
export_to_excel(full_schedule)