from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector

 
 
app = Flask(__name__)
app.secret_key = '08112003'
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="manager-student",
    charset='utf8mb4'
)

cursor = conn.cursor()



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email:
            return render_template("login.html", error_message="Vui lòng nhập email")
        
        # Kiểm tra email trong bảng admin
        cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
        admin = cursor.fetchone()
        
        if admin:
            if admin[2] == password:  # Giả sử cột mật khẩu là cột thứ 3 (index 2)
                session["username"] = admin[1]  # Lưu tên người dùng vào session
                return redirect('/')
            else:
                return render_template("login.html", error_message="Sai mật khẩu")
        
        # Kiểm tra email trong bảng teacher
        cursor.execute("SELECT * FROM teacher WHERE email=%s", (email,))
        teacher = cursor.fetchone()
             
        if teacher:
            if teacher[1] == password:  # Giả sử cột ngày sinh là cột thứ 2 (index 1)
                session["username"] = teacher[2]  # Lưu tên người dùng vào session
                return redirect('/main_teacher')
            else:
                return render_template("login.html", error_message="Sai mật khẩu (ngày sinh)")
        
        # Kiểm tra email trong bảng student
        cursor.execute("SELECT * FROM student WHERE email=%s", (email,))
        student = cursor.fetchone()
        
        if student:
            if str(student[1]) == password:  # Giả sử cột student_code là cột thứ 2 (index 1)
                session["username"] = student[2]  # Lưu tên người dùng vào session
                return redirect('/main_student')
            else:
                return render_template("login.html", error_message="Sai mật khẩu (mã sinh viên)")
        
        # Nếu email không tồn tại trong bất kỳ bảng nào
        return render_template("login.html", error_message="Email không đúng")
    
    return render_template('login.html')


@app.route('/')
def admin():
    if not session.get("username"):
        print("No username in session, redirecting to login")
        return redirect("/login")
    print(f"User logged in with username: {session['username']}")
    return render_template('main.html')
@app.route('/main_student')
def admin_student():
    if not session.get("username"):
        print("No username in session, redirecting to login")
        return redirect("/login")
    print(f"User logged in with username: {session['username']}")
    return render_template('main_student.html')
@app.route('/main_teacher')
def admin_teacher():
    if not session.get("username"):
        print("No username in session, redirecting to login")
        return redirect("/login")
    print(f"User logged in with username: {session['username']}")
    return render_template('main_teacher.html')


