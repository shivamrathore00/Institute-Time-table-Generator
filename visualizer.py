from datetime import datetime
import pandas as pd
from io import BytesIO
from typing import Dict, Any

#creates an Excel file in memory (with two sheets schedule and faculty workload) from the given dictionary and return the file as bytes
def generate_excel_bytes(schedule: dict) -> bytes:
    """Generate Excel file in memory and return as bytes"""
    output = BytesIO()

    # Create main schedule sheet
    schedule_list = []
    for course_code, sessions in schedule.items():
        for session in sessions:
            schedule_list.append({ #collecting all relevent information and adding to dictionary
                'Course Code': course_code,
                'Course Name': session.get('course_name', ''),
                'Session Type': session['type'].capitalize(),
                'Day': session['day'],
                'Time': session['time'],
                'Faculty': session['faculty'],
                'Room': session.get('room', ''),
                'Batch': session.get('batch', ''),
                'Duration (hrs)': session.get('duration', 1)
            })

    # Create faculty workload sheet
    faculty_hours = {}
    for sessions in schedule.values():
        for session in sessions:
            faculty = session['faculty']
            duration = session.get('duration', 1)
            faculty_hours[faculty] = faculty_hours.get(faculty, 0) + duration

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        pd.DataFrame(schedule_list).to_excel(writer, sheet_name='Schedule', index=False)
        faculty_df = pd.DataFrame({
            'Faculty': list(faculty_hours.keys()),
            'Scheduled Hours': list(faculty_hours.values())
        })
        faculty_df.to_excel(writer, sheet_name='Faculty Workload', index=False)

    return output.getvalue()


def get_session_color(session_type, color_map):
    """Get color for session type with flexible matching"""
    key = session_type.lower().strip()
    mapping = {
        'lab': ['lab', 'labs', 'laboratory'],
        'practical': ['practical', 'practicals', 'prac'],
        'tutorial': ['tutorial', 'tut'],
        'lecture': ['lecture', 'lec'],
        'core': ['core', 'compulsory'],
        'elective': ['elective', 'optional']
    }
    for cat, aliases in mapping.items():
        if key in aliases:
            return color_map.get(cat)
    return '#7f8c8d'


def normalize_time(time_str):
    if ':' not in time_str:
        return time_str
    parts = time_str.split(':')
    hour = parts[0].zfill(2)
    minute = parts[1][:2].zfill(2)
    return f"{hour}:{minute}"


def normalize_time_slot(slot):
    if ' - ' in slot:
        start, end = slot.split(' - ', 1)
    else:
        parts = slot.split('-')
        start = parts[0].strip()
        end = parts[1].strip() if len(parts) > 1 else ''
    start_n = normalize_time(start)
    end_n = normalize_time(end) if end else ''
    if not end_n and start_n:
        hr = int(start_n.split(':')[0])
        end_n = f"{hr:02d}:55"
    return f"{start_n} - {end_n}" if end_n else start_n



def generate_time_slots():
    return [f"{h:02d}:00 - {h:02d}:55" for h in range(8, 18)]


