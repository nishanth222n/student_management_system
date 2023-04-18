from flask import *
import mysql.connector
from datetime import *

app = Flask(__name__)

# MySQL Configuration
mydb =  mysql.connector.connect(
     host="localhost",
  user="root",
  password="root",
  database="student"
)
app.debug = True


app.secret_key = 'mysecretkey' # set a secret key for session management


@app.route('/')
def home():
   if session.get('logged_in'):
        return redirect(url_for('index'))
   return render_template("home.html")

@app.route('/Home')
def index():
  if not session.get('logged_in'):
        return redirect(url_for('login'))
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # check if submitted username and password match
        if request.form['username'] == 'admin' and request.form['password'] == 'admin':
            # set the user's login status in the session
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            # show an error message if login failed
            error = 'Invalid username or password'
            return render_template('admin.html', error=error)
    else:
        return render_template('admin.html')



@app.route('/student', methods=['GET', 'POST'])
def addStudent():
   if session.get('logged_in'):
        if request.method == 'POST':
                name = request.form['name']
                email = request.form['email']
                address = request.form['address']
                contact_number = request.form['contact_number']
                course_details = request.form['course_details']
                
                # Insert data into MySQL database
                cursor = mydb.cursor()
                sql = "INSERT INTO students (name, email, address, contact_number, course_details) VALUES (%s, %s, %s, %s, %s)"
                values = (name, email, address, contact_number, course_details)
                cursor.execute(sql, values)
                mydb.commit()
                cursor.close()

                return redirect(url_for('addStudent'))
        else:
                return render_template('addStudent.html')
   return render_template("home.html")
   
@app.route('/all/student')
def allStudents():
    if session.get('logged_in'):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.close()
        return render_template('allStudent.html', students=students)
    return render_template("home.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
   if session.get('logged_in'):
        if request.method == 'POST':
                search_query = request.form['search']
                cursor = mydb.cursor()
                query = "SELECT * FROM students WHERE name LIKE %s"
                cursor.execute(query, ('%' + search_query + '%',))
                students = cursor.fetchall()
                cursor.close()
                return render_template('search.html', students=students, search_query=search_query)
        else:
                return render_template('search.html')
   return render_template("home.html")



@app.route('/course', methods=['GET', 'POST'])
def addCourse():
     if session.get('logged_in'):
      if request.method == 'POST':
        course_name = request.form['course_name']
        duration = request.form['duration']
        fees = request.form['fees']
        # Insert the course into the database
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO courses (course_name, duration, fees) VALUES (%s, %s, %s)", (course_name, duration, fees))
        mydb.commit()
        cursor.close()
        return redirect(url_for('show_courses'))
      else:
        return render_template('addCourse.html')          
     return render_template("home.html")


@app.route('/all/courses')
def show_courses():
   if session.get('logged_in'):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        return render_template('show_courses.html', courses=courses)
   return render_template("home.html")

@app.route('/logout')
def logout():
    # remove the user's login status from the session
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
   cursor = mydb.cursor()
   if session.get('logged_in'):
        if request.method == 'POST':
            student_id = request.form['student_id']
            course_id = request.form['course_id']
            session_date = datetime.strptime(request.form['session_date'], '%Y-%m-%d').date()
            status = request.form['status']
            cursor.execute("INSERT INTO attendance (student_id, course_id, session_date, status) VALUES (%s, %s, %s, %s)", (student_id, course_id, session_date, status))
            mydb.commit()
            cursor.close()
            return redirect('/all/attendance')
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        cursor.execute("SELECT * FROM courses")
        courses = cursor.fetchall()
        mydb.commit()
        cursor.close()
        return render_template('addAttendance.html', students=students, courses=courses)

   return render_template("home.html")


@app.route('/all/attendance')
def view_attendance():
    if session.get('logged_in'):
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM attendance_report")
        attendance_report = cursor.fetchall()
        cursor.execute("SELECT * FROM attendance")
        attendance_data = cursor.fetchall()
        cursor.close()
        return render_template('view_attendance.html', attendance_report=attendance_report, attendance_data=attendance_data)
    return render_template("home.html")

@app.route('/add_exam', methods=['GET','POST'])
def addExam():
    if session.get('logged_in'):
      if request.method == 'POST':
       
        exam_name = request.form['exam_name']
        exam_date = request.form['exam_date']
        course_id = request.form['course_id']
        with mydb.cursor() as cursor:
            sql = "INSERT INTO exams (exam_name, exam_date, course_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (exam_name, exam_date, course_id))
            mydb.commit()
            return "Exam added successfully"     
      else:
            return render_template('addExam.html')
    return render_template("index.html")

@app.route('/exam')
def exam():
   if session.get('logged_in'):
    try:
        with mydb.cursor() as cursor:
            sql = "SELECT * FROM exams"
            cursor.execute(sql)
            exams = cursor.fetchall()
            print(exams)
            return render_template('allExams.html', exams=exams)
    except:
        return "Error"
   return render_template("index.html")




if __name__ == '__main__':
    app.run()
