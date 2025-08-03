import pandas as pd
from collections import defaultdict
import datetime

class TimetableScheduler:
    def __init__(self, courses, slot_master):
        self.courses = courses
        self.slots = slot_master
        self.schedule = defaultdict(list)
        self.constraints = {
            'faculty_days': defaultdict(set),
            'batch_days': defaultdict(set),
            'subject_day': defaultdict(lambda: defaultdict(bool))
        }
        self.slot_groups = defaultdict(list)
        self._build_slot_groups()
    
    def _build_slot_groups(self):
        """Group slots by their group code"""
        for _, slot in self.slots.iterrows():
            group_code = slot['SlotCode'].split('(')[0].strip()
            self.slot_groups[group_code].append(slot.to_dict())
        
        # Sort each group by day and start time
        for group in self.slot_groups.values():
            group.sort(key=lambda x: (x['Day'], x['StartTime']))
    
    def parse_ltp(self, ltp_str):
        """Parse L-T-P string into (lecture, tutorial, practical)"""
        try:
            parts = ltp_str.split('-')
            if len(parts) != 3:
                return 0, 0, 0
            return int(parts[0]), int(parts[1]), int(parts[2])
        except:
            return 0, 0, 0
    
    def _compare_times(self, time1, time2):
        """Compare two time objects that could be strings or datetime.time"""
        if isinstance(time1, str):
            time1 = pd.to_datetime(time1).time()
        if isinstance(time2, str):
            time2 = pd.to_datetime(time2).time()
        return time1, time2
    
    def _has_conflict(self, course, day, slot):
        faculty = course['Faculty1']
        batch = course['BatchYear']
        subject_code = course['SubjectCode']
        
        # Get slot times properly
        slot_start, slot_end = self._compare_times(slot['StartTime'], slot['EndTime'])
        
        # Check faculty availability
        if faculty in self.constraints['faculty_days'][day]:
            for scheduled in self.schedule.values():
                for session in scheduled:
                    if session['faculty'] == faculty and session['day'] == day:
                        sess_start, sess_end = self._compare_times(
                            session['time'].split(' - ')[0],
                            session['time'].split(' - ')[1]
                        )
                        if max(slot_start, sess_start) < min(slot_end, sess_end):
                            return True
        
        
        # Check batch conflicts
        if batch in self.constraints['batch_days'][day]:
            for scheduled in self.schedule.values():
                for session in scheduled:
                    if session['batch'] == batch and session['day'] == day:
                        sess_start, sess_end = self._compare_times(
                            session['time'].split(' - ')[0],
                            session['time'].split(' - ')[1]
                        )
                        if max(slot_start, sess_start) < min(slot_end, sess_end):
                            return True
        
        # Check subject daily limit
        if self.constraints['subject_day'][subject_code].get(day, False):
            return True
        
        return False
    
    def _place_session(self, course, day, slot, session_type, duration):
        """Place a session and update constraints"""
        subject_code = course['SubjectCode']
        faculty = course['Faculty1']
        batch = course['BatchYear']
        l, t, p = self.parse_ltp(course['L-T-P'])

        actual_type = 'Tutorial' if session_type == 'Theory' and t > 0 else 'Lecture'

        # Format time string consistently
        start_time = slot['StartTime'] if isinstance(slot['StartTime'], str) else slot['StartTime'].strftime('%H:%M:%S')
        end_time = slot['EndTime'] if isinstance(slot['EndTime'], str) else slot['EndTime'].strftime('%H:%M:%S')
        
        entry = {
            'course_code': subject_code,
            'course_name': course['SubjectName'],
            'type': actual_type.lower(),
            'day': day,
            'time': f"{start_time} - {end_time}",
            'faculty': faculty,
            'duration': duration,
            'batch': batch
        }
        self.schedule[subject_code].append(entry)
        
        # Update constraints
        self.constraints['faculty_days'][day].add(faculty)
        self.constraints['batch_days'][day].add(batch)
        self.constraints['subject_day'][subject_code][day] = True
        
        # Remove the slot from available slots
        self.slots = self.slots[self.slots['SlotCode'] != slot['SlotCode']]
    
    def _assign_sessions(self, course, session_type, count, duration):
        """Assign individual sessions (fallback method)"""
        faculty = course['Faculty1']
        batch = course['BatchYear']
        subject_code = course['SubjectCode']
        
        for _ in range(count):
            assigned = False
            
            # Try all days in order
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                # Find available slots matching our requirements
                available = self.slots[
                    (self.slots['Day'] == day) &
                    (self.slots['Duration'] == duration) &
                    (self.slots['SlotType'] == ('Lab' if session_type == 'Lab' else 'Theory'))
                ]
                
                # Try each available slot
                for _, slot in available.iterrows():
                    if self._has_conflict(course, day, slot):
                        continue
                        
                    # Place the session if no conflicts
                    self._place_session(course, day, slot, session_type, duration)
                    assigned = True
                    break
                    
                if assigned:
                    break
                    
            # If we couldn't assign with desired duration, try smaller durations
            if not assigned and duration > 1:
                # Split into smaller chunks
                self._assign_sessions(course, session_type, count, duration-1)
    
    def _assign_with_group(self, course, group_code, total_hours):
        """Assign a course using a slot group"""
        group_slots = self.slot_groups.get(group_code, [])
        if not group_slots:
            return False
        
        # Check if all slots in the group are still available
        slot_codes = [slot['SlotCode'] for slot in group_slots]
        available_slots = self.slots[self.slots['SlotCode'].isin(slot_codes)]
        if len(available_slots) != len(group_slots):
            return False
        
        # Check for conflicts
        for slot in group_slots:
            if self._has_conflict(course, slot['Day'], slot):
                return False
        
        # Assign sessions without distinguishing between lecture/tutorial
        hours_assigned = 0
        for slot in group_slots:
            session_duration = min(slot['Duration'], total_hours - hours_assigned)
            self._place_session(course, slot['Day'], slot, 'Theory', session_duration)
            hours_assigned += session_duration
            
            if hours_assigned >= total_hours:
                break
        
        return hours_assigned == total_hours
    
    def _assign_lab_course(self, course):
        """Assign a lab course: 3-hour lab and then the theory part"""
        l, t, p = self.parse_ltp(course['L-T-P'])
        total_theory = l + t
        
        # First assign the lab (3-hour block)
        lab_assigned = False
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            available = self.slots[
                (self.slots['Day'] == day) &
                (self.slots['Duration'] == 3) &
                (self.slots['SlotType'] == 'Lab')
            ]
            for _, slot in available.iterrows():
                if self._has_conflict(course, day, slot):
                    continue
                self._place_session(course, day, slot, 'Lab', 3)
                lab_assigned = True
                break
            if lab_assigned:
                break
        
        # Then assign the theory part
        if total_theory > 0:
            # Try to assign with a group
            group_candidates = []
            for group_code, slots in self.slot_groups.items():
                total_duration = sum(slot['Duration'] for slot in slots)
                if total_duration >= total_theory:
                    group_candidates.append((group_code, total_duration))
            
            # Sort by closest match to total hours needed
            group_candidates.sort(key=lambda x: abs(x[1] - total_theory))
            
            for group_code, _ in group_candidates:
                if self._assign_with_group(course, group_code, total_theory):
                    return True
            
            # Fallback to individual assignment
            remaining = total_theory
            while remaining > 0:
                duration = 2 if remaining >= 2 else 1
                self._assign_sessions(course, 'Theory', 1, duration)
                remaining -= duration
        
        return True
    
    def _assign_theory_course(self, course):
        """Assign a theory course (no lab)"""
        l, t, p = self.parse_ltp(course['L-T-P'])
        total_hours = l + t
        
        # Try to assign with a group first
        group_candidates = []
        for group_code, slots in self.slot_groups.items():
            total_duration = sum(slot['Duration'] for slot in slots)
            if total_duration >= total_hours:
                group_candidates.append((group_code, total_duration))
        
        # Sort by closest match to total hours needed
        group_candidates.sort(key=lambda x: abs(x[1] - total_hours))
        
        for group_code, _ in group_candidates:
            if self._assign_with_group(course, group_code, total_hours):
                return True
        
        # Fallback to individual assignment
        remaining = total_hours
        while remaining > 0:
            duration = 2 if remaining >= 2 else 1
            self._assign_sessions(course, 'Theory', 1, duration)
            remaining -= duration
        
        return True
    
    
    def generate_schedule(self):
        # First, process lab courses
        lab_courses = self.courses[self.courses['Type'].str.lower() == 'lab']
        for _, course in lab_courses.iterrows():
            self._assign_lab_course(course)
        
        # Then, non-lab courses
        non_lab_courses = self.courses[self.courses['Type'].str.lower() != 'lab']
        for _, course in non_lab_courses.iterrows():
            self._assign_theory_course(course)
        
        return self.schedule