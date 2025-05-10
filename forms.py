from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FloatField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User, Student, Staff, Course
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('admin', 'Administrator'), ('staff', 'Staff'), ('student', 'Student')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class StudentProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    enrollment_date = DateField('Enrollment Date', validators=[Optional()], default=date.today)
    graduation_date = DateField('Expected Graduation Date', validators=[Optional()])
    current_semester = IntegerField('Current Semester', validators=[Optional()])
    submit = SubmitField('Save Profile')
    
    def validate_student_id(self, student_id):
        student = Student.query.filter_by(student_id=student_id.data).first()
        if student and student.user_id != self.user_id.data:
            raise ValidationError('This Student ID is already registered.')

class StaffProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    department = StringField('Department', validators=[Optional()])
    position = StringField('Position', validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    phone_number = StringField('Phone Number', validators=[Optional()])
    hire_date = DateField('Hire Date', validators=[Optional()], default=date.today)
    submit = SubmitField('Save Profile')
    
    def validate_staff_id(self, staff_id):
        staff = Staff.query.filter_by(staff_id=staff_id.data).first()
        if staff and staff.user_id != self.user_id.data:
            raise ValidationError('This Staff ID is already registered.')

class CourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired()])
    title = StringField('Course Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    credits = IntegerField('Credits', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired()])
    instructor_id = SelectField('Instructor', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Course')
    
    def validate_course_code(self, course_code):
        course = Course.query.filter_by(course_code=course_code.data).first()
        if course and course.id != self.course_id.data:
            raise ValidationError('This Course Code is already in use.')

class AttendanceForm(FlaskForm):
    student_id = HiddenField('Student ID', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    status = SelectField('Status', choices=[
        ('present', 'Present'), 
        ('absent', 'Absent'), 
        ('excused', 'Excused')
    ], validators=[DataRequired()])
    remarks = TextAreaField('Remarks', validators=[Optional()])
    submit = SubmitField('Record Attendance')

class GradeForm(FlaskForm):
    student_id = HiddenField('Student ID', validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    assignment_name = StringField('Assignment Name', validators=[DataRequired()])
    assignment_type = SelectField('Assignment Type', choices=[
        ('quiz', 'Quiz'),
        ('test', 'Test'),
        ('homework', 'Homework'),
        ('project', 'Project'),
        ('exam', 'Exam')
    ], validators=[DataRequired()])
    max_score = FloatField('Maximum Score', validators=[DataRequired()])
    score = FloatField('Score', validators=[DataRequired()])
    weight = FloatField('Weight (%)', validators=[DataRequired()])
    comments = TextAreaField('Comments', validators=[Optional()])
    submit = SubmitField('Save Grade')

class BulkAttendanceForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    submit = SubmitField('Continue')

class UserSearchForm(FlaskForm):
    search = StringField('Search by name, ID, or email', validators=[Optional()])
    role = SelectField('Role', choices=[
        ('all', 'All Roles'),
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('student', 'Student')
    ], default='all')
    submit = SubmitField('Search')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
