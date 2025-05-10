"""
Populate the Student Information System with sample data.
Run this script to create sample staff, students, courses, attendance records, and grades.
"""

import random
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app import app, db
from models import Role, User, Staff, Student, Course, Enrollment, Attendance, Grade

def create_roles():
    """Create admin, staff, and student roles if they don't exist."""
    roles = [
        {'name': 'admin', 'description': 'Administrator with full access'},
        {'name': 'staff', 'description': 'Staff with student management access'},
        {'name': 'student', 'description': 'Student with limited access'}
    ]
    
    for role_data in roles:
        role = Role.query.filter_by(name=role_data['name']).first()
        if not role:
            role = Role(name=role_data['name'], description=role_data['description'])
            db.session.add(role)
    
    db.session.commit()
    print("Roles created successfully.")

def create_admin():
    """Create admin user if it doesn't exist."""
    admin_role = Role.query.filter_by(name='admin').first()
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@sis.edu',
            role_id=admin_role.id
        )
        admin.password_hash = generate_password_hash('admin123')  # Default password
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully.")

def create_staff():
    """Create sample staff members."""
    staff_role = Role.query.filter_by(name='staff').first()
    
    staff_data = [
        {'username': 'arunkumar', 'first_name': 'Arun', 'last_name': 'Kumar', 'department': 'Computer Science'},
        {'username': 'priyasharma', 'first_name': 'Priya', 'last_name': 'Sharma', 'department': 'Mathematics'},
        {'username': 'rajeshpatel', 'first_name': 'Rajesh', 'last_name': 'Patel', 'department': 'Physics'},
        {'username': 'anjali', 'first_name': 'Anjali', 'last_name': 'Desai', 'department': 'English'},
        {'username': 'venkat', 'first_name': 'Venkat', 'last_name': 'Rao', 'department': 'Computer Science'},
    ]
    
    # Get all existing staff
    existing_staff = Staff.query.all()
    if existing_staff:
        print(f"Found {len(existing_staff)} existing staff members.")
        return existing_staff
    
    staff_instances = []
    for idx, data in enumerate(staff_data, 1):
        # Check if user already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            # Get existing staff profile
            staff = Staff.query.filter_by(user_id=existing_user.id).first()
            if staff:
                staff_instances.append(staff)
                continue
        
        # Create user if needed
        if not existing_user:
            email = f"{data['username']}@sis.edu"
            staff_user = User(
                username=data['username'],
                email=email,
                role_id=staff_role.id
            )
            staff_user.password_hash = generate_password_hash('staff123')  # Default password
            db.session.add(staff_user)
            db.session.commit()  # Commit to get user_id
            user_id = staff_user.id
        else:
            user_id = existing_user.id
        
        # Create staff profile
        # Get the max staff ID and increment
        max_staff = Staff.query.order_by(Staff.id.desc()).first()
        next_id = 1 if not max_staff else max_staff.id + 1
        staff_id = f"STAFF{next_id:04d}"
        
        staff = Staff(
            user_id=user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            staff_id=staff_id,
            department=data['department'],
            position='Lecturer',
            hire_date=date(2020, 1, 1) - timedelta(days=random.randint(0, 1000))
        )
        db.session.add(staff)
        staff_instances.append(staff)
        db.session.commit()
    
    print(f"{len(staff_instances)} staff members created successfully.")
    return staff_instances

