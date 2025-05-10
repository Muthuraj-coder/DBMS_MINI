from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Role-based access control
class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Role {self.name}>'

# User model for authentication
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    role = db.relationship('Role', backref=db.backref('users', lazy=True))
    student = db.relationship('Student', backref='user', uselist=False)
    staff = db.relationship('Staff', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role.name == 'admin'
    
    def is_staff(self):
        return self.role.name == 'staff'
    
    def is_student(self):
        return self.role.name == 'student'
    
    def __repr__(self):
        return f'<User {self.username}>'

# Student model
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    enrollment_date = db.Column(db.Date)
    graduation_date = db.Column(db.Date)
    current_semester = db.Column(db.Integer)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    attendances = db.relationship('Attendance', backref='student', lazy=True)
    grades = db.relationship('Grade', backref='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.first_name} {self.last_name}>'
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

# Staff model
class Staff(db.Model):
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    hire_date = db.Column(db.Date)
    
    # Relationships
    courses = db.relationship('Course', backref='instructor', lazy=True)
    
    def __repr__(self):
        return f'<Staff {self.first_name} {self.last_name}>'
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

# Course model
class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer)
    semester = db.Column(db.Integer)
    instructor_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)
    attendances = db.relationship('Attendance', backref='course', lazy=True)
    grades = db.relationship('Grade', backref='course', lazy=True)
    
    def __repr__(self):
        return f'<Course {self.course_code}: {self.title}>'

# Enrollment model
class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, dropped, completed
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} in {self.course_id}>'

# Attendance model
class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # present, absent, excused
    remarks = db.Column(db.Text)
    recorded_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('Staff', foreign_keys=[recorded_by], backref='recorded_attendances')
    
    def __repr__(self):
        return f'<Attendance {self.student_id} in {self.course_id} on {self.date}>'

# Grade model
class Grade(db.Model):
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    assignment_name = db.Column(db.String(100), nullable=False)
    assignment_type = db.Column(db.String(50))  # quiz, test, homework, project, exam
    max_score = db.Column(db.Float)
    score = db.Column(db.Float)
    weight = db.Column(db.Float)  # percentage weight of this assignment in final grade
    graded_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.Column(db.Text)
    
    # Relationships
    staff = db.relationship('Staff', foreign_keys=[graded_by], backref='graded_assignments')
    
    def __repr__(self):
        return f'<Grade {self.student_id} in {self.course_id} for {self.assignment_name}>'
    
    def percentage(self):
        if self.max_score == 0:
            return 0
        return (self.score / self.max_score) * 100
    
    def letter_grade(self):
        percentage = self.percentage()
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
