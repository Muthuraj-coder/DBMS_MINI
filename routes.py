from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, desc
from datetime import datetime, date
from werkzeug.security import generate_password_hash

from app import app, db
from models import User, Role, Student, Staff, Course, Enrollment, Attendance, Grade
from forms import (
    LoginForm, RegistrationForm, StudentProfileForm, StaffProfileForm, 
    CourseForm, AttendanceForm, GradeForm, BulkAttendanceForm,
    UserSearchForm, PasswordChangeForm, AddStudentForm
)
from utils import requires_roles, calculate_overall_grade, calculate_attendance_percentage, get_grade_statistics

# Authentication routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        elif current_user.is_staff():
            return redirect(url_for('staff_dashboard'))
        elif current_user.is_student():
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('index')
            
            flash('Login successful.', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form, title='Login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# Register route is now disabled for public use
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect unauthenticated users to login
    if not current_user.is_authenticated:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))
    
    # Redirect non-admin authenticated users to their dashboard
    if not current_user.is_admin():
        return redirect(url_for('index'))
    
    # Admins are redirected to the add_user page
    return redirect(url_for('add_user'))

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_user():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        role = Role.query.filter_by(name=form.role.data).first()
        if not role:
            flash(f'Role {form.role.data} does not exist.', 'danger')
            return render_template('admin/add_user.html', form=form, title='Add New User')
        
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('admin/add_user.html', form=form, title='Add New User')
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/add_user.html', form=form, title='Add New User')
        
        # Create the user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=role
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # If the role is staff, create a staff profile
        if role.name == 'staff':
            staff_id = f"STAFF{user.id:04d}"
            staff = Staff(
                user_id=user.id,
                first_name="",
                last_name="",
                staff_id=staff_id
            )
            db.session.add(staff)
            db.session.commit()
            
            flash(f'Staff account created with ID: {staff_id}.', 'success')
        
        # If the role is student, create a student profile
        elif role.name == 'student':
            student_id = f"STU{user.id:04d}"
            student = Student(
                user_id=user.id,
                first_name="",
                last_name="",
                student_id=student_id
            )
            db.session.add(student)
            db.session.commit()
            
            flash(f'Student account created with ID: {student_id}.', 'success')
        else:
            flash('Admin account created successfully.', 'success')
        
        return redirect(url_for('manage_users'))
    
    return render_template('admin/add_user.html', form=form, title='Add New User')

@app.route('/staff/add_student', methods=['GET', 'POST'])
@login_required
@requires_roles('staff', 'admin')
def add_student():
    form = AddStudentForm()
    
    if form.validate_on_submit():
        # First create the user account
        role = Role.query.filter_by(name='student').first()
        if not role:
            flash('Student role does not exist.', 'danger')
            return render_template('staff/add_student.html', form=form, title='Add New Student')
        
        # Create the user
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=role
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Create the student profile
        student_id = f"STU{user.id:04d}"
        student = Student(
            user_id=user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            student_id=student_id,
            date_of_birth=form.date_of_birth.data,
            current_semester=form.current_semester.data or 1
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash(f'Student account created successfully. Student ID: {student_id}', 'success')
        
        # Redirect to appropriate page based on user role
        if current_user.is_admin():
            return redirect(url_for('manage_users'))
        else:
            return redirect(url_for('staff_students'))
            
    return render_template('staff/add_student.html', form=form, title='Add New Student')

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('change_password.html', form=form, title='Change Password')

# Admin routes
@app.route('/admin/dashboard')
@login_required
@requires_roles('admin')
def admin_dashboard():
    total_students = Student.query.count()
    total_staff = Staff.query.count()
    total_courses = Course.query.count()
    
    # Get enrollment statistics
    enrollment_stats = db.session.query(
        Course.title,
        func.count(Enrollment.id).label('count')
    ).join(
        Enrollment, Course.id == Enrollment.course_id
    ).group_by(
        Course.title
    ).order_by(
        func.count(Enrollment.id).desc()
    ).limit(5).all()
    
    # Get attendance statistics
    attendance_stats = db.session.query(
        Course.title,
        func.count(Attendance.id).label('count'),
        func.avg(
            func.case(
                [(Attendance.status == 'present', 1)],
                else_=0
            )
        ).label('attendance_rate')
    ).join(
        Attendance, Course.id == Attendance.course_id
    ).group_by(
        Course.title
    ).order_by(
        func.count(Attendance.id).desc()
    ).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_students=total_students,
        total_staff=total_staff,
        total_courses=total_courses,
        enrollment_stats=enrollment_stats,
        attendance_stats=attendance_stats
    )