def create_students():
    """Create sample students."""
    student_role = Role.query.filter_by(name='student').first()
    
    student_data = [
        {'username': 'ravi', 'first_name': 'Ravi', 'last_name': 'Singh', 'semester': 3},
        {'username': 'nandha', 'first_name': 'Nandha', 'last_name': 'Kumar', 'semester': 2},
        {'username': 'mounish', 'first_name': 'Mounish', 'last_name': 'Reddy', 'semester': 4},
        {'username': 'rahul', 'first_name': 'Rahul', 'last_name': 'Verma', 'semester': 1},
        {'username': 'ananya', 'first_name': 'Ananya', 'last_name': 'Patel', 'semester': 3},
        {'username': 'krishna', 'first_name': 'Krishna', 'last_name': 'Iyer', 'semester': 2},
        {'username': 'divya', 'first_name': 'Divya', 'last_name': 'Sharma', 'semester': 4},
        {'username': 'vijay', 'first_name': 'Vijay', 'last_name': 'Malhotra', 'semester': 1},
        {'username': 'sneha', 'first_name': 'Sneha', 'last_name': 'Gupta', 'semester': 3},
        {'username': 'arjun', 'first_name': 'Arjun', 'last_name': 'Nair', 'semester': 2}
    ]
    
    # Get all existing students
    existing_students = Student.query.all()
    if existing_students:
        print(f"Found {len(existing_students)} existing students.")
        return existing_students
    
    student_instances = []
    for idx, data in enumerate(student_data, 1):
        # Check if user already exists
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            # Get existing student profile
            student = Student.query.filter_by(user_id=existing_user.id).first()
            if student:
                student_instances.append(student)
                continue
                
        # Create user if needed
        if not existing_user:
            email = f"{data['username']}@student.sis.edu"
            student_user = User(
                username=data['username'],
                email=email,
                role_id=student_role.id
            )
            student_user.password_hash = generate_password_hash('student123')  # Default password
            db.session.add(student_user)
            db.session.commit()  # Commit to get user_id
            user_id = student_user.id
        else:
            user_id = existing_user.id
        
        # Create student profile
        # Get the max student ID and increment
        max_student = Student.query.order_by(Student.id.desc()).first()
        next_id = 1 if not max_student else max_student.id + 1
        student_id = f"STU{next_id:04d}"
        
        student = Student(
            user_id=user_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            student_id=student_id,
            date_of_birth=date(1998, 1, 1) - timedelta(days=random.randint(0, 2000)),
            enrollment_date=date(2020, 1, 1) - timedelta(days=random.randint(0, 500)),
            current_semester=data['semester']
        )
        db.session.add(student)
        student_instances.append(student)
        db.session.commit()
    
    print(f"{len(student_instances)} students created successfully.")
    return student_instances

def create_courses(staff_members):
    """Create sample courses assigned to staff members."""
    # Check for existing courses
    existing_courses = Course.query.all()
    if existing_courses:
        print(f"Found {len(existing_courses)} existing courses.")
        return existing_courses
    
    course_data = [
        {'code': 'CS101', 'title': 'Introduction to Programming', 'credits': 4, 'semester': 1},
        {'code': 'CS201', 'title': 'Data Structures', 'credits': 4, 'semester': 2},
        {'code': 'CS301', 'title': 'Database Systems', 'credits': 3, 'semester': 3},
        {'code': 'CS401', 'title': 'Artificial Intelligence', 'credits': 4, 'semester': 4},
        {'code': 'MATH101', 'title': 'Calculus I', 'credits': 3, 'semester': 1},
        {'code': 'MATH201', 'title': 'Linear Algebra', 'credits': 3, 'semester': 2},
        {'code': 'PHY101', 'title': 'Physics I', 'credits': 4, 'semester': 1},
        {'code': 'ENG101', 'title': 'English Composition', 'credits': 3, 'semester': 1}
    ]
    
    course_instances = []
    for data in course_data:
        # Check if course already exists
        existing_course = Course.query.filter_by(course_code=data['code']).first()
        if existing_course:
            course_instances.append(existing_course)
            continue
            
        # Select a random staff member for the course
        staff = random.choice(staff_members)
        
        course = Course(
            course_code=data['code'],
            title=data['title'],
            description=f"This is a sample course for {data['title']}",
            credits=data['credits'],
            semester=data['semester'],
            instructor_id=staff.id
        )
        db.session.add(course)
        db.session.commit()  # Commit to get course id
        course_instances.append(course)
    
    print(f"{len(course_instances)} courses available.")
    return course_instances

def create_enrollments(students, courses):
    """Create enrollments for students in courses."""
    # Check for existing enrollments
    existing_enrollments = Enrollment.query.all()
    if existing_enrollments:
        print(f"Found {len(existing_enrollments)} existing enrollments.")
        return existing_enrollments
    
    enrollments = []
    for student in students:
        # Enroll each student in 2-4 courses
        num_courses = random.randint(2, 4)
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            # Check if enrollment already exists
            existing_enrollment = Enrollment.query.filter_by(
                student_id=student.id, course_id=course.id
            ).first()
            
            if existing_enrollment:
                enrollments.append(existing_enrollment)
                continue
                
            enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id,
                enrollment_date=datetime.now() - timedelta(days=random.randint(0, 90)),
                status='active'
            )
            db.session.add(enrollment)
            db.session.commit()  # Commit to get enrollment id
            enrollments.append(enrollment)
    
    print(f"{len(enrollments)} enrollments available.")
    return enrollments

