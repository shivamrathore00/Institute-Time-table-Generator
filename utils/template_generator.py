import pandas as pd
from io import BytesIO

def generate_template():
    """Generate a template Excel file matching newinput1.xlsx format"""
    # Define columns and sample data matching newinput1.xlsx
    sample_data = {
        'Subject Number': [
            'AE21202/AE21002', 
            'AE29202/AE29002',
            'AE20202/AE21008',
            'Anysubject'
        ],
        'Subject Name': [
            'Low Speed Aerodynamics', 
            'Aerodynamics Lab I',
            'Introduction to Flight Vehicle Controls'
        ],
        'L-T-P': ['3-1-0', '0-0-3', '3-0-0'],
        'Teacher(s)': ['SG', 'MK+SMD', 'SH'],
        'Type': ['Core', 'Lab', 'Core'],
        'Batch': ['2nd', '2nd', '2nd'],
        'Room': ['', 'Aero-lab', '']
    }
    
    output = BytesIO()
    df = pd.DataFrame(sample_data)
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    output.seek(0)
    return output




# import pandas as pd
# from io import BytesIO

# def generate_template():
#     """Generate combined template file with Courses and Faculty sheets"""
#     output = BytesIO()
    
#     # Courses template
#     courses_columns = [
#         'SubjectCode', 'SubjectName', 'Type', 'Credits', 'L-T-P', 
#         'AllowedSlots', 'RoomPref', 'Faculty1', 'Faculty2', 'Batches'
#     ]
#     courses_df = pd.DataFrame(columns=courses_columns)
    
#     # Faculty template
#     faculty_columns = [
#         'Name', 'UnavailableSlots', 'CoursesQualifiedToTeach', 'MaxHours'
#     ]
#     faculty_df = pd.DataFrame(columns=faculty_columns)
    
#     # Save to Excel
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         courses_df.to_excel(writer, sheet_name='Courses', index=False)
#         faculty_df.to_excel(writer, sheet_name='Faculty', index=False)
    
#     return output.getvalue()