@app.route('/admin/manage_users', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def manage_users():
    form = UserSearchForm()
    
    query = User.query
    
    if form.validate_on_submit() or request.args.get('search'):
        search_term = form.search.data or request.args.get('search', '')
        role_filter = form.role.data or request.args.get('role', 'all')
        
        if search_term:
            query = query.filter(
                (User.username.contains(search_term)) |
                (User.email.contains(search_term))
            )
        
        if role_filter != 'all':
            role = Role.query.filter_by(name=role_filter).first()
            if role:
                query = query.filter(User.role_id == role.id)
    
    users = query.order_by(User.username).all()
    
    return render_template(
        'admin/manage_users.html',
        title='Manage Users',
        users=users,
        form=form
    )

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@requires_roles('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('manage_users'))
    
    # Delete associated profiles
    if user.student:
        db.session.delete(user.student)
    if user.staff:
        db.session.delete(user.staff)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/user/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@requires_roles('admin')
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('manage_users'))
    
    user.active = not user.active
    db.session.commit()
    
    status = 'activated' if user.active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/manage_courses', methods=['GET'])
@login_required
@requires_roles('admin')
def manage_courses():
    courses = Course.query.order_by(Course.course_code).all()
    return render_template(
        'admin/manage_courses.html',
        title='Manage Courses',
        courses=courses
    )

@app.route('/admin/course/add', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def add_course():
    form = CourseForm()
    form.instructor_id.choices = [(s.id, f"{s.staff_id} - {s.first_name} {s.last_name}") 
                                 for s in Staff.query.order_by(Staff.last_name).all()]
    
    if form.validate_on_submit():
        course = Course(
            course_code=form.course_code.data,
            title=form.title.data,
            description=form.description.data,
            credits=form.credits.data,
            semester=form.semester.data,
            instructor_id=form.instructor_id.data
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course {course.course_code} has been added.', 'success')
        return redirect(url_for('manage_courses'))
    
    return render_template(
        'admin/course_form.html',
        title='Add Course',
        form=form
    )

@app.route('/admin/course/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@requires_roles('admin')
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    form.instructor_id.choices = [(s.id, f"{s.staff_id} - {s.first_name} {s.last_name}") 
                                 for s in Staff.query.order_by(Staff.last_name).all()]
    
    if form.validate_on_submit():
        course.course_code = form.course_code.data
        course.title = form.title.data
        course.description = form.description.data
        course.credits = form.credits.data
        course.semester = form.semester.data
        course.instructor_id = form.instructor_id.data
        
        db.session.commit()
        
        flash(f'Course {course.course_code} has been updated.', 'success')
        return redirect(url_for('manage_courses'))
    
    return render_template(
        'admin/course_form.html',
        title='Edit Course',
        form=form,
        course=course
    )

@app.route('/admin/course/<int:course_id>/delete', methods=['POST'])
@login_required
@requires_roles('admin')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    db.session.delete(course)
    db.session.commit()
    
    flash(f'Course {course.course_code} has been deleted.', 'success')
    return redirect(url_for('manage_courses'))

# Staff routes
@app.route('/staff/dashboard')
@login_required
@requires_roles('staff')
def staff_dashboard():
    # Get staff profile
    staff = current_user.staff
    
    # Get courses taught by this staff
    courses = Course.query.filter_by(instructor_id=staff.id).all()
    
    # Get recent attendance records
    recent_attendance = Attendance.query.filter_by(recorded_by=staff.id)\
        .order_by(Attendance.recorded_at.desc())\
        .limit(5)\
        .all()
    
    # Get recent grades
    recent_grades = Grade.query.filter_by(graded_by=staff.id)\
        .order_by(Grade.graded_at.desc())\
        .limit(5)\
        .all()
    
    # Get enrollment counts for courses
    enrollment_counts = {}
    for course in courses:
        enrollment_counts[course.id] = Enrollment.query.filter_by(course_id=course.id).count()
    
    return render_template(
        'staff/dashboard.html',
        title='Staff Dashboard',
        staff=staff,
        courses=courses,
        recent_attendance=recent_attendance,
        recent_grades=recent_grades,
        enrollment_counts=enrollment_counts
    )

@app.route('/staff/students')
@login_required
@requires_roles('staff')
def staff_students():
    # Get staff profile
    staff = current_user.staff
    
    # Get courses taught by this staff
    courses = Course.query.filter_by(instructor_id=staff.id).all()
    
    # Get all students enrolled in any of the staff's courses
    enrolled_students = {}
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        for enrollment in enrollments:
            if enrollment.student_id not in enrolled_students:
                enrolled_students[enrollment.student_id] = {
                    'student': enrollment.student,
                    'courses': []
                }
            enrolled_students[enrollment.student_id]['courses'].append(course)
    
    return render_template(
        'staff/students.html',
        title='Manage Students',
        enrolled_students=enrolled_students.values()
    )

@app.route('/staff/attendance', methods=['GET', 'POST'])
@login_required
@requires_roles('staff')
def staff_attendance():
    # Get staff profile
    staff = current_user.staff
    
    # Get courses taught by this staff
    courses = Course.query.filter_by(instructor_id=staff.id).all()
    
    form = BulkAttendanceForm()
    form.course_id.choices = [(c.id, f"{c.course_code} - {c.title}") for c in courses]
    
    if form.validate_on_submit():
        selected_course = Course.query.get(form.course_id.data)
        
        if not selected_course or selected_course.instructor_id != staff.id:
            flash('You are not authorized to manage attendance for this course.', 'danger')
            return redirect(url_for('staff_attendance'))
        
        enrollments = Enrollment.query.filter_by(course_id=selected_course.id).all()
        students = [enrollment.student for enrollment in enrollments]
        
        return render_template(
            'staff/record_attendance.html',
            title='Record Attendance',
            course=selected_course,
            students=students,
            date=form.date.data
        )
    
    # Get recent attendance records
    recent_attendance = db.session.query(
        Course.title,
        func.count(Attendance.id).label('count'),
        Attendance.date
    ).join(
        Attendance, Course.id == Attendance.course_id
    ).filter(
        Attendance.recorded_by == staff.id
    ).group_by(
        Course.title, Attendance.date
    ).order_by(
        Attendance.date.desc()
    ).limit(10).all()
    
    return render_template(
        'staff/attendance.html',
        title='Manage Attendance',
        form=form,
        courses=courses,
        recent_attendance=recent_attendance
    )

@app.route('/staff/save_attendance', methods=['POST'])
@login_required
@requires_roles('staff')
def save_attendance():
    # Get staff profile
    staff = current_user.staff
    
    course_id = request.form.get('course_id')
    date_str = request.form.get('date')
    
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('staff_attendance'))
    
    course = Course.query.get(course_id)
    
    if not course or course.instructor_id != staff.id:
        flash('You are not authorized to manage attendance for this course.', 'danger')
        return redirect(url_for('staff_attendance'))
    
    # Get all student IDs from the form
    student_ids = []
    for key in request.form:
        if key.startswith('student_'):
            student_id = key.split('_')[1]
            student_ids.append(int(student_id))
    
    # Process each student
    for student_id in student_ids:
        status = request.form.get(f'status_{student_id}')
        remarks = request.form.get(f'remarks_{student_id}', '')
        
        # Check if attendance record already exists
        existing = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course.id,
            date=attendance_date
        ).first()
        
        if existing:
            # Update existing record
            existing.status = status
            existing.remarks = remarks
            existing.recorded_by = staff.id
            existing.recorded_at = datetime.utcnow()
        else:
            # Create new record
            attendance = Attendance(
                student_id=student_id,
                course_id=course.id,
                date=attendance_date,
                status=status,
                remarks=remarks,
                recorded_by=staff.id
            )
            db.session.add(attendance)
    
    db.session.commit()
    flash('Attendance records have been saved.', 'success')
    return redirect(url_for('staff_attendance'))

@app.route('/staff/grades', methods=['GET', 'POST'])
@login_required
@requires_roles('staff')
def staff_grades():
    # Get staff profile
    staff = current_user.staff
    
    # Get courses taught by this staff
    courses = Course.query.filter_by(instructor_id=staff.id).all()
    
    form = BulkAttendanceForm()  # Reusing this form since it has course_id
    form.course_id.choices = [(c.id, f"{c.course_code} - {c.title}") for c in courses]
    
    if form.validate_on_submit():
        selected_course = Course.query.get(form.course_id.data)
        
        if not selected_course or selected_course.instructor_id != staff.id:
            flash('You are not authorized to manage grades for this course.', 'danger')
            return redirect(url_for('staff_grades'))
        
        enrollments = Enrollment.query.filter_by(course_id=selected_course.id).all()
        students = [enrollment.student for enrollment in enrollments]
        
        return render_template(
            'staff/manage_grades.html',
            title='Manage Grades',
            course=selected_course,
            students=students
        )
    
    # Get recent grade submissions
    recent_grades = db.session.query(
        Course.title,
        func.count(Grade.id).label('count'),
        Grade.assignment_name,
        func.max(Grade.graded_at).label('graded_at')
    ).join(
        Grade, Course.id == Grade.course_id
    ).filter(
        Grade.graded_by == staff.id
    ).group_by(
        Course.title, Grade.assignment_name
    ).order_by(
        func.max(Grade.graded_at).desc()
    ).limit(10).all()
    
    return render_template(
        'staff/grades.html',
        title='Manage Grades',
        form=form,
        courses=courses,
        recent_grades=recent_grades
    )

@app.route('/staff/add_grade/<int:student_id>/<int:course_id>', methods=['GET', 'POST'])
@login_required
@requires_roles('staff')
def add_grade(student_id, course_id):
    # Get staff profile
    staff = current_user.staff
    
    student = Student.query.get_or_404(student_id)
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != staff.id:
        flash('You are not authorized to manage grades for this course.', 'danger')
        return redirect(url_for('staff_grades'))
    
    form = GradeForm()
    form.student_id.data = student_id
    form.course_id.choices = [(course.id, f"{course.course_code} - {course.title}")]
    form.course_id.data = course.id
    
    if form.validate_on_submit():
        grade = Grade(
            student_id=form.student_id.data,
            course_id=form.course_id.data,
            assignment_name=form.assignment_name.data,
            assignment_type=form.assignment_type.data,
            max_score=form.max_score.data,
            score=form.score.data,
            weight=form.weight.data,
            comments=form.comments.data,
            graded_by=staff.id
        )
        
        db.session.add(grade)
        db.session.commit()
        
        flash('Grade has been added.', 'success')
        return redirect(url_for('manage_student_grades', student_id=student_id, course_id=course_id))
    
    return render_template(
        'staff/grade_form.html',
        title='Add Grade',
        form=form,
        student=student,
        course=course
    )

@app.route('/staff/manage_student_grades/<int:student_id>/<int:course_id>')
@login_required
@requires_roles('staff')
def manage_student_grades(student_id, course_id):
    # Get staff profile
    staff = current_user.staff
    
    student = Student.query.get_or_404(student_id)
    course = Course.query.get_or_404(course_id)
    
    if course.instructor_id != staff.id:
        flash('You are not authorized to manage grades for this course.', 'danger')
        return redirect(url_for('staff_grades'))
    
    # Get all grades for this student in this course
    grades = Grade.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).order_by(
        Grade.assignment_type,
        Grade.graded_at
    ).all()
    
    # Calculate overall grade
    overall_grade = calculate_overall_grade(grades)
    
    return render_template(
        'staff/student_grades.html',
        title=f'Grades for {student.full_name()}',
        student=student,
        course=course,
        grades=grades,
        overall_grade=overall_grade
    )

@app.route('/staff/edit_grade/<int:grade_id>', methods=['GET', 'POST'])
@login_required
@requires_roles('staff')
def edit_grade(grade_id):
    # Get staff profile
    staff = current_user.staff
    
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.get(grade.course_id)
    
    if course.instructor_id != staff.id:
        flash('You are not authorized to edit this grade.', 'danger')
        return redirect(url_for('staff_grades'))
    
    form = GradeForm(obj=grade)
    form.student_id.data = grade.student_id
    form.course_id.choices = [(course.id, f"{course.course_code} - {course.title}")]
    
    if form.validate_on_submit():
        grade.assignment_name = form.assignment_name.data
        grade.assignment_type = form.assignment_type.data
        grade.max_score = form.max_score.data
        grade.score = form.score.data
        grade.weight = form.weight.data
        grade.comments = form.comments.data
        grade.graded_by = staff.id
        grade.graded_at = datetime.utcnow()
        
        db.session.commit()
        
        flash('Grade has been updated.', 'success')
        return redirect(url_for('manage_student_grades', student_id=grade.student_id, course_id=grade.course_id))
    
    return render_template(
        'staff/grade_form.html',
        title='Edit Grade',
        form=form,
        student=grade.student,
        course=course,
        grade=grade
    )

@app.route('/staff/delete_grade/<int:grade_id>', methods=['POST'])
@login_required
@requires_roles('staff')
def delete_grade(grade_id):
    # Get staff profile
    staff = current_user.staff
    
    grade = Grade.query.get_or_404(grade_id)
    course = Course.query.get(grade.course_id)
    
    if course.instructor_id != staff.id:
        flash('You are not authorized to delete this grade.', 'danger')
        return redirect(url_for('staff_grades'))
    
    student_id = grade.student_id
    course_id = grade.course_id
    
    db.session.delete(grade)
    db.session.commit()
    
    flash('Grade has been deleted.', 'success')
    return redirect(url_for('manage_student_grades', student_id=student_id, course_id=course_id))

# Student routes
@app.route('/student/dashboard')
@login_required
@requires_roles('student')
def student_dashboard():
    # Get student profile
    student = current_user.student
    
    if not student:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student_profile'))
    
    # Get enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = [enrollment.course for enrollment in enrollments]
    
    # Get attendance information
    attendance_data = {}
    for course in courses:
        attendance_records = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).all()
        
        attendance_data[course.id] = {
            'course': course,
            'percentage': calculate_attendance_percentage(attendance_records),
            'total_classes': len(attendance_records),
            'present': sum(1 for a in attendance_records if a.status == 'present'),
            'absent': sum(1 for a in attendance_records if a.status == 'absent'),
            'excused': sum(1 for a in attendance_records if a.status == 'excused')
        }
    
    # Get grades information
    grade_data = {}
    for course in courses:
        grades = Grade.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).all()
        
        overall_grade = calculate_overall_grade(grades)
        grade_data[course.id] = {
            'course': course,
            'overall_grade': overall_grade,
            'total_assignments': len(grades)
        }
    
    return render_template(
        'student/dashboard.html',
        title='Student Dashboard',
        student=student,
        courses=courses,
        attendance_data=attendance_data,
        grade_data=grade_data
    )

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
@requires_roles('student')
def student_profile():
    # Check if student profile exists
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if student:
        form = StudentProfileForm(obj=student)
    else:
        form = StudentProfileForm()
    
    form.user_id = current_user.id
    
    if form.validate_on_submit():
        if student:
            # Update existing student
            student.first_name = form.first_name.data
            student.last_name = form.last_name.data
            student.student_id = form.student_id.data
            student.date_of_birth = form.date_of_birth.data
            student.address = form.address.data
            student.phone_number = form.phone_number.data
            student.enrollment_date = form.enrollment_date.data
            student.graduation_date = form.graduation_date.data
            student.current_semester = form.current_semester.data
        else:
            # Create new student
            student = Student(
                user_id=current_user.id,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                student_id=form.student_id.data,
                date_of_birth=form.date_of_birth.data,
                address=form.address.data,
                phone_number=form.phone_number.data,
                enrollment_date=form.enrollment_date.data,
                graduation_date=form.graduation_date.data,
                current_semester=form.current_semester.data
            )
            db.session.add(student)
        
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template(
        'student/profile.html',
        title='Student Profile',
        form=form,
        student=student
    )

