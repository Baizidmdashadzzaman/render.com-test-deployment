from datetime import datetime

students = [
    {"id": 213008, "name": "BAIZID KAMRUZZAMAN"},
    {"id": 213009, "name": "MR ROHIM"},
    {"id": 213010, "name": "SHOHAG MIA"},
]

semesters = [
    {"id": 1, "name": "Spring 2025"},
    {"id": 2, "name": "Autumn 2025"},
]

subjects = [
    {"id": 1, "code": "CSE101", "name": "Introduction to Programming"},
    {"id": 2, "code": "MAT101", "name": "Calculus I"},
    {"id": 3, "code": "PHY101", "name": "Physics I"},
    {"id": 4, "code": "CSE201", "name": "Data Structures"},
    {"id": 5, "code": "MAT201", "name": "Linear Algebra"},
]

registrations = [
    {"student_id": 213008, "semester_id": 1},
    {"student_id": 213009, "semester_id": 1},
    {"student_id": 213010, "semester_id": 2},
]

enrollments = [
    {"student_id": 213008, "semester_id": 1, "subject_ids": [1, 2, 3]},
    {"student_id": 213009, "semester_id": 1, "subject_ids": [2, 3]},
    {"student_id": 213010, "semester_id": 2, "subject_ids": [4, 5]},
]


exam_routines = [
    {"semester_id": 1, "subject_id": 1, "date": "2025-05-10"},
    {"semester_id": 1, "subject_id": 2, "date": "2025-05-12"},
    {"semester_id": 1, "subject_id": 3, "date": "2025-05-14"},
    {"semester_id": 2, "subject_id": 4, "date": "2025-06-01"},
    {"semester_id": 2, "subject_id": 5, "date": "2025-06-03"},
]

def get_student_info(student_id):
    student = next((s for s in students if s["id"] == int(student_id)), None)
    if not student:
        return "Student not found"

    return f" ID:{student['id']} - Name:{student['name']}"


def get_all_students_with_semester():
    student_semester_info = []
    for reg in registrations:
        student = next(s for s in students if s["id"] == reg["student_id"])
        semester = next(sem for sem in semesters if sem["id"] == reg["semester_id"])
        student_semester_info.append({
            "student_id": student["id"],
            "student_name": student["name"],
            "semester_name": semester["name"]
        })
    return student_semester_info

def get_date_wise_exam_routine_flask():
    subject_lookup = {subj["id"]: subj for subj in subjects}

    date_map = {}

    for exam in exam_routines:
        subject_id = exam["subject_id"]
        exam_date = datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y")
        subject = subject_lookup[subject_id]

        if exam_date not in date_map:
            date_map[exam_date] = []

        date_map[exam_date].append({
            "subject_code": subject["code"],
            "subject_name": subject["name"]
        })

    result = []
    for date in sorted(date_map):
        date_entry = {"date": date, "exams": []}
        for entry in date_map[date]:
            date_entry["exams"].append({
                "subject_code": entry["subject_code"],
                "subject_name": entry["subject_name"]
            })
        result.append(date_entry)

    return result


def get_all_students_subjects_with_exam_dates_flask():
    result = []

    for student in students:
        student_id = student["id"]
        enrollment = next((e for e in enrollments if e["student_id"] == student_id), None)
        if not enrollment:
            continue

        semester_id = enrollment["semester_id"]
        subject_ids = enrollment["subject_ids"]

        subjects_with_dates = []
        for subject_id in subject_ids:
            subject = next((s for s in subjects if s["id"] == subject_id), None)
            exam = next((e for e in exam_routines if e["semester_id"] == semester_id and e["subject_id"] == subject_id), None)
            if subject and exam:
                subjects_with_dates.append({
                    "subject_name": subject["name"],
                    "subject_code": subject["code"],
                    "exam_date": datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y")
                })

        result.append({
            "student_id": student_id,
            "student_name": student["name"],
            "semester": semester_id,
            "subjects": subjects_with_dates
        })

    return result

def display_data():
    print("Students:")
    for s in students:
        print(f"  ID: {s['id']}, Name: {s['name']}")

    print("\nSemesters:")
    for sem in semesters:
        print(f"  ID: {sem['id']}, Name: {sem['name']}")

    print("\nSubjects:")
    for subj in subjects:
        print(f"  ID: {subj['id']}, Code: {subj['code']}, Name: {subj['name']}")

    print("\nEnrollments:")
    for e in enrollments:
        student_name = next(s["name"] for s in students if s["id"] == e["student_id"])
        semester_name = next(sem["name"] for sem in semesters if sem["id"] == e["semester_id"])
        subject_names = [sub["name"] for sub in subjects if sub["id"] in e["subject_ids"]]
        print(f"  {student_name} -> {semester_name}: {', '.join(subject_names)}")