@app.route('/sigin', methods=['GET', 'POST'])
def sigin():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        cursor.execute("SELECT * FROM admin WHERE username=%s", (username,))
        existing_admin = cursor.fetchone()
        if existing_admin:
            return render_template("sigin.html", error_message="Đăng ký thất bại, tên đăng nhập đã tồn tại")
        else:
            cursor.execute("INSERT INTO admin (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
            conn.commit()
            return redirect('/login')
    return render_template("sigin.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/home')
def home():
    username = session.get('username')
    if not username:
        return redirect('/login')
    
    return render_template('home.html', username=username)


@app.route('/teacher')
def teacher():
    cursor.execute("SELECT * FROM teacher")
    teachers = cursor.fetchall()  # Change variable name from teacher to teachers
    return render_template('teacher.html', teachers=teachers)  # Change variable name from teacher to teachers

@app.route('/add_teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        teacher_code = request.form['teacher_code']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        degree = request.form['degree']
        nationality = request.form['nationality']
        department = request.form['department']
        class_name = request.form['class_name']
        date_of_birth = request.form['date_of_birth']
        
        cursor.execute("SELECT * FROM teacher WHERE teacher_code=%s", (teacher_code,))
        existing_teacher = cursor.fetchone()
        if existing_teacher:
            return "Giáo viên đã tồn tại!"
        else:
            cursor.execute("INSERT INTO teacher (teacher_code, name, email, phone, degree, nationality, department, class_name, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (teacher_code, name, email, phone, degree, nationality, department, class_name, date_of_birth))
            conn.commit()
            return redirect('/teacher')
    return render_template('add_teacher.html')

 

@app.route('/update_teacher/<id>', methods=[ 'POST' ,'GET'])
def edit_teacher(id):
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        degree = request.form.get('degree')
        nationality = request.form.get('nationality')
        department = request.form.get('department')
        class_name = request.form.get('class_name')
        date_of_birth = request.form.get('date_of_birth')
        
        cursor.execute("SELECT teacher_code FROM teacher WHERE id = %s", (id,))
        old_teacher_code = cursor.fetchone()[0]

        new_teacher_code = request.form.get('teacher_code')



        if new_teacher_code and new_teacher_code != old_teacher_code:
            cursor.execute("SELECT * FROM teacher WHERE teacher_code = %s AND id != %s", (new_teacher_code, id))
            new_teacher = cursor.fetchone()
            if new_teacher:
                # Nếu mã giảng viên mới đã tồn tại cho một giảng viên khác, thông báo lỗi
                cursor.execute("SELECT * FROM Teacher WHERE id = %s", (id,))
                teacher = cursor.fetchone()
                return render_template("update_teacher.html", error="Teacher code already exists!", teacher=teacher)

        # Thực hiện cập nhật dữ liệu nếu mã giảng viên không bị trùng
        cursor.execute('''
            UPDATE Teacher
            SET teacher_code=%s, name=%s, email=%s, phone=%s, degree=%s, nationality=%s, department=%s, class_name=%s,
                date_of_birth=%s
            WHERE id=%s
        ''', (new_teacher_code if new_teacher_code else old_teacher_code, name, email, phone, degree, nationality, 
              department, class_name, date_of_birth, id))
        conn.commit()

        # Chuyển hướng về trang danh sách giảng viên
        return redirect('/teacher')

    # Nếu là GET request, lấy thông tin giảng viên hiện tại để hiển thị trong form
    cursor.execute("SELECT * FROM teacher WHERE id = %s", (id,))
    teacher = cursor.fetchone()
    if not teacher:
        return redirect('/teacher')  # Hoặc bạn có thể hiển thị trang lỗi

    return render_template("update_teacher.html", teacher=teacher)


# Xóa giáo viên
@app.route('/delete_teacher/<teacher_code>', methods=['POST', 'GET'])
def delete_teacher(teacher_code):
    cursor.execute("DELETE FROM teacher WHERE teacher_code = %s", (teacher_code,))
    conn.commit()
    return redirect("/teacher")


@app.route('/students')
def students():
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()
    return render_template('students.html', students=students)

@app.route('/add_students', methods=['GET', 'POST'])
def add_students():
    if request.method == 'POST':
        student_code = request.form.get('student_code')
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        faculty_name = request.form.get('faculty_name')
        birth = request.form.get('birth')
        email = request.form.get('email')
        hometown = request.form.get('hometown')
        phone = request.form.get('phone')
        id_card = request.form.get('id_card')
        ethnicity = request.form.get('ethnicity')
        religion = request.form.get('religion')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        father_phone = request.form.get('father_phone')
        mother_phone = request.form.get('mother_phone')
        father_occupation = request.form.get('father_occupation')
        mother_occupation = request.form.get('mother_occupation')

        cursor.execute("SELECT * FROM Student WHERE student_code = %s", (student_code,))
        existing_student = cursor.fetchall()

        if existing_student:
            return render_template("add_students.html", error_message="Student code already exists!")
        else:
            cursor.execute(
                """
                INSERT INTO Student (student_code, name, class_name, faculty_name,eamil, birth, hometown, phone, id_card, ethnicity, religion, father_name, mother_name, father_phone, mother_phone, father_occupation, mother_occupation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                """,
                (student_code, name, class_name, faculty_name, birth,email, hometown, phone, id_card, ethnicity, religion, father_name, mother_name, father_phone, mother_phone, father_occupation, mother_occupation)
            )
            conn.commit()
            return redirect('/students')
    return render_template("add_students.html")


@app.route('/update_student/<student_code>', methods=['GET', 'POST'])
def edit_student(student_code):
    if request.method == 'POST':
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        faculty_name = request.form.get('faculty_name')
        birth = request.form.get('birth')
        hometown = request.form.get('hometown')
        phone = request.form.get('phone')
        email = request.form.get('email')
        id_card = request.form.get('id_card')
        ethnicity = request.form.get('ethnicity')
        religion = request.form.get('religion')
        father_name = request.form.get('father_name')
        mother_name = request.form.get('mother_name')
        father_phone = request.form.get('father_phone')
        mother_phone = request.form.get('mother_phone')
        father_occupation = request.form.get('father_occupation')
        mother_occupation = request.form.get('mother_occupation')

        # Kiểm tra xem mã sinh viên mới có bị trùng không
        new_student_code = request.form.get('student_code')
        if new_student_code and new_student_code != student_code:
            cursor.execute("SELECT * FROM Student WHERE student_code = %s", (new_student_code,))
            new_student = cursor.fetchone()
            if new_student:
                # Nếu mã sinh viên mới đã tồn tại, thông báo lỗi
                cursor.execute("SELECT * FROM Student WHERE student_code = %s", (student_code,))
                student = cursor.fetchone()
                return render_template("update_student.html", error="Student code already exists!", student=student)

        # Thực hiện cập nhật dữ liệu nếu mã sinh viên không bị trùng
        cursor.execute('''
            UPDATE Student
            SET student_code=%s, name=%s, class_name=%s, faculty_name=%s, birth=%s, email=%s, hometown=%s, phone=%s,
                id_card=%s, ethnicity=%s, religion=%s, father_name=%s, mother_name=%s, father_phone=%s, 
                mother_phone=%s, father_occupation=%s, mother_occupation=%s
            WHERE student_code=%s
        ''', (new_student_code if new_student_code else student_code, name, class_name, faculty_name, birth, email, 
              hometown, phone, id_card, ethnicity, religion, father_name, mother_name, father_phone, mother_phone, 
              father_occupation, mother_occupation, student_code))
        conn.commit()


        return redirect('/students')


    cursor.execute("SELECT * FROM Student WHERE student_code = %s", (student_code,))
    student = cursor.fetchone()
    if not student:
        return redirect('/students')  # Hoặc bạn có thể hiển thị trang lỗi

    return render_template("update_student.html", student=student)



@app.route('/delete_student/<student_code>', methods=['POST', 'GET'])
def delete_student(student_code):
    cursor.execute("DELETE FROM Student WHERE student_code = %s", (student_code,))
    conn.commit()
    return redirect("/students")



@app.route('/score')
def score():
    # Lấy danh sách điểm từ database để hiển thị
    cursor.execute("SELECT * FROM grade")
    grades = cursor.fetchall()
    return render_template('score.html', grades=grades)

# Route để thêm điểm
@app.route('/add_score', methods=['GET', 'POST'])
def add_score():
    if request.method == 'POST':
        print(request.form)  # Add this line to print the form data to the console
        student_code = request.form['student_code']
        student_name = request.form['student_name']
        subject_name = request.form['subject_name']
        score_b = float(request.form['score_b'])
        score_c = float(request.form['score_c'])
        grade = float(request.form['grade'])
        

        gpa = (score_b + score_c + grade) / 3

        cursor.execute("INSERT INTO grade (student_code, student_name, subject_name, score_b, score_c, grade, gpa) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                       (student_code, student_name, subject_name, score_b, score_c, grade, gpa))
        conn.commit()

        return redirect('/score')
    return render_template('add_score.html')

# Route để cập nhật điểm dựa trên ID
@app.route('/update_score/<int:id>', methods=['POST', 'GET'])
def update_score(id):
    if request.method == 'POST':
        new_student_code = request.form['student_code']
        new_student_name = request.form['student_name']
        new_subject_name = request.form['subject_name']
        new_score_b = float(request.form['score_b'])
        new_score_c = float(request.form['score_c'])
        new_grade = float(request.form['grade'])
        
        
        gpa = (new_score_b + new_score_c + new_grade) / 3

        cursor.execute("UPDATE grade SET student_code=%s, student_name=%s, subject_name=%s, score_b=%s, score_c=%s, grade=%s, gpa=%s WHERE id=%s", 
                       (new_student_code, new_student_name, new_subject_name, new_score_b, new_score_c, new_grade, gpa, id))
        conn.commit()

        return redirect('/score')
    
    # Fetch the current grade data from the database for GET request
    cursor.execute("SELECT * FROM grade WHERE id = %s", (id,))
    grade = cursor.fetchone()
    return render_template('update_score.html', grade=grade)


# Route để xóa điểm dựa trên ID (Placeholder for your delete route)
@app.route('/delete_score/<int:id>', methods=['POST'])
def delete_score(id):
    cursor.execute("DELETE FROM grade WHERE id = %s", (id,))
    conn.commit()
    return redirect('/score')



@app.route('/faculty')
def faculty():
    # Lấy danh sách faculty từ database
    cursor.execute("SELECT * FROM faculty")
    faculties = cursor.fetchall()
    return render_template('faculty.html', faculties=faculties)

# Route thêm faculty mới
@app.route('/add_faculty', methods=['POST' , 'GET'])
def add_faculty():
    if request.method == 'POST':
        faculty_code = request.form['faculty_code']
        faculty_name = request.form['faculty_name']
        
        # Kiểm tra xem faculty_code đã tồn tại chưa
        cursor.execute("SELECT * FROM faculty WHERE faculty_code = %s", (faculty_code,))
        existing_faculty = cursor.fetchone()
        
        if existing_faculty:
            # Nếu faculty_code đã tồn tại, hiển thị thông báo lỗi
            error_message = "Faculty code already exists. Please choose another one."
            return render_template('add_faculty.html', error_message=error_message)
        else:
            # Nếu không có, thực hiện INSERT vào database
            cursor.execute("INSERT INTO faculty (faculty_code, faculty_name) VALUES (%s, %s)", (faculty_code, faculty_name))
            conn.commit()
            return redirect('/faculty')
    return render_template('add_faculty.html')

# Route sửa thông tin faculty
@app.route('/update_faculty/<id>', methods=['POST', 'GET'])
def update_faculty(id):
    if request.method == 'POST':
        faculty_code = request.form['faculty_code']
        faculty_name = request.form['faculty_name']
        
        # Kiểm tra xem mã khoa mới có trùng không
        cursor.execute("SELECT * FROM faculty WHERE faculty_code = %s AND id != %s", (faculty_code, id))
        existing_faculty = cursor.fetchone()
        
        if existing_faculty:
            # Nếu mã khoa mới trùng với mã khoa khác, hiển thị thông báo lỗi
            error_message = "Faculty code already exists. Please choose another one."
            return render_template('update_faculty.html', error_message=error_message, faculty={'id': id, 'faculty_code': faculty_code, 'faculty_name': faculty_name})
        else:
            # Nếu không trùng, thực hiện UPDATE vào database
            cursor.execute("UPDATE faculty SET faculty_code=%s, faculty_name=%s WHERE id=%s", (faculty_code, faculty_name, id))
            conn.commit()
            return redirect('/faculty')
    cursor.execute("SELECT * FROM faculty WHERE id = %s", (id,))
    faculty = cursor.fetchone()
        
    return render_template('update_faculty.html', faculty=faculty)


# Route xóa faculty
@app.route('/delete_faculty/<int:id>', methods=['POST'])
def delete_faculty(id):
    cursor.execute("DELETE FROM faculty WHERE id = %s", (id,))
    conn.commit()
    return redirect('/faculty')

@app.route('/class', methods=['GET'])
def class_list():
    cursor.execute("SELECT * FROM class")
    classes = cursor.fetchall()
    return render_template('class.html', classes=classes)

@app.route('/add_class', methods=['POST', 'GET'])
def add_class():
    if request.method == 'POST':
        class_code = request.form['class_code']
        faculty_name = request.form['faculty_name']
        class_name = request.form['class_name']
        year = request.form['year']
        time = request.form['time']        
        cursor.execute("SELECT * FROM class WHERE class_code = %s", (class_code,))
        existing_class = cursor.fetchone()
        if existing_class:
            error = "Class code already exists."
            return render_template('class.html', error=error)
        
        cursor.execute("INSERT INTO class (class_code,faculty_name, class_name,year,time) VALUES (%s, %s,%s,%s,%s)", (class_code,faculty_name, class_name,year,time))
        conn.commit()
        
        return redirect('/class')
    return render_template('add_class.html')

@app.route('/update_class/<int:id>', methods=['POST', 'GET'])
def update_class(id):
    if request.method == 'POST':
        class_code = request.form['class_code']
        faculty_name = request.form['faculty_name']
        class_name = request.form['class_name']
        year = request.form['year']
        time = request.form['time'] 
        
        cursor.execute("SELECT * FROM class WHERE class_code = %s AND id != %s", (class_code, id))
        existing_class = cursor.fetchone()
        if existing_class:
            error = "Class code already exists."
            return render_template('update_class.html', error=error, class_data={'id': id, 'class_code': class_code, 'faculty_name':faculty_name, 'class_name': class_name, 'year':year, 'time':time})
        
        cursor.execute("UPDATE class SET class_code=%s,faculty_name=%s, class_name=%s, year=%s, time=%s WHERE id=%s", (class_code,faculty_name, class_name,year,time, id))
        conn.commit()
        
        return redirect('/class')
    
    cursor.execute("SELECT * FROM class WHERE id = %s", (id,))
    class_data = cursor.fetchone()
    return render_template('update_class.html', class_data=class_data)


# Route xóa lớp học
@app.route('/delete_class/<id>', methods=['POST'])
def delete_class(id):
    # Thực hiện DELETE từ database
    cursor.execute("DELETE FROM class WHERE id = %s", (id,))
    conn.commit()
    
    return redirect('/class')

@app.route('/subject', methods=['GET'])
def subject():
    cursor.execute("SELECT * FROM subject")
    subjects = cursor.fetchall()
    return render_template('subject.html', subjects= subjects)


@app.route('/add_subject', methods=['POST', 'GET'])
def add_subject():
    if request.method == 'POST':
        subject_code = request.form['subject_code']
        subject_name = request.form['subject_name']
        credits = request.form['credits']
        money = request.form['money'] 
        
        # Kiểm tra xem lớp học đã tồn tại hay chưa
        cursor.execute("SELECT * FROM subject WHERE subject_code = %s", (subject_code,))
        existing_subject = cursor.fetchone()
        if existing_subject:
            error = "Subject code already exists."
            return render_template('subject.html', error=error)
        
        # Thực hiện INSERT vào database
        cursor.execute("INSERT INTO subject (subject_code, subject_name,credits,money) VALUES (%s, %s, %s,%s)", (subject_code, subject_name,credits,money))
        conn.commit()
        
        return redirect('/subject')
    return render_template('add_subject.html')


@app.route('/update_subject/<int:id>', methods=['POST', 'GET'])
def update_subject(id):
    if request.method == 'POST':
        subject_code = request.form['subject_code']
        subject_name = request.form['subject_name']
        credits = request.form['credits']
        money = request.form['money'] 

        
        cursor.execute("SELECT * FROM subject WHERE subject_code = %s AND id != %s", (subject_code, id))
        existing_subject = cursor.fetchone()
        if existing_subject:
            error = "Mã môn đã tồn tại."
            return render_template('update_subject.html', error=error, subject={'id': id, 'subject_code': subject_code, 'subject_name': subject_name, 'credits': credits, 'money':money})

        # Cập nhật thông tin môn học trong cơ sở dữ liệu
        cursor.execute("UPDATE subject SET subject_code=%s, subject_name=%s, credits=%s, money=%s WHERE id=%s", (subject_code, subject_name, credits,money, id))
        conn.commit()

        return redirect('/subject')
    
    # Lấy dữ liệu môn học để hiển thị trong form
    cursor.execute("SELECT * FROM subject WHERE id = %s", (id,))
    subject = cursor.fetchone()
    return render_template('update_subject.html', subject=subject)
    


@app.route('/delete_subject/<int:id>', methods=['POST'])
def delete_subject(id):
    # Thực hiện DELETE từ database
    cursor.execute("DELETE FROM subject WHERE id = %s", (id,))
    conn.commit()
    
    return redirect('/subject')


@app.route('/timetable')  
def timetable():
    
    return render_template('timetable.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')



if __name__ == '__main__':
    app.run(debug=True)