@app.route('/student/attendance')
@login_required
@requires_roles('student')
def student_attendance():
    # Get student profile
    student = current_user.student
    
    if not student:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student_profile'))
    
    # Get enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = [enrollment.course for enrollment in enrollments]
    
    # Get attendance information
    attendance_data = {}
    for course in courses:
        attendance_records = Attendance.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).order_by(Attendance.date.desc()).all()
        
        attendance_data[course.id] = {
            'course': course,
            'percentage': calculate_attendance_percentage(attendance_records),
            'total_classes': len(attendance_records),
            'present': sum(1 for a in attendance_records if a.status == 'present'),
            'absent': sum(1 for a in attendance_records if a.status == 'absent'),
            'excused': sum(1 for a in attendance_records if a.status == 'excused'),
            'records': attendance_records
        }
    
    return render_template(
        'student/attendance.html',
        title='My Attendance',
        student=student,
        attendance_data=attendance_data
    )

@app.route('/student/grades')
@login_required
@requires_roles('student')
def student_grades():
    # Get student profile
    student = current_user.student
    
    if not student:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('student_profile'))
    
    # Get enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    courses = [enrollment.course for enrollment in enrollments]
    
    # Get grades information
    grade_data = {}
    for course in courses:
        grades = Grade.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).order_by(
            Grade.assignment_type,
            Grade.graded_at
        ).all()
        
        # Get grade statistics for this course
        stats = get_grade_statistics(course.id)
        
        grade_data[course.id] = {
            'course': course,
            'overall_grade': calculate_overall_grade(grades),
            'grades': grades,
            'stats': stats
        }
    
    return render_template(
        'student/grades.html',
        title='My Grades',
        student=student,
        grade_data=grade_data
    )