def get_student_exam_routine(student_id):
    student = next(s for s in students if s["id"] == student_id)
    enrollment = next(e for e in enrollments if e["student_id"] == student_id)
    semester_id = enrollment["semester_id"]
    subject_ids = enrollment["subject_ids"]

    routine = []
    for exam in exam_routines:
        if exam["semester_id"] == semester_id and exam["subject_id"] in subject_ids:
            subject = next(s for s in subjects if s["id"] == exam["subject_id"])
            routine.append({
                "subject": subject["name"],
                "code": subject["code"],
                "date": datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y")
            })

    routine.sort(key=lambda x: x["date"])  
    return {"student": student["name"], "semester": semester_id, "routine": routine}

def display_all_routines():
    print("Student Exam Routines:\n")
    for student in students:
        info = get_student_exam_routine(student["id"])
        print(f"Student: {info['student']}")
        for r in info["routine"]:
            print(f"  {r['date']} - {r['code']}: {r['subject']}")
        print("")


def display_date_wise_exam_routine():
    print("Date-wise Exam Routine:\n")

    subject_lookup = {subj["id"]: subj for subj in subjects}
    student_lookup = {s["id"]: s["name"] for s in students}
    enrollment_lookup = {
        (e["student_id"], e["semester_id"]): e["subject_ids"]
        for e in enrollments
    }

    date_map = {}

    for exam in exam_routines:
        subject_id = exam["subject_id"]
        semester_id = exam["semester_id"]
        exam_date = datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y")
        subject = subject_lookup[subject_id]

        if exam_date not in date_map:
            date_map[exam_date] = []

        students_in_exam = [
            student_lookup[student_id]
            for student_id, sem_id in enrollment_lookup.keys()
            if sem_id == semester_id and subject_id in enrollment_lookup[(student_id, sem_id)]
        ]

        date_map[exam_date].append({
            "subject_code": subject["code"],
            "subject_name": subject["name"],
            "students": students_in_exam
        })


    for date in sorted(date_map):
        print(f"Date: {date}")
        for entry in date_map[date]:
            print(f"  {entry['subject_code']} - {entry['subject_name']}")
            print(f"    Students: {', '.join(entry['students'])}")
        print("")



def get_exam_by_date_for_student(date_str, student_id):
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%b-%Y")
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    enrollment = next((e for e in enrollments if e["student_id"] == student_id), None)
    if not enrollment:
        print("Student not found or not enrolled.")
        return

    semester_id = enrollment["semester_id"]
    subject_ids = enrollment["subject_ids"]

    exams_today = [
        exam for exam in exam_routines
        if exam["semester_id"] == semester_id and
           exam["subject_id"] in subject_ids and
           datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y") == input_date
    ]

    student_name = next((s["name"] for s in students if s["id"] == student_id), "Unknown")

    print(f"\nExam schedule for {student_name} on {input_date}:")
    if not exams_today:
        print("  No exam scheduled.")
        return "  No exam scheduled."
    else:
        for exam in exams_today:
            subject = next(s for s in subjects if s["id"] == exam["subject_id"])
            print(f"  {subject['code']} - {subject['name']}")
            return f"  {subject['code']} - {subject['name']}"
        


def get_exam_by_date_for_student_flask(date_str, student_id):
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%b-%Y")
    except ValueError:
        #print("Invalid date format. Use YYYY-MM-DD.")
        return "Invalid date format. Use YYYY-MM-DD."

    enrollment = next((e for e in enrollments if e["student_id"] == int(student_id)), None)
    if not enrollment:
        #print("Student not found or not enrolled.")
        return "Student not found or not enrolled."

    semester_id = enrollment["semester_id"]
    subject_ids = enrollment["subject_ids"]

    exams_today = [
        exam for exam in exam_routines
        if exam["semester_id"] == semester_id and
           exam["subject_id"] in subject_ids and
           datetime.strptime(exam["date"], "%Y-%m-%d").strftime("%d-%b-%Y") == input_date
    ]

    student_name = next((s["name"] for s in students if s["id"] == int(student_id)), "Unknown")
    result_lines = [f"Exam schedule for {student_name} on {input_date}:"]
    
    if not exams_today:
        result_lines.append("  No exam scheduled.")
    else:
        for exam in exams_today:
            subject = next(s for s in subjects if s["id"] == exam["subject_id"])
            result_lines.append(f"  {subject['code']} - {subject['name']}")

    return "\n".join(result_lines)

