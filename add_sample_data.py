"""
A simplified script to add sample data to the Student Information System.
This version is more direct and faster than the full populate_sample_data.py script.
"""

import random
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app import app, db
from models import Role, User, Staff, Student, Course, Enrollment, Attendance, Grade

def main():
    """Main function to add sample data to the database."""
    with app.app_context():
        print("Starting to add sample data...")
        
        # Make sure roles exist
        ensure_roles()
        
        # Get or create admin
        admin = get_or_create_admin()
        
        # Add staff
        staff_members = add_staff_members()
        
        # Add students
        students = add_students()
        
        # Add courses
        courses = add_courses(staff_members)
        
        # Add enrollments
        enrollments = add_enrollments(students, courses)
        
        # Add some grades and attendance (limited amount for speed)
        add_grades(enrollments)
        add_attendance(enrollments)
        
        print("Sample data added successfully!")

def ensure_roles():
    """Make sure all required roles exist."""
    roles = {
        'admin': 'Administrator with full access',
        'staff': 'Staff with student management access',
        'student': 'Student with limited access'
    }
    
    for role_name, description in roles.items():
        role = Role.query.filter_by(name=role_name).first()
        if not role:
            db.session.add(Role(name=role_name, description=description))
    
    db.session.commit()
    print("Roles verified.")