# API routes for data visualization
@app.route('/api/attendance_data/<int:student_id>')
@login_required
def api_attendance_data(student_id):
    # Only allow admin, staff, or the student themselves to access this data
    student = Student.query.get_or_404(student_id)
    
    if not (current_user.is_admin() or 
            (current_user.is_staff() and Staff.query.filter_by(user_id=current_user.id).first()) or 
            (current_user.is_student() and current_user.student and current_user.student.id == student_id)):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get enrollments
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    course_ids = [e.course_id for e in enrollments]
    courses = Course.query.filter(Course.id.in_(course_ids)).all()
    
    # Get attendance data for all courses
    result = []
    for course in courses:
        attendance_records = Attendance.query.filter_by(
            student_id=student_id,
            course_id=course.id
        ).all()
        
        result.append({
            'course': course.title,
            'present': sum(1 for a in attendance_records if a.status == 'present'),
            'absent': sum(1 for a in attendance_records if a.status == 'absent'),
            'excused': sum(1 for a in attendance_records if a.status == 'excused'),
            'percentage': calculate_attendance_percentage(attendance_records)
        })
    
    return jsonify(result)

@app.route('/api/grade_data/<int:student_id>')
@login_required
def api_grade_data(student_id):
    # Only allow admin, staff, or the student themselves to access this data
    student = Student.query.get_or_404(student_id)
    
    if not (current_user.is_admin() or 
            (current_user.is_staff() and Staff.query.filter_by(user_id=current_user.id).first()) or 
            (current_user.is_student() and current_user.student and current_user.student.id == student_id)):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get enrollments
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    course_ids = [e.course_id for e in enrollments]
    courses = Course.query.filter(Course.id.in_(course_ids)).all()
    
    # Get grade data for all courses
    result = []
    for course in courses:
        grades = Grade.query.filter_by(
            student_id=student_id,
            course_id=course.id
        ).all()
        
        # Calculate overall grade
        overall_grade = calculate_overall_grade(grades)
        
        # Get grade statistics for comparison
        stats = get_grade_statistics(course.id)
        
        result.append({
            'course': course.title,
            'overall_grade': overall_grade,
            'avg_class_grade': stats['avg_grade'] if stats else None,
            'grades': [
                {
                    'name': g.assignment_name,
                    'type': g.assignment_type,
                    'score': g.score,
                    'max_score': g.max_score,
                    'percentage': g.percentage(),
                    'weight': g.weight
                } for g in grades
            ]
        })
    
    return jsonify(result)

