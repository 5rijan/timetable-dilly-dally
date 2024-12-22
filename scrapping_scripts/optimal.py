from typing import Dict, List, Set
from collections import defaultdict

class TimetableOptimizer:
    def __init__(self, data: dict):
        self.data = data
        self.subjects = data['subjects']
        self.optimization = data['optimization']
        
    def time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes since midnight"""
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

    def get_subject_activities(self) -> Dict[str, Dict[str, List[dict]]]:
        """
        Returns a nested dictionary:
        subject_code -> activity_group_code -> list of activities
        This ensures we group all activities by their subject and group codes
        """
        subject_activities = defaultdict(lambda: defaultdict(list))
        
        for subject in self.subjects:
            subject_code = subject['subject_code']
            for activity in subject['activities'].values():
                group_code = activity['activity_group_code']
                subject_activities[subject_code][group_code].append(activity)
                
        return subject_activities

    def score_avoid_days(self, activity: dict) -> float:
        """Score how well an activity matches the avoid days preference"""
        avoid_days = [day.lower()[:3] for day in self.optimization['avoidDays']]
        activity_day = activity['day_of_week'].lower()[:3]
        return 0.0 if activity_day in avoid_days else 1.0

    def score_time_restrictions(self, activity: dict) -> float:
        """Score how well an activity fits within time restrictions"""
        start_time = self.time_to_minutes(activity['start_time'])
        duration = int(activity['duration'])
        end_time = start_time + duration
        
        allowed_start = self.optimization['timeRestrictions']['start'] * 60
        allowed_end = self.optimization['timeRestrictions']['end'] * 60
        
        # Calculate how much the activity deviates from allowed times
        start_deviation = max(0, allowed_start - start_time) + max(0, start_time - allowed_end)
        end_deviation = max(0, allowed_start - end_time) + max(0, end_time - allowed_end)
        
        total_deviation = start_deviation + end_deviation
        max_possible_deviation = 24 * 60  # Maximum possible deviation in minutes
        
        return 1.0 - (total_deviation / max_possible_deviation)

    def check_clash(self, activity1: dict, activity2: dict) -> bool:
        """Check if two activities clash"""
        if activity1['day_of_week'] != activity2['day_of_week']:
            return False
            
        start1 = self.time_to_minutes(activity1['start_time'])
        end1 = start1 + int(activity1['duration'])
        start2 = self.time_to_minutes(activity2['start_time'])
        end2 = start2 + int(activity2['duration'])
        
        return not (end1 <= start2 or end2 <= start1)

    def score_activity_combination(self, activities: List[dict]) -> float:
        """Score a combination of activities based on all preferences"""
        if not activities:
            return float('-inf')
            
        # Score weights (in order of priority)
        AVOID_DAYS_WEIGHT = 0.5
        TIME_RESTRICT_WEIGHT = 0.3
        CLASH_WEIGHT = 0.2
        
        # Calculate avoid days score
        avoid_days_score = sum(self.score_avoid_days(activity) for activity in activities) / len(activities)
        
        # Calculate time restrictions score
        time_score = sum(self.score_time_restrictions(activity) for activity in activities) / len(activities)
        
        # Calculate clash score
        clash_count = 0
        total_possible_clashes = (len(activities) * (len(activities) - 1)) / 2
        if total_possible_clashes > 0:
            for i in range(len(activities)):
                for j in range(i + 1, len(activities)):
                    if self.check_clash(activities[i], activities[j]):
                        clash_count += 1
            clash_score = 1.0 - (clash_count / total_possible_clashes)
        else:
            clash_score = 1.0

        # Weighted average of scores
        total_score = (AVOID_DAYS_WEIGHT * avoid_days_score +
                      TIME_RESTRICT_WEIGHT * time_score +
                      CLASH_WEIGHT * clash_score)
                      
        return total_score

    def optimize_timetable(self) -> List[dict]:
        subject_activities = self.get_subject_activities()
        best_combination = []
        best_score = float('-inf')
        
        def try_subject_combinations(subject_codes: List[str], current_idx: int, current_selection: List[dict]):
            nonlocal best_combination, best_score
            
            # Base case: we've processed all subjects
            if current_idx == len(subject_codes):
                score = self.score_activity_combination(current_selection)
                if score > best_score:
                    best_score = score
                    best_combination = current_selection.copy()
                return
            
            # Get current subject and its activity groups
            subject_code = subject_codes[current_idx]
            activity_groups = subject_activities[subject_code]
            
            # Try all possible combinations of activities for this subject's groups
            def try_group_combinations(group_codes: List[str], group_idx: int, subject_selection: List[dict]):
                if group_idx == len(group_codes):
                    # We have a complete selection for this subject, move to next subject
                    combined_selection = current_selection + subject_selection
                    try_subject_combinations(subject_codes, current_idx + 1, combined_selection)
                    return
                
                # Get current group and try each activity in it
                group_code = group_codes[group_idx]
                activities = activity_groups[group_code]
                
                # Must select exactly one activity from this group
                for activity in activities:
                    subject_selection.append(activity)
                    try_group_combinations(group_codes, group_idx + 1, subject_selection)
                    subject_selection.pop()
            
            # Start combinations for this subject's groups
            group_codes = list(activity_groups.keys())
            try_group_combinations(group_codes, 0, [])
        
        # Start the optimization process
        subject_codes = list(subject_activities.keys())
        try_subject_combinations(subject_codes, 0, [])
        
        return best_combination

    def format_output(self, selected_activities: List[dict]) -> List[str]:
        output = []
        for activity in selected_activities:
            formatted = (f"{activity['subject_code']} | "
                       f"{activity['activity_group_code']} | "
                       f"Activity {activity['activity_code']} | "
                       f"{activity['day_of_week']} {activity['start_time']} "
                       f"({activity['duration']} mins)")
            output.append(formatted)
        return sorted(output)

def optimize_timetable(input_data: dict) -> List[str]:
    optimizer = TimetableOptimizer(input_data)
    selected_activities = optimizer.optimize_timetable()
    return optimizer.format_output(selected_activities)

if __name__ == "__main__":
    sample_input ={'subjects': [{'activities': {'INTS3003-S1C-ND-CC|Lecture|01': {'activitiesDays': ['27/2/2025', '6/3/2025', '13/3/2025', '20/3/2025', '27/3/2025', '3/4/2025', '10/4/2025', '17/4/2025', '1/5/2025', '8/5/2025', '15/5/2025', '22/5/2025', '29/5/2025'], 'activity_code': '01', 'activity_group_code': 'Lecture', 'activity_type': 'Lecture', 'availability': 60, 'campus': 'Camperdown/Darlington, Sydney', 'cluster': '', 'color': '#e5e5e5', 'day_of_week': 'Thu', 'department': 'SLC Administration', 'description': 'Lecture', 'duration': '120', 'location': 'F11.02.236.Chemistry Building.Chemistry Lecture Theatre 4', 'selectable': 'available', 'semester': 'S1C', 'semester_description': 'Semester 1', 'staff': '-', 'start_date': '30/12/2024', 'start_time': '09:00', 'subject_code': 'INTS3003-S1C-ND-CC', 'week_pattern': '0000000011111111011111000000000000000000000000000000', 'zone': 'CC - Camperdown/Darlington'}, 'INTS3003-S1C-ND-CC|Tutorial|01': {'activitiesDays': ['28/2/2025', '7/3/2025', '14/3/2025', '21/3/2025', '28/3/2025', '4/4/2025', '11/4/2025', '2/5/2025', '9/5/2025', '16/5/2025', '23/5/2025', '30/5/2025'], 'activity_code': '01', 'activity_group_code': 'Tutorial', 'activity_type': 'Tutorial', 'availability': 30, 'campus': 'Camperdown/Darlington, Sydney', 'cluster': '', 'color': '#70dcf0', 'day_of_week': 'Fri', 'department': 'SLC Administration', 'description': 'Tutorial', 'duration': '60', 'location': 'D17.01.1101.Charles Perkins Centre.CPC Seminar Room 1.2', 'selectable': 'available', 'semester': 'S1C', 'semester_description': 'Semester 1', 'staff': '-', 'start_date': '30/12/2024', 'start_time': '12:00', 'subject_code': 'INTS3003-S1C-ND-CC', 'week_pattern': '0000000011111110011111000000000000000000000000000000', 'zone': 'CC - Camperdown/Darlington'}}, 'activity_count': 2, 'callista_code': 'INTS3003', 'campus': 'CC', 'children': [{'code': 'INGS3602-S1C-ND-CC', 'description': 'Social Movements in the Global South'}], 'description': 'Southern Social Movements and Theories', 'email_address': 'vek.lewis@sydney.edu.au', 'faculty': 'ARTS', 'manager': 'PAUL LEWIS', 'semester': 'S1C', 'show_on_timetable': 89, 'subject_code': 'INTS3003-S1C-ND-CC'}, {'activities': {'BMET5995-S1C-ND-CC|Lecture|01': {'activitiesDays': ['24/2/2025', '3/3/2025', '10/3/2025', '17/3/2025', '24/3/2025', '31/3/2025', '7/4/2025', '14/4/2025', '28/4/2025', '5/5/2025', '12/5/2025', '19/5/2025', '26/5/2025'], 'activity_code': '01', 'activity_group_code': 'Lecture', 'activity_type': 'Lecture', 'availability': 60, 'campus': 'Camperdown/Darlington, Sydney', 'cluster': '', 'color': '#e5e5e5', 'day_of_week': 'Mon', 'department': 'Biomedical Engineering', 'description': 'Lecture', 'duration': '120', 'location': 'J02.03.304.PNR Building.PNR Lecture Theatre (1) 304 (Farrell)', 'selectable': 'available', 'semester': 'S1C', 'semester_description': 'Semester 1', 'staff': '-', 'start_date': '30/12/2024', 'start_time': '14:00', 'subject_code': 'BMET5995-S1C-ND-CC', 'week_pattern': '0000000011111111011111000000000000000000000000000000', 'zone': 'CC - Camperdown/Darlington'}, 'BMET5995-S1C-ND-CC|Practical|02': {'activitiesDays': ['5/3/2025', '12/3/2025', '19/3/2025', '26/3/2025', '2/4/2025', '9/4/2025', '16/4/2025', '30/4/2025', '7/5/2025', '14/5/2025', '21/5/2025', '28/5/2025'], 'activity_code': '02', 'activity_group_code': 'Practical', 'activity_type': 'Practical', 'availability': 30, 'campus': 'Camperdown/Darlington, Sydney', 'cluster': '', 'color': '#9adf66', 'day_of_week': 'Wed', 'department': 'Biomedical Engineering', 'description': 'Practical - Dry Lab', 'duration': '180', 'location': 'J03.04.461.DRY60.A1-VR.Electrical Engineering Building.461.Electrical Engineering Building.Electrical Eng Dry Lab 461', 'selectable': 'available', 'semester': 'S1C', 'semester_description': 'Semester 1', 'staff': '-', 'start_date': '30/12/2024', 'start_time': '09:30', 'subject_code': 'BMET5995-S1C-ND-CC', 'week_pattern': '0000000001111111011111000000000000000000000000000000', 'zone': 'CC - Camperdown/Darlington'}, 'BMET5995-S1C-ND-CC|Practical|03': {'activitiesDays': ['5/3/2025', '12/3/2025', '19/3/2025', '26/3/2025', '2/4/2025', '9/4/2025', '16/4/2025', '30/4/2025', '7/5/2025', '14/5/2025', '21/5/2025', '28/5/2025'], 'activity_code': '03', 'activity_group_code': 'Practical', 'activity_type': 'Practical', 'availability': 30, 'campus': 'Camperdown/Darlington, Sydney', 'cluster': '', 'color': '#9adf66', 'day_of_week': 'Wed', 'department': 'Biomedical Engineering', 'description': 'Practical - Dry Lab', 'duration': '180', 'location': 'J03.04.461.DRY60.A1-VR.Electrical Engineering Building.461.Electrical Engineering Building.Electrical Eng Dry Lab 461', 'selectable': 'available', 'semester': 'S1C', 'semester_description': 'Semester 1', 'staff': '-', 'start_date': '30/12/2024', 'start_time': '13:30', 'subject_code': 'BMET5995-S1C-ND-CC', 'week_pattern': '0000000001111111011111000000000000000000000000000000', 'zone': 'CC - Camperdown/Darlington'}}, 'activity_count': 3, 'callista_code': 'BMET5995', 'campus': 'CC', 'children': [], 'description': 'Advanced Bionics', 'email_address': 'gregg.suaning@sydney.edu.au', 'faculty': 'ENGI', 'manager': 'GREGG SUANING', 'semester': 'S1C', 'show_on_timetable': 89, 'subject_code': 'BMET5995-S1C-ND-CC'}], 'optimization': {'timeRestrictions': {'start': 6, 'end': 18}, 'avoidDays': ['tue', 'thu'], 'preferences': {'minimizeClashes': True, 'clashLectures': False, 'crampClasses': False, 'allocateBreaks': True, 'spreadClasses': True}}}
    result = optimize_timetable(sample_input)
    for line in result:
        print(line)