def generate_html(schedule: dict) -> str:
    color_map = {
        'lab': '#e74c3c', # lab or practical are same
        'practical': '#e74c3c',
        'tutorial': '#9b59b6',
        'lecture': '#3498db', #lecture and core color should be same both are same
        'core': '#2ecc71',
        'elective': '#f39c12'
    }
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    all_slots = generate_time_slots()

    matrix = {day: {ts: None for ts in all_slots} for day in days} # initialize a tabel name matrix for each day and time slot
    occupied = {day: set() for day in days}

    # Fill matrix with sessions
    for code, ses_list in schedule.items():
        for s in ses_list:
            day = s['day']
            duration = s.get('duration', 1)
            start_slot = normalize_time_slot(s['time'])
            start_time = start_slot.split(' - ')[0]
            time_index = [t.split(' - ')[0] for t in all_slots]
            if start_time not in time_index:
                continue  # ignore non-matching time
            idx = time_index.index(start_time)
            if idx + duration > len(all_slots):
                continue  # skip overflow
            span_slots = all_slots[idx:idx + duration]
            if any(ts in occupied[day] for ts in span_slots):
                continue  # already occupied
            matrix[day][all_slots[idx]] = {**s, 'course_code': code, 'duration': duration}
            for ts in span_slots:
                occupied[day].add(ts)

    # Generate HTML
    html = f"""<!DOCTYPE html><html><head>
<meta charset="UTF-8"><title>Timetable</title>
<style>
  * {{box-sizing: border-box; font-family: 'Segoe UI', sans-serif;}}
  body {{margin: 0; padding: 20px; background: #f5f7fa;}}
  .timetable-container {{overflow-x: auto; background: #fff; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);}}
  .timetable {{width: 100%; border-collapse: collapse; min-width: 1000px;}}
  .timetable th, .timetable td {{border: 1px solid #e0e6ed; padding: 10px; text-align: center;}}
  .timetable th {{background: #3498db; color: white;}}
  .time-header {{background: #2c3e50; color: white;}}
  .course-card {{padding: 8px; margin: 4px 0; border-radius: 6px; color: white; cursor: move;}}
  .empty-slot {{color: #aaa; font-size: 11px;}}
  .drop-target.highlight {{outline: 2px dashed #27ae60;}}

   .course-card {{
    padding: 6px;
    margin: 3px 0;
    border-radius: 4px;
    font-size: 0.85em;
  }}
  .drop-target {{
    min-height: 60px;
    overflow-y: auto;
  }}

</style>
</head><body>
<div class="header"><h2>Timetable Preview</h2></div>
<div class="timetable-container">
<table class="timetable"><thead><tr><th class="time-header">Day</th>"""

    for ts in all_slots:
        html += f"<th>{ts}</th>"
    html += "</tr></thead><tbody>"

    for day in days:
        html += f"<tr><td class='time-header'><strong>{day}</strong></td>"
        skip = 0
        for i, ts in enumerate(all_slots):
            if skip > 0:
                skip -= 1
                continue
            session = matrix[day][ts]
            if session:
                dur = session['duration']
                color = get_session_color(session['type'], color_map)
                html += f"<td colspan='{dur}' class='drop-target' data-day='{day}' data-time='{ts}'>"
                html += f"<div class='course-card' draggable='true' data-course='{session['course_code']}' data-type='{session['type']}' data-faculty='{session['faculty']}' data-duration='{dur}' style='background:{color}'>"
                html += f"<div class='course-code'>{session['course_code']}</div><div class='course-details'>{session['faculty']}</div></div></td>"
                skip = dur - 1
            else:
                html += f"<td class='drop-target' data-day='{day}' data-time='{ts}'><div class='empty-slot'>Available</div></td>"
        html += "</tr>"
    html += "</tbody></table></div>"

    # Add drag/drop script
    html += """
<script>
        document.addEventListener('DOMContentLoaded', () => {
            let dragged = null;
            let origin = null;
            let originalSpan = 1;
            let originalDuration = 1;
            let originalPosition = null;

            // Initialize the timetable
            updateEmpty();

            // Add event listeners to all course cards
            document.querySelectorAll('.course-card').forEach(card => {
                card.addEventListener('dragstart', e => {
                    dragged = card;
                    origin = card.closest('td');
                    originalSpan = parseInt(origin.getAttribute('colspan') || "1");
                    originalDuration = parseInt(dragged.getAttribute('data-duration') || "1");
                    originalPosition = {
                        row: origin.parentElement.rowIndex,
                        col: origin.cellIndex
                    };

                    // Store original duration
                    dragged.setAttribute('data-original-duration', originalDuration);

                    // Unmerge cell if needed
                    const row = origin.parentElement;
                    const startIndex = Array.from(row.children).indexOf(origin);
                    
                    if (originalSpan > 1) {
                        origin.removeAttribute('colspan');
                        for (let i = 1; i < originalSpan; i++) {
                            const emptyTD = document.createElement('td');
                            emptyTD.className = 'drop-target';
                            emptyTD.innerHTML = "<div class='empty-slot'>Available</div>";
                            row.insertBefore(emptyTD, row.children[startIndex + i]);
                        }
                    }

                    setTimeout(() => card.style.opacity = '0.4', 0);
                });

                card.addEventListener('dragend', () => {
                    if (dragged) {
                        dragged.style.opacity = '1';
                        document.querySelectorAll('.drop-target.highlight').forEach(cell => 
                            cell.classList.remove('highlight'));
                    }
                });
            });

            // Add event listeners to all drop targets
            document.querySelectorAll('.drop-target').forEach(cell => {
                cell.addEventListener('dragover', e => {
                    e.preventDefault();
                    cell.classList.add('highlight');
                });
                
                cell.addEventListener('dragleave', () => {
                    cell.classList.remove('highlight');
                });
                
                cell.addEventListener('drop', e => {
                    e.preventDefault();
                    cell.classList.remove('highlight');
                    
                    if (!dragged || origin === cell) return;

                    originalDuration = parseInt(dragged.getAttribute('data-original-duration') || "1");
                    const row = cell.parentElement;
                    const startIndex = Array.from(row.children).indexOf(cell);
                    
                    let canPlace = false;
                    let placementType = '';
                    
                    // Check for existing courses in the target cell
                    const existingCards = cell.querySelectorAll('.course-card');
                    const existingDuration = existingCards.length > 0 ? 
                        parseInt(existingCards[0].getAttribute('data-duration') || "1") : 0;

                    // Check if we can place in the same slot
                    if (existingCards.length > 0) {
                        // All courses must have the same duration
                        const allSameDuration = Array.from(existingCards).every(card => {
                            const cardDuration = parseInt(card.getAttribute('data-duration') || "1");
                            return cardDuration === originalDuration;
                        });
                        
                        if (allSameDuration && existingDuration === originalDuration) {
                            canPlace = true;
                            placementType = 'same-slot';
                        }
                    } else {
                        // Check if we have enough consecutive slots for multi-slot courses
                        if (originalDuration === 1) {
                            // Single slot course can be placed in any empty cell
                            canPlace = true;
                            placementType = 'empty-slot';
                        } else {
                            // Multi-slot course requires consecutive empty cells
                            canPlace = true;
                            
                            for (let i = 0; i < originalDuration; i++) {
                                const targetCell = row.children[startIndex + i];
                                
                                if (!targetCell || 
                                    !targetCell.classList.contains('drop-target') || 
                                    targetCell.querySelector('.course-card') ||
                                    targetCell.hasAttribute('colspan')) {
                                    canPlace = false;
                                    break;
                                }
                            }
                            
                            placementType = 'consecutive';
                        }
                    }
                    
                    if (canPlace) {
                        // Remove the dragged element from origin
                        origin.removeChild(dragged);
                        
                        // Place in new cell
                        if (placementType === 'same-slot') {
                            // Add to existing slot
                            cell.appendChild(dragged);
                        } else if (placementType === 'empty-slot') {
                            // Place in empty slot
                            if (cell.querySelector('.empty-slot')) {
                                cell.querySelector('.empty-slot').remove();
                            }
                            cell.appendChild(dragged);
                        } else if (placementType === 'consecutive') {
                            // Place in consecutive slots
                            if (cell.querySelector('.empty-slot')) {
                                cell.querySelector('.empty-slot').remove();
                            }
                            cell.appendChild(dragged);
                            
                            // Set colspan and remove next cells
                            if (originalDuration > 1) {
                                cell.setAttribute('colspan', originalDuration);
                                
                                for (let i = 1; i < originalDuration; i++) {
                                    const nextCell = row.children[startIndex + 1];
                                    if (nextCell) {
                                        row.removeChild(nextCell);
                                    }
                                }
                            }
                        }
                        
                        // Update empty slots
                        updateEmpty();
                    } else {
                        // If can't place, return to original position
                        alert(`Cannot place here. ${originalDuration}-hour courses can only be placed with other ${originalDuration}-hour courses.`);
                        
                        // Restore to original position
                        if (originalPosition) {
                            const originalRow = document.querySelector(`tbody tr:nth-child(${originalPosition.row + 1})`);
                            const originalCell = originalRow.cells[originalPosition.col];
                            originalCell.appendChild(dragged);
                            
                            // Restore colspan if needed
                            if (originalSpan > 1) {
                                originalCell.setAttribute('colspan', originalSpan);
                                
                                // Remove any extra cells created during drag
                                const row = originalCell.parentElement;
                                const startIndex = Array.from(row.children).indexOf(originalCell);
                                for (let i = 1; i < originalSpan; i++) {
                                    if (row.children[startIndex + i]) {
                                        row.removeChild(row.children[startIndex + i]);
                                    }
                                }
                            }
                        }
                    }
                    
                    // Clean up
                    dragged.style.opacity = '1';
                    dragged = null;
                });
            });

            // Function to update empty slots
            function updateEmpty() {
                document.querySelectorAll('.drop-target').forEach(cell => {
                    if (!cell.querySelector('.course-card') && !cell.querySelector('.empty-slot')) {
                        const empty = document.createElement('div');
                        empty.className = 'empty-slot';
                        empty.textContent = 'Available';
                        cell.appendChild(empty);
                    } else if (cell.querySelector('.course-card')) {
                        cell.querySelector('.empty-slot')?.remove();
                    }
                });
            }
        });
    </script>



</body></html>"""
    return html




def generate_html_per_batch(schedule: dict) -> dict:
    """Generate separate HTML for each batch year"""
    from collections import defaultdict

    batch_grouped = defaultdict(lambda: defaultdict(list))
    for course_code, sessions in schedule.items():
        for session in sessions:
            batch = session['batch'] # groups all session by course code
            batch_grouped[batch][course_code].append(session)

    return {batch: generate_html(batch_schedule) for batch, batch_schedule in batch_grouped.items()}