@app.route('/api/course_enrollment_stats')
@login_required
@requires_roles('admin')
def api_course_enrollment_stats():
    # Get enrollment counts for all courses
    enrollments = db.session.query(
        Course.title,
        func.count(Enrollment.id).label('count')
    ).join(
        Enrollment, Course.id == Enrollment.course_id
    ).group_by(
        Course.title
    ).all()
    
    result = [
        {'course': e.title, 'count': e.count}
        for e in enrollments
    ]
    
    return jsonify(result)

@app.route('/api/course_attendance_stats')
@login_required
@requires_roles('admin')
def api_course_attendance_stats():
    # Get attendance statistics for all courses
    attendance_stats = db.session.query(
        Course.title,
        func.count(Attendance.id).label('total'),
        func.sum(func.case([(Attendance.status == 'present', 1)], else_=0)).label('present'),
        func.sum(func.case([(Attendance.status == 'absent', 1)], else_=0)).label('absent'),
        func.sum(func.case([(Attendance.status == 'excused', 1)], else_=0)).label('excused')
    ).join(
        Attendance, Course.id == Attendance.course_id
    ).group_by(
        Course.title
    ).all()
    
    result = [
        {
            'course': a.title,
            'total': a.total,
            'present': a.present,
            'absent': a.absent,
            'excused': a.excused,
            'percentage': (a.present / a.total * 100) if a.total > 0 else 0
        }
        for a in attendance_stats
    ]
    
    return jsonify(result)

# Initialize database with roles
# Initialize roles when the application starts
# Flask 2.0+ removed before_first_request, using with_appcontext instead
def create_initial_roles():
    # Check if roles already exist
    if Role.query.count() == 0:
            roles = [
                Role(name='admin', description='Administrator with full access'),
                Role(name='staff', description='Staff with limited access'),
                Role(name='student', description='Student with restricted access')
            ]
            db.session.bulk_save_objects(roles)
            db.session.commit()
            
            # Create initial admin user
            admin_role = Role.query.filter_by(name='admin').first()
            admin_exists = User.query.filter_by(username='admin').first()
            
            if not admin_exists:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    role=admin_role
                )
                admin.set_password('admin123')  # default password, should be changed
                db.session.add(admin)
                db.session.commit()
