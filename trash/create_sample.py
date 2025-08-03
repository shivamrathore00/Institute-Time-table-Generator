import pandas as pd

# Create sample courses data
courses_data = {
    'SubjectCode': ['AE20202'],
    'SubjectName': ['Flight Controls'],
    'Type': ['Theory'],
    'AllowedSlots': ['C31,C32,C33']
}
courses_df = pd.DataFrame(courses_data)

# Create sample faculty data
faculty_data = {
    'Name': ['Dr. Smith'],
    'MaxHours': [16],
    'CoursesQualifiedToTeach': ['AE20202,AE21202']
}
faculty_df = pd.DataFrame(faculty_data)

# Save to Excel
with pd.ExcelWriter('data/sample_input.xlsx') as writer:
    courses_df.to_excel(writer, sheet_name='Courses', index=False)
    faculty_df.to_excel(writer, sheet_name='Faculty', index=False)

print("Sample Excel file created at data/sample_input.xlsx")