import pandas as pd
from src.scheduler import schedule_all

# Sample Data
courses = pd.DataFrame({
    'SubjectCode': ['AE29202', 'AE21202', 'AE31004'],
    'SubjectName': ['Aero Lab', 'Low Speed Aero', 'Aircraft Stability'],
    'Type': ['Lab', 'Core', 'Core'],
    'Batches': ['2nd', '2nd', '3rd'],
    'Faculty': ['MK,SMD', 'SG', 'MS'],
    'Duration': [3, 4, 4],
    'LabRoom': ['AeroLab', None, None]
})

faculty = pd.DataFrame({
    'Name': ['SG', 'MS', 'MK,SMD'],
    'UnavailableSlots': ['F41', None, 'L']
})

# Run scheduler
schedule, conflicts = schedule_all(
    courses_df=courses,
    faculty_df=faculty,
    slot_master_path='data/slot_master.xlsx'
)

# Results
print("✅ SCHEDULED COURSES:")
for code, details in schedule.items():
    print(f"\n{code}: {details.get('name', '')}")
    print(f"  - Type: {details.get('type', '')}")
    print(f"  - Slot: {details.get('slot', '')} ({details.get('day', '')} {details.get('time', '')})")
    print(f"  - Faculty: {details.get('faculty', '')}")
    if details.get('type') == 'lab':
        print(f"  - Lab Room: {details.get('room', '')}")

print("\n⚠️ CONFLICTS:" if conflicts else "\n✅ NO CONFLICTS")
print("\n".join(conflicts) if conflicts else "")






















# import pandas as pd
# from src.scheduler import schedule_all

# # Sample Data
# courses = pd.DataFrame({
#     'SubjectCode': ['AE29202', 'AE21202', 'AE31004'],
#     'SubjectName': ['Aero Lab', 'Low Speed Aero', 'Aircraft Stability'],
#     'Type': ['Lab', 'Core', 'Core'],
#     'Batches': ['2nd', '2nd', '3rd'],
#     'Faculty': ['MK,SMD', 'SG', 'MS'],
#     'Duration': [3, 4, 4],
#     'LabRoom': ['AeroLab', None, None]
# })

# faculty = pd.DataFrame({
#     'Name': ['SG', 'MS', 'MK,SMD'],
#     'UnavailableSlots': ['F41', None, 'L']
# })

# # Run scheduler
# schedule, conflicts = schedule_all(
#     courses_df=courses,
#     faculty_df=faculty,
#     slot_master_path='data/slot_master.xlsx'
# )

# # Results
# print("✅ SCHEDULED COURSES:")
# for code, details in schedule.items():
#     print(f"\n{code}: {details['SubjectName']}")
#     print(f"  - Type: {details['type']}")
#     print(f"  - Slot: {details['slot']} ({details['day']} {details['time']})")
#     print(f"  - Faculty: {details['faculty']}")
#     if details['type'] == 'lab':
#         print(f"  - Lab Room: {details['room']}")

# print("\n⚠️ CONFLICTS:" if conflicts else "\n✅ NO CONFLICTS")
# print("\n".join(conflicts) if conflicts else "")





















# # """
# # Test script for lab scheduler
# # Run with: python test_scheduler.py
# # """
# # import pandas as pd
# # from src.data_loader import load_courses, load_faculty
# # from src.scheduler import schedule_labs

# # # 1. Load sample data
# # print("="*50)
# # print("🚀 STARTING LAB SCHEDULER TEST")
# # print("="*50)
# # courses = load_courses('data/sample_input.xlsx')
# # faculty = load_faculty('data/sample_input.xlsx')

# # # 2. Run scheduler
# # if courses is not None and faculty is not None:
# #     lab_schedule = schedule_labs(courses, faculty)
    
# #     # 3. Display results
# #     print("\n" + "="*50)
# #     print("📋 FINAL LAB SCHEDULE")
# #     print("="*50)
# #     for lab, details in lab_schedule.items():
# #         print(f"{lab}:")
# #         print(f"  - Slot: {details['slot']}")
# #         print(f"  - Faculty: {details['faculty']}")
# #         print(f"  - Room: {details['room']}")
# #         print("-" * 30)
# # else:
# #     print("❌ Failed to load data. Check previous errors.")