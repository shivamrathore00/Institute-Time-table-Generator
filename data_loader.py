import pandas as pd

def infer_batch(batch_str):
    """Convert batch numbers to descriptive names and handle multiple batches"""
    if pd.isna(batch_str) or not str(batch_str).strip():
        return []
    
    batch_names = {
        '1': '1st',
        '2': '2nd',
        '3': '3rd',
        '4': '4th',
        '5': '5th'
    }
    
    batches = []
    for num in str(batch_str).split(','):
        num = num.strip()
        if num in batch_names:
            batches.append(batch_names[num])
        elif num.isdigit():
            batches.append(f"{num}th")
    return batches

def infer_type(ltp):
    try:
        l, t, p = map(int, str(ltp).split('-'))
        if p > 0:
            return 'Lab'
        elif t > 0:
            return 'Tutorial'
        else:
            return 'Lecture'
    except:
        return 'Unknown'

def expand_teachers(teacher_str):
    return [t.strip() for t in str(teacher_str).split('+')]


def load_courses_from_minimal_format(file_stream):
    df = pd.read_excel(file_stream)
    
    # Handle different column name variations
    column_map = {
        'Subject Number': 'SubjectCode',
        'Subject Name': 'SubjectName',
        'L-T-P': 'L-T-P',
        'Teacher(s)': 'FacultyRaw',
        'Batch': 'BatchRaw',
        'Room': 'RoomPref'
    }
    
    # Rename columns to standard names
    for old_name, new_name in column_map.items():
        if old_name in df.columns:
            df.rename(columns={old_name: new_name}, inplace=True)
    
    # Create missing columns if needed
    if 'BatchRaw' not in df.columns:
        df['BatchRaw'] = ''
    if 'RoomPref' not in df.columns:
        df['RoomPref'] = ''
    
    # Standardize data formats
    # Handle L-T-P date formatting issue
    #df['L-T-P'] = df['L-T-P'].astype(str).apply(lambda x: x.split(' ')[0] if ' ' in x else x).apply(fix_ltp_string)
    df['L-T-P'] = df['L-T-P'].apply(fix_ltp_string)
    df['FacultyRaw'] = df['FacultyRaw'].astype(str).str.strip()
    df['FacultyList'] = df['FacultyRaw'].apply(expand_teachers)
    df['Faculty1'] = df['FacultyList'].apply(lambda x: x[0] if x else '')
    
    # Process batches and expand rows
    df['BatchList'] = df['BatchRaw'].apply(infer_batch)
    
    # Expand DataFrame for multi-batch courses
    expanded_rows = []
    for _, row in df.iterrows():
        if row['BatchList']:
            # For courses with multiple batches
            for batch in row['BatchList']:
                new_row = row.copy()
                new_row['BatchYear'] = batch
                # Preserve original batch list for reference
                new_row['AllBatches'] = ','.join(row['BatchList'])
                expanded_rows.append(new_row)
        else:
            # For courses without specified batch
            inferred = infer_batch_from_code(row['SubjectCode'])
            row['BatchYear'] = inferred
            row['AllBatches'] = inferred
            expanded_rows.append(row)
    
    expanded_df = pd.DataFrame(expanded_rows)
    
    # Determine course type based on L-T-P
    expanded_df['Type'] = expanded_df['L-T-P'].apply(infer_type)
    
    # Return all relevant columns including AllBatches
    return expanded_df[['SubjectCode', 'SubjectName', 'L-T-P', 'Faculty1', 
                       'BatchYear', 'AllBatches', 'Type', 'RoomPref']]
def fix_ltp_string(ltp):
    """Ensure L-T-P string is in 'int-int-int' format."""
    try:
        ltp = str(ltp).replace('/', '-').replace('\\', '-').strip()
        parts = ltp.split('-')
        parts = [int(p) if p.isdigit() else 0 for p in parts]
        while len(parts) < 3:
            parts.append(0)
        return f"{parts[0]}-{parts[1]}-{parts[2]}"
    except:
        return "0-0-0"

def infer_batch_from_code(subject_code):
    """Infer batch year from subject code prefix"""
    code = str(subject_code).split('/')[0].strip()
    digits = ''.join(filter(str.isdigit, code))
    if len(digits) >= 3:
        if digits.startswith('1'):
            return '1st'
        elif digits.startswith('2'):
            return '2nd'
        elif digits.startswith('3') or digits.startswith('4'):
            return '3rd'
        elif digits.startswith('5') or digits.startswith('6'):
            return '4th'
    return 'Unknown'
# import pandas as pd
# from datetime import datetime

# def infer_batch(batch_str):
#     """Convert batch numbers to descriptive names and handle multiple batches"""
#     if pd.isna(batch_str) or not str(batch_str).strip():
#         return []
    
#     batch_names = {
#         '1': '1st',
#         '2': '2nd',
#         '3': '3rd',
#         '4': '4th',
#         '5': '5th'
#     }
    
