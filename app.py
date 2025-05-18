from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import pytesseract
from PIL import Image
import base64
from io import BytesIO
import re
import database_utils

app = Flask(__name__)


cap = cv2.VideoCapture(0)
detected_info = {"id": "", "name": "", "exam_date": "","check_admit_authenticity":""}

@app.route('/update-exam-date', methods=['POST'])
def update_exam_date():
    data = request.get_json()
    detected_info['exam_date'] = data.get('exam_date')
    return jsonify({'status': 'success', 'updated_date': detected_info['exam_date']})

@app.route('/detected-info')
def get_detected_info():
    return jsonify(detected_info)

def detect_and_display_text():
    global detected_info
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_resized = cv2.resize(frame, (640, 480))
        gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

        custom_config = r'--oem 3 --psm 6'
        data = pytesseract.image_to_data(gray,
                                         output_type=pytesseract.Output.DICT,
                                         config=custom_config)

        n_boxes = len(data['level'])
        for i in range(n_boxes):
            text = data['text'][i].strip()

            if "ID No" in text or "C21" in text:
                detected_info['id'] = text.split(":")[-1].strip()
                if detected_info['id']:
                    detected_info['name'] = database_utils.get_student_info(re.sub(r'\D', '', detected_info['id']))
                    if detected_info['exam_date']:
                        detected_info['check_admit_authenticity'] = database_utils.get_exam_by_date_for_student_flask(detected_info['exam_date'], re.sub(r'\D', '', detected_info['id']))

            # elif "Name" in text and "Father" not in text and "Mother" not in text or "BAI" in text:
            #     detected_info['name'] = text.split(":")[-1].strip()
    
            if text:
                x, y, w, h = (data['left'][i], data['top'][i],
                              data['width'][i], data['height'][i])

                overlay = frame_resized.copy()
                cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), -1)
                alpha = 0.4
                cv2.addWeighted(overlay, alpha, frame_resized, 1 - alpha, 0, frame_resized)
                cv2.rectangle(frame_resized, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.putText(frame_resized, text, (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        ret2, buffer = cv2.imencode('.jpg', frame_resized)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def extract_text_from_base64_image(base64_image):
    image_data = base64.b64decode(base64_image.split(',')[1])
    np_img = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return pytesseract.image_to_string(thresh)


def parse_student_info(text):
    print("=== LEFT OCR ===")
    print(text)
    info = {
        'session': None,
        'id': None,
        'registration_no': None,
        'name': None,
        'father_name': None,
        'mother_name': None,
        'section': None,
        'program': None,
        'validity': None,
        'print_date': None
    }

    m = re.search(r'Session\s*[:\s]*(\S+)', text)
    if m:
        info['session'] = m.group(1)

    m = re.search(r'ID\s*No\.?\s*[:>\s]*([A-Z€]?\s*\d{5,7})', text, re.IGNORECASE)
    if m:
        info['id'] = re.sub(r'\s+|€', '', m.group(1).replace('€', 'C').replace('>', 'C'))
    else:
        m2 = re.search(r'(\d{5,7})', text)
        if m2:
            info['id'] = m2.group(1)

    m = re.search(r'Registration\s*No\.?\s*[:\s]*(\S+)', text)
    if m:
        info['registration_no'] = m.group(1)

    m = re.search(r'Name\s*[:\s]*(.+)', text)
    if m:
        info['name'] = m.group(1).strip()

    m = re.search(r"Father's Name\s*[:\s]*(.+)", text)
    if m:
        info['father_name'] = m.group(1).strip()

    m = re.search(r"Mother's Name\s*[:\s]*(.+)", text)
    if m:
        info['mother_name'] = m.group(1).strip()

    m = re.search(r'Section\s*[:\s]*(\S+)', text)
    if m:
        info['section'] = m.group(1)

    m = re.search(r'Program\s*[:\s]*([\s\S]+?)\s+Validity', text)
    if m:
        info['program'] = m.group(1).strip()
    else:
        m2 = re.search(r'Program\s*[:\s]*(.+)', text)
        if m2:
            info['program'] = m2.group(1).strip()

    m = re.search(r'Validity\s*[:\s]*(.+)', text)
    if m:
        info['validity'] = m.group(1).strip()

    m = re.search(r'Print Date\s*[:\s]*(\S+)', text)
    if m:
        info['print_date'] = m.group(1)

    return info


def parse_courses(text):
    lines = text.split('\n')
    courses = []
    semester = None
    controller = None

    for line in lines:
        if 'Semester Enrolled' in line:
            match = re.search(r'Semester Enrolled[:\s]*([0-9]+)', line)
            semester = match.group(1) if match else None

        course_match = re.match(r'([A-Z]{3}-\d{4})\s+(.*)', line)
        if course_match:
            courses.append({
                'code': course_match.group(1),
                'name': course_match.group(2).strip()
            })

        if 'Controller of Examinations' in line:
            controller = lines[lines.index(line)-1].strip()

    return {
        'semester_enrolled': semester,
        'courses': courses,
        'controller_signature': controller
    }


def highlight_text_regions(base64_image):
    img_data = base64.b64decode(base64_image.split(',')[1])
    np_img = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    n = len(data['level'])
    for i in range(n):
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    _, buf = cv2.imencode('.jpg', img)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf).decode('utf-8')


@app.route('/scan', methods=['POST'])
def scan_admit_card():
    exam_date = request.form.get('exam_date')
    base64_image = request.form.get('admit_card_base64')

    image_data = base64.b64decode(base64_image.split(',')[1])
    np_img = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    id_card = None
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 100 and h > 100 and x < 300 and y < 300:
            id_card = image[y:y+h, x:x+w]
            break

    id_card_data_uri = crop_image_information = crop_image_information_1 = crop_image_information_2 = None
    student_info = course_info = {}

    if id_card is not None:
        _, buffer = cv2.imencode('.jpg', id_card)
        id_card_base64 = base64.b64encode(buffer).decode('utf-8')
        id_card_data_uri = 'data:image/jpeg;base64,' + id_card_base64

        id_card_img = cv2.imdecode(np.frombuffer(base64.b64decode(id_card_base64), np.uint8), cv2.IMREAD_COLOR)

        height, width, _ = id_card_img.shape
        y1, y2 = int(height * 0.17), int(height * 0.65)
        cropped = id_card_img[y1:y2, 0:width]

        _, crop_buffer = cv2.imencode('.jpg', cropped)
        crop_base64 = base64.b64encode(crop_buffer).decode('utf-8')
        crop_image_information = 'data:image/jpeg;base64,' + crop_base64

        h, w, _ = cropped.shape
        mid_x = w // 2
        crop_left = cropped[:, :mid_x]
        crop_right = cropped[:, mid_x:]

        _, buffer_left = cv2.imencode('.jpg', crop_left)
        crop_image_information_1 = 'data:image/jpeg;base64,' + base64.b64encode(buffer_left).decode('utf-8')

        _, buffer_right = cv2.imencode('.jpg', crop_right)
        crop_image_information_2 = 'data:image/jpeg;base64,' + base64.b64encode(buffer_right).decode('utf-8')

        text_left = extract_text_from_base64_image(crop_image_information_1)
        text_right = extract_text_from_base64_image(crop_image_information_2)

        student_info = parse_student_info(text_left)
        course_info = parse_courses(text_right)

        crop_image_information_1_highlighted = highlight_text_regions(crop_image_information_1)
        crop_image_information_2_highlighted = highlight_text_regions(crop_image_information_2)
         
        try:
            student_info['id'] = re.sub(r'\D', '', student_info['id'])
            exam_result_check = database_utils.get_exam_by_date_for_student_flask(exam_date, student_info['id'])
        except Exception as e:
            exam_result_check = "Unable to fetch exam result. Please try again."


    return render_template(
        'scan-result.html',
        image_data=base64_image,
        id_card_data_uri=id_card_data_uri,
        crop_image_information=crop_image_information,
        crop_image_information_1=crop_image_information_1,
        crop_image_information_2=crop_image_information_2,
        student_info=student_info,
        course_info=course_info,
        text_left=text_left,
        text_right=text_right,
        crop_image_information_1_highlighted=crop_image_information_1_highlighted,
        crop_image_information_2_highlighted=crop_image_information_2_highlighted,
        exam_result_check=exam_result_check,
    )



@app.route('/')
def home():
    detected_info.update({'id': "", 'name': "", 'exam_date': "", 'check_admit_authenticity': ""})

    students_db = database_utils.get_all_students_with_semester()
    exam_routines = database_utils.get_date_wise_exam_routine_flask()
    student_wise_exam_routines = database_utils.get_all_students_subjects_with_exam_dates_flask()

    return render_template(
        'index.html', 
        students_db=students_db,
        exam_routines=exam_routines,
        student_wise_exam_routines=student_wise_exam_routines,
    )


@app.route('/text-feed')
def text_feed():
    return Response(detect_and_display_text(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)