def create_attendance(enrollments, staff_members):
    """Create attendance records for enrolled students."""
    # Check for existing attendance records
    existing_attendance = Attendance.query.all()
    if len(existing_attendance) > 100:  # If we have significant attendance data
        print(f"Found {len(existing_attendance)} existing attendance records.")
        return existing_attendance
    
    attendance_records = []
    today = date.today()
    
    # Create attendance for the last 30 days
    for i in range(0, 30):
        record_date = today - timedelta(days=i)
        
        # Skip weekends
        if record_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            continue
            
        for enrollment in enrollments:
            # Check if attendance already exists for this date and enrollment
            existing_record = Attendance.query.filter_by(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                date=record_date
            ).first()
            
            if existing_record:
                attendance_records.append(existing_record)
                continue
                
            # Not every student attends every day (80% attendance rate)
            if random.random() > 0.2:  # 80% chance of being present
                status = 'present'
            else:
                status = random.choice(['absent', 'excused'])
                
            # Get the instructor of the course
            course = Course.query.get(enrollment.course_id)
            staff = Staff.query.get(course.instructor_id)
            
            attendance = Attendance(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                date=record_date,
                status=status,
                remarks="Regular class",
                recorded_by=staff.id,
                recorded_at=datetime.combine(record_date, datetime.min.time())
            )
            db.session.add(attendance)
            attendance_records.append(attendance)
            
            # Commit in batches to avoid memory issues
            if len(attendance_records) % 20 == 0:
                db.session.commit()
    
    db.session.commit()
    print(f"{len(attendance_records)} attendance records available.")
    return attendance_records

def create_grades(enrollments, staff_members):
    """Create grades for enrolled students."""
    # Check for existing grades
    existing_grades = Grade.query.all()
    if len(existing_grades) > 50:  # If we have significant grade data
        print(f"Found {len(existing_grades)} existing grade records.")
        return existing_grades
    
    grade_records = []
    assignment_types = ['quiz', 'test', 'homework', 'project', 'exam']
    
    for enrollment in enrollments:
        # Create 3-5 grade entries per enrollment
        num_grades = random.randint(3, 5)
        
        # Check existing grades for this enrollment
        existing_grades_count = Grade.query.filter_by(
            student_id=enrollment.student_id, 
            course_id=enrollment.course_id
        ).count()
        
        if existing_grades_count >= num_grades:
            # We already have enough grades for this enrollment
            for grade in Grade.query.filter_by(
                student_id=enrollment.student_id, 
                course_id=enrollment.course_id
            ).all():
                grade_records.append(grade)
            continue
            
        # Get the instructor of the course
        course = Course.query.get(enrollment.course_id)
        staff = Staff.query.get(course.instructor_id)
        
        for i in range(num_grades - existing_grades_count):
            assignment_type = random.choice(assignment_types)
            max_score = 100 if assignment_type == 'exam' else random.choice([10, 20, 50])
            
            # Calculate random score (generally good scores)
            score = max_score * random.uniform(0.6, 1.0)
            score = round(score, 1)  # Round to 1 decimal place
            
            # Weights should sum up to around 100%
            weight = round(100 / num_grades, 2)
            
            grade = Grade(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                assignment_name=f"{assignment_type.capitalize()} {i+1}",
                assignment_type=assignment_type,
                max_score=max_score,
                score=score,
                weight=weight,
                graded_by=staff.id,
                graded_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                comments="Good work!" if score/max_score > 0.8 else "Needs improvement"
            )
            db.session.add(grade)
            db.session.commit()  # Commit each grade to avoid conflicts
            grade_records.append(grade)
    
    print(f"{len(grade_records)} grade records available.")
    return grade_records

def main():
    """Main function to populate the database with sample data."""
    with app.app_context():
        print("Starting to populate database with sample data...")
        
        # Create roles and admin user
        create_roles()
        create_admin()
        
        # Create staff and students
        staff_members = create_staff()
        students = create_students()
        
        # Create courses and enrollments
        courses = create_courses(staff_members)
        enrollments = create_enrollments(students, courses)
        
        # Create attendance records and grades
        create_attendance(enrollments, staff_members)
        create_grades(enrollments, staff_members)
        
        print("Sample data created successfully!")

if __name__ == '__main__':
    main()