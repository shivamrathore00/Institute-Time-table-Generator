import pandas as pd

def validate_ltp(ltp_str):
    try:
        parts = ltp_str.split('-')
        if len(parts) != 3:
            return False
        l, t, p = map(int, parts)
        return l >= 0 and t >= 0 and p >= 0
    except:
        return False

def validate_data(courses, slot_master_path):
    errors = []
    slots = pd.read_excel(slot_master_path, sheet_name='Slots')
    
    # Validate required columns
    required_course_cols = ['SubjectCode', 'Type', 'L-T-P', 'Faculty1', 'BatchYear']
    for col in required_course_cols:
        if col not in courses.columns:
            errors.append(f"Missing column in Courses: {col}")
    
    if errors:
        return errors
    
    # Validate L-T-P format
    for _, course in courses.iterrows():
        if not validate_ltp(course['L-T-P']):
            errors.append(f"Invalid L-T-P format for {course['SubjectCode']}")
    
    # Validate slot codes
    slot_codes = slots['SlotCode'].tolist()
    for group in courses['AllowedSlots'].dropna():
        for code in str(group).split(','):
            if code.strip() not in slot_codes:
                errors.append(f"Invalid slot code: {code.strip()}")
    
    return errors