def get_or_create_admin():
    """Get the admin user or create if not exists."""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_role = Role.query.filter_by(name='admin').first()
        admin = User(
            username='admin',
            email='admin@sis.edu',
            role_id=admin_role.id
        )
        admin.password_hash = generate_password_hash('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    return admin

def add_staff_members():
    """Add staff members directly."""
    staff_role = Role.query.filter_by(name='staff').first()
    
    staff_data = [
        {'username': 'arunkumar', 'first_name': 'Arun', 'last_name': 'Kumar', 'dept': 'Computer Science'},
        {'username': 'priyasharma', 'first_name': 'Priya', 'last_name': 'Sharma', 'dept': 'Mathematics'},
        {'username': 'rajeshpatel', 'first_name': 'Rajesh', 'last_name': 'Patel', 'dept': 'Physics'},
        {'username': 'anjalidesai', 'first_name': 'Anjali', 'last_name': 'Desai', 'dept': 'English'},
        {'username': 'venkatrao', 'first_name': 'Venkat', 'last_name': 'Rao', 'dept': 'Computer Science'}
    ]
    
    staff_members = []
    
    # Add each staff member if they don't exist
    for idx, data in enumerate(staff_data, 1):
        staff_user = User.query.filter_by(username=data['username']).first()
        
        if not staff_user:
            # Create new staff user
            staff_user = User(
                username=data['username'],
                email=f"{data['username']}@sis.edu",
                role_id=staff_role.id
            )
            staff_user.password_hash = generate_password_hash('staff123')
            db.session.add(staff_user)
            db.session.commit()
            
            # Create staff profile with unique staff_id
            staff_id = f"STAFF{idx:04d}"
            staff = Staff(
                user_id=staff_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                staff_id=staff_id,
                department=data['dept'],
                position='Lecturer',
                hire_date=date(2020, 1, 1) - timedelta(days=random.randint(0, 500))
            )
            db.session.add(staff)
            db.session.commit()
            print(f"Created staff: {data['first_name']} {data['last_name']}")
        else:
            # Get existing staff profile
            staff = Staff.query.filter_by(user_id=staff_user.id).first()
            if not staff:
                # This should not happen normally, but handle just in case
                staff_id = f"STAFF{idx:04d}"
                staff = Staff(
                    user_id=staff_user.id,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    staff_id=staff_id,
                    department=data['dept'],
                    position='Lecturer',
                    hire_date=date(2020, 1, 1)
                )
                db.session.add(staff)
                db.session.commit()
                print(f"Created missing staff profile for existing user: {data['username']}")
            else:
                print(f"Staff already exists: {staff.first_name} {staff.last_name}")
        
        staff_members.append(staff)
    
    return staff_members

def add_students():
    """Add student users directly."""
    student_role = Role.query.filter_by(name='student').first()
    
    student_data = [
        {'username': 'ravikumar', 'first_name': 'Ravi', 'last_name': 'Kumar', 'semester': 3},
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
    
    students = []
    
    # Add each student if they don't exist
    for idx, data in enumerate(student_data, 1):
        student_user = User.query.filter_by(username=data['username']).first()
        
        if not student_user:
            # Create new student user
            student_user = User(
                username=data['username'],
                email=f"{data['username']}@student.sis.edu",
                role_id=student_role.id
            )
            student_user.password_hash = generate_password_hash('student123')
            db.session.add(student_user)
            db.session.commit()
            
            # Create student profile with unique student_id
            student_id = f"STU{idx:04d}"
            student = Student(
                user_id=student_user.id,
                first_name=data['first_name'],
                last_name=data['last_name'],
                student_id=student_id,
                date_of_birth=date(1998, 1, 1) - timedelta(days=random.randint(0, 1000)),
                enrollment_date=date(2020, 1, 1) - timedelta(days=random.randint(0, 500)),
                current_semester=data['semester']
            )
            db.session.add(student)
            db.session.commit()
            print(f"Created student: {data['first_name']} {data['last_name']}")
        else:
            # Get existing student profile
            student = Student.query.filter_by(user_id=student_user.id).first()
            if not student:
                # Create profile if missing
                student_id = f"STU{idx:04d}"
                student = Student(
                    user_id=student_user.id,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    student_id=student_id,
                    date_of_birth=date(1998, 1, 1),
                    enrollment_date=date(2020, 1, 1),
                    current_semester=data['semester']
                )
                db.session.add(student)
                db.session.commit()
                print(f"Created missing student profile for existing user: {data['username']}")
            else:
                print(f"Student already exists: {student.first_name} {student.last_name}")
        
        students.append(student)
    
    return students

def add_courses(staff_members):
    """Add courses directly."""
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
    
    courses = []
    
    # Add each course if it doesn't exist
    for idx, data in enumerate(course_data):
        course = Course.query.filter_by(course_code=data['code']).first()
        
        if not course:
            # Assign to a random staff member
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
            db.session.commit()
            print(f"Created course: {data['code']} - {data['title']}")
        else:
            print(f"Course already exists: {course.course_code} - {course.title}")
        
        courses.append(course)
    
    return courses

def add_enrollments(students, courses):
    """Add enrollments directly."""
    enrollments = []
    
    # For each student, enroll in 2-4 random courses
    for student in students:
        # Determine how many courses this student takes
        num_courses = random.randint(2, 4)
        # Get a random selection of courses
        selected_courses = random.sample(courses, min(num_courses, len(courses)))
        
        for course in selected_courses:
            # Check if enrollment already exists
            enrollment = Enrollment.query.filter_by(
                student_id=student.id, course_id=course.id
            ).first()
            
            if not enrollment:
                # Create new enrollment
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_date=date.today() - timedelta(days=random.randint(0, 60)),
                    status='active'
                )
                db.session.add(enrollment)
                db.session.commit()
                print(f"Enrolled {student.first_name} in {course.title}")
            else:
                print(f"{student.first_name} already enrolled in {course.title}")
            
            enrollments.append(enrollment)
    
    return enrollments

def add_grades(enrollments):
    """Add some grades for the enrollments."""
    assignment_types = ['quiz', 'test', 'homework', 'project', 'exam']
    grades_added = 0
    
    # Only add grades for up to 20 enrollments for speed
    for enrollment in enrollments[:20]:
        # Check if this enrollment already has grades
        existing_grades = Grade.query.filter_by(
            student_id=enrollment.student_id,
            course_id=enrollment.course_id
        ).count()
        
        if existing_grades >= 3:
            print(f"Enrollment already has {existing_grades} grades. Skipping.")
            continue
        
        # Get course instructor
        course = Course.query.get(enrollment.course_id)
        if not course or not course.instructor_id:
            print(f"Course {enrollment.course_id} has no instructor. Skipping grades.")
            continue
            
        staff = Staff.query.get(course.instructor_id)
        if not staff:
            print(f"Staff {course.instructor_id} not found. Skipping grades.")
            continue
        
        # Add 3 grades per enrollment
        for i in range(3):
            assignment_type = random.choice(assignment_types)
            max_score = 100 if assignment_type == 'exam' else random.choice([10, 20, 50])
            
            # Students generally do well (60-100%)
            score = max_score * random.uniform(0.6, 1.0)
            score = round(score, 1)
            
            # Each assignment gets equal weight
            weight = 33.33
            
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
            grades_added += 1
            
            # Commit after each grade to avoid conflicts
            db.session.commit()
    
    print(f"Added {grades_added} grades.")

def add_attendance(enrollments):
    """Add attendance records for the enrollments."""
    attendance_added = 0
    today = date.today()
    
    # Only process a subset of enrollments and days for speed
    for enrollment in enrollments[:15]:
        # Get course instructor
        course = Course.query.get(enrollment.course_id)
        if not course or not course.instructor_id:
            print(f"Course {enrollment.course_id} has no instructor. Skipping attendance.")
            continue
            
        staff = Staff.query.get(course.instructor_id)
        if not staff:
            print(f"Staff {course.instructor_id} not found. Skipping attendance.")
            continue
        
        # Add attendance for last 10 days (excluding weekends)
        for i in range(10):
            record_date = today - timedelta(days=i)
            
            # Skip weekends
            if record_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                continue
                
            # Check if attendance record already exists
            existing = Attendance.query.filter_by(
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                date=record_date
            ).first()
            
            if existing:
                # print(f"Attendance record already exists for {record_date}. Skipping.")
                continue
            
            # 80% chance of being present
            status = 'present' if random.random() > 0.2 else random.choice(['absent', 'excused'])
            
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
            attendance_added += 1
            
            # Commit in small batches
            if attendance_added % 5 == 0:
                db.session.commit()
    
    # Final commit
    db.session.commit()
    print(f"Added {attendance_added} attendance records.")

if __name__ == '__main__':
    main()