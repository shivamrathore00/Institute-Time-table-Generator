"""
Test script for lab scheduler
Run with: python test_scheduler.py
"""
import pandas as pd
from src.data_loader import load_courses, load_faculty
from src.scheduler import schedule_labs

# 1. Load sample data
print("="*50)
print("🚀 STARTING LAB SCHEDULER TEST")
print("="*50)
courses = load_courses('data/sample_input.xlsx')
faculty = load_faculty('data/sample_input.xlsx')

# 2. Run scheduler
if courses is not None and faculty is not None:
    lab_schedule = schedule_labs(courses, faculty)
    
    # 3. Display results
    print("\n" + "="*50)
    print("📋 FINAL LAB SCHEDULE")
    print("="*50)
    for lab, details in lab_schedule.items():
        print(f"{lab}:")
        print(f"  - Slot: {details['slot']}")
        print(f"  - Faculty: {details['faculty']}")
        print(f"  - Room: {details['room']}")
        print("-" * 30)
else:
    print("❌ Failed to load data. Check previous errors.")