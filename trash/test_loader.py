from src.data_loader import load_courses, load_faculty

# Test with sample data 
courses = load_courses('data/sample_input.xlsx')
faculty = load_faculty('data/sample_input.xlsx')

if courses is not None:
    print("\nCourses DataFrame Columns:")
    print(courses.columns.tolist())
    
if faculty is not None:
    print("\nFaculty DataFrame Columns:")
    print(faculty.columns.tolist())
