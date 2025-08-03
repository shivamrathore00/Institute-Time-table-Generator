"""
Test enhanced scheduler with both lab and theory courses
"""
import pandas as pd
from src.scheduler import schedule_courses

# Sample Data
courses = pd.DataFrame({
    'SubjectCode': ['AE29202', 'AE21202', 'AE20202', 'AE40018'],
    'Type': ['Lab', 'Theory', 'Theory', 'Theory'],
    'Faculty': ['Prof. Dash', 'Prof. Ghosh', 'Prof. Hota', 'Prof. Ghosh'],
    'AllowedSlots': ['J,K', 'C31,C32', 'A31,A32', 'C31,C33'],
    'RoomPref': ['AeroLab', '', '', '']
    'Batches': ['2nd', '2nd,3rd', '3rd'] 
})

faculty = pd.DataFrame({
    'Name': ['Prof. Dash', 'Prof. Ghosh', 'Prof. Hota'],
    'AvailableSlots': ['J,L', 'C31,C33', 'A31,B31']
})

lab_rooms = pd.DataFrame({
    'RoomID': ['AeroLab', 'StructLab'],
    'BookedSlots': ['', 'L']
})


# Run scheduler
full_schedule, labs, theories, conflicts = schedule_courses(courses, faculty, lab_rooms)

# Print results
print("🔷 FULL SCHEDULE:")
for code, details in full_schedule.items():
    print(f"{code} ({details['type']}):")
    print(f"  - Slot: {details['slot']}")
    print(f"  - Faculty: {details['faculty']}")
    print(f"  - Room: {details['room'] or 'N/A'}")

print("\n🔷 LABS:")
print(labs)

print("\n🔷 THEORY:")
print(theories)

print("\n🔷 CONFLICTS:")
print("\n".join(conflicts) if conflicts else "No conflicts")