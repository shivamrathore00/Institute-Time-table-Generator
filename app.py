from flask import Flask, render_template, request, send_file, session 
import pandas as pd # to read and write excel files
from io import BytesIO # handles files in memory no need to save them to disk
from pathlib import Path 
import uuid # generate unique id used to track session
import json # jason converts data to and from a format that can be stored in the session
import os 
# flask create webapp, request handles data from users,send_files: semd files to users
# for us excel file, session: stoers data for a user across requests

from data_loader import load_courses_from_minimal_format as load_courses
from scheduler import TimetableScheduler
from visualizer import generate_html, generate_excel_bytes, generate_html_per_batch

app = Flask(__name__)  #start the flask app
app.secret_key = os.urandom(24)

BASE_DIR = Path(__file__).resolve().parent #folder where app is running
SLOT_MASTER_PATH = BASE_DIR / 'data' / 'slot_master.xlsx' # slot master path

@app.route('/')  # routes shows pages
def index():
    return render_template('upload.html')

@app.route('/download_template')
def download_template():
    sample_data = {
        'Subject Number': ['AE21202/AE21002', 'AE29202/AE29002'],
        'Subject Name': ['Low Speed Aerodynamics', 'Aerodynamics Lab I'],
        'L-T-P': ['3-1-0', '0-0-3'],
        'Teacher(s)': ['SG', 'MK+SMD'],
        'Type': ['Core', 'Lab'],
        'Batch': ['2nd', '2nd'],
        'Room': ['', 'Aero-lab']
    }
    
    output = BytesIO() # creates in memory file
    df = pd.DataFrame(sample_data) #Converts the dictionary sample_data into a pandas DataFrame (df).
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0) # moves the cursor to the start 

    return send_file(output,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True, # download file not displaying
                    download_name='timetable_input_template.xlsx')

@app.route('/generate', methods=['POST'])  # / generate that only accepts POST requests  like uploading a file
def generate():
    if 'file' not in request.files or request.files['file'].filename == '':
        return render_template('error.html', errors=["Please upload a valid Excel file."]) # check if file uploaded or not

    try:
        file = request.files['file']  #get file
        file_bytes = BytesIO(file.read()) # reads the file in memory
        courses = load_courses(file_bytes) # calling function load_courses to process the uploaded file and extract the data

        if not SLOT_MASTER_PATH.exists():
            return render_template('error.html', errors=["Slot master file not found."]) # slots file check if it is there or not

        slot_master = pd.read_excel(SLOT_MASTER_PATH, sheet_name='Slots') #reading slots sheet data
        scheduler = TimetableScheduler(courses, slot_master)  # creates object name scheduler giving it the courses and available slots 
        schedule = scheduler.generate_schedule()     # generate the timetable (core logic for arranging courses into slots)

        session_id = str(uuid.uuid4())
        session[session_id] = json.dumps(schedule)

        # Generate per-batch HTML
        batch_htmls = generate_html_per_batch(schedule)

        return render_template('multi_preview.html', batch_htmls=batch_htmls, session_id=session_id)

    # except Exception as e:
    #     return render_template('error.html', errors=[f"Error generating timetable: {str(e)}"]) #If anything goes wrong in the try block (bad file, scheduling error, etc.), it shows an error page with the error message.

    #change here
    except Exception as e:
        import traceback
        error_detail = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        return render_template('error.html', errors=[error_detail])


@app.route('/download/<session_id>')
def download_excel(session_id):
    try:
        schedule_json = session.get(session_id)
        if not schedule_json:
            return render_template('error.html', errors=["Session expired or invalid."])

        schedule = json.loads(schedule_json) # json to python object
        output = BytesIO(generate_excel_bytes(schedule))

        return send_file(output,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True,
                         download_name='timetable.xlsx') # sending downloadable excel file
    except Exception as e:
        return render_template('error.html', errors=[f"Error downloading timetable: {str(e)}"])


# dynamically adjustment of timetable
@app.route('/adjust', methods=['POST'])
def adjust():
    try:
        session_id = request.form.get('session_id') #session id fetteched from data
        updated_schedule = json.loads(request.form.get('schedule', '{}'))

        if not session_id:
            return "Missing session ID", 400

        session[session_id] = json.dumps(updated_schedule)
        html = generate_html(updated_schedule)
        return html

    except Exception as e:
        return f"<div class='error'>Adjustment error: {str(e)}</div>", 500

if __name__ == '__main__': #starts the flask webserver when run scripts directly
    app.run(debug=True)  #debug=True helps you see errors and automatically reloads the app when you make code changes