#     batches = []
#     for num in str(batch_str).split(','):
#         num = num.strip()
#         if num in batch_names:
#             batches.append(batch_names[num])
#         elif num.isdigit():
#             batches.append(f"{num}th")
#     return batches

# def infer_type(ltp):
#     try:
#         l, t, p = map(int, str(ltp).split('-'))
#         if p > 0:
#             return 'Lab'
#         elif t > 0:
#             return 'Tutorial'
#         else:
#             return 'Lecture'
#     except:
#         return 'Unknown'

# def expand_teachers(teacher_str):
#     return [t.strip() for t in str(teacher_str).split('+')]

# def fix_ltp_string(ltp):
#     """Robust L-T-P formatting with Excel date handling"""
#     if isinstance(ltp, datetime.datetime):  # Handle Excel date conversion
#         return "0-0-0"
    
#     ltp = str(ltp).strip()
#     if ltp.lower() in ['nan', 'nat', '']:
#         return "0-0-0"
    
#     # Handle various separators and date formats
#     ltp = ltp.replace('/', '-').replace('\\', '-').replace(' ', '')
    
#     # Fix Excel date conversions (e.g., "3-1-0" → "3-Jan" → "1/3/00")
#     if any(char in ltp for char in ['/', 'Jan', 'Feb', 'Mar']):
#         parts = []
#         for part in ltp.split('-'):
#             try:
#                 if part.isdigit():
#                     parts.append(part)
#                 else:
#                     parts.append('0')
#             except:
#                 parts.append('0')
#         ltp = '-'.join(parts[:3])
#     else:
#         parts = ltp.split('-')
    
#     # Ensure exactly 3 parts
#     while len(parts) < 3:
#         parts.append('0')
#     parts = parts[:3]
    
#     # Convert to integers safely
#     try:
#         return f"{int(float(parts[0]))}-{int(float(parts[1]))}-{int(float(parts[2]))}"
#     except:
#         return "0-0-0"

# def infer_batch_from_code(subject_code):
#     """Infer batch year from subject code prefix"""
#     code = str(subject_code).split('/')[0].strip()
#     digits = ''.join(filter(str.isdigit, code))
#     if len(digits) >= 3:
#         if digits.startswith('1'):
#             return '1st'
#         elif digits.startswith('2'):
#             return '2nd'
#         elif digits.startswith('3') or digits.startswith('4'):
#             return '3rd'
#         elif digits.startswith('5') or digits.startswith('6'):
#             return '4th'
#     return 'Unknown'

# def load_courses_from_minimal_format(file_stream):
#     df = pd.read_excel(file_stream)
    
#     # Handle different column name variations
#     column_map = {
#         'Subject Code': 'SubjectCode',
#         'Subject Name': 'SubjectName',
#         'Teacher(s)': 'FacultyRaw',
#         'L-T-P': 'L-T-P',
#         'Type': 'Type',
#         'Batch': 'BatchRaw',
#         'Room': 'RoomPref'
#     }
    
#     # Rename columns to standard names
#     for old_name, new_name in column_map.items():
#         if old_name in df.columns:
#             df.rename(columns={old_name: new_name}, inplace=True)
    
#     # Create missing columns if needed
#     if 'BatchRaw' not in df.columns:
#         df['BatchRaw'] = ''
#     if 'RoomPref' not in df.columns:
#         df['RoomPref'] = ''
    
#     # Handle L-T-P formatting
#     df['L-T-P'] = df['L-T-P'].apply(fix_ltp_string)
    
#     # Process faculty data
#     df['FacultyRaw'] = df['FacultyRaw'].astype(str).str.strip()
#     df['FacultyList'] = df['FacultyRaw'].apply(expand_teachers)
#     df['Faculty1'] = df['FacultyList'].apply(lambda x: x[0] if x else '')
    
#     # Process batches and expand rows
#     df['BatchList'] = df['BatchRaw'].apply(infer_batch)
    
#     # Expand DataFrame for multi-batch courses
#     expanded_rows = []
#     for _, row in df.iterrows():
#         if row['BatchList']:
#             for batch in row['BatchList']:
#                 new_row = row.copy()
#                 new_row['BatchYear'] = batch
#                 new_row['AllBatches'] = ','.join(row['BatchList'])
#                 expanded_rows.append(new_row)
#         else:
#             inferred = infer_batch_from_code(row['SubjectCode'])
#             row['BatchYear'] = inferred
#             row['AllBatches'] = inferred
#             expanded_rows.append(row)
    
#     expanded_df = pd.DataFrame(expanded_rows)
    
#     # Determine course type based on L-T-P
#     expanded_df['Type'] = expanded_df['L-T-P'].apply(infer_type)
    
#     # Return all relevant columns
#     return expanded_df[['SubjectCode', 'SubjectName', 'L-T-P', 'Faculty1', 
#                        'BatchYear', 'AllBatches', 'Type', 'RoomPref']]
