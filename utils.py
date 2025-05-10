from flask import abort
from functools import wraps
from flask_login import current_user
from sqlalchemy import func
from sqlalchemy.sql import text

from models import Grade

def requires_roles(*roles):
    """
    Function decorator to restrict access to specified roles.
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.role or current_user.role.name not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return wrapper

def calculate_overall_grade(grades):
    """
    Calculate the overall grade based on weighted assignments.
    """
    if not grades:
        return None
    
    total_weight = sum(g.weight for g in grades)
    if total_weight == 0:
        return 0
    
    weighted_sum = sum((g.score / g.max_score) * g.weight for g in grades)
    return (weighted_sum / total_weight) * 100

def calculate_attendance_percentage(attendance_records):
    """
    Calculate attendance percentage (present / total classes).
    """
    if not attendance_records:
        return 100  # No records means no absences
    
    total = len(attendance_records)
    present = sum(1 for a in attendance_records if a.status == 'present')
    
    return (present / total) * 100 if total > 0 else 100

def get_grade_statistics(course_id):
    """
    Get grade statistics for a course (min, max, avg grades).
    """
    from app import db
    
    # Query to calculate statistics for each assignment
    stats_by_assignment = db.session.query(
        Grade.assignment_name,
        func.min(Grade.score / Grade.max_score * 100).label('min_grade'),
        func.max(Grade.score / Grade.max_score * 100).label('max_grade'),
        func.avg(Grade.score / Grade.max_score * 100).label('avg_grade'),
        func.count(Grade.id).label('count')
    ).filter(
        Grade.course_id == course_id
    ).group_by(
        Grade.assignment_name
    ).all()
    
    # Calculate overall course statistics
    overall_stats = db.session.query(
        func.min(func.sum(Grade.score * Grade.weight) / func.sum(Grade.max_score * Grade.weight) * 100).label('min_grade'),
        func.max(func.sum(Grade.score * Grade.weight) / func.sum(Grade.max_score * Grade.weight) * 100).label('max_grade'),
        func.avg(func.sum(Grade.score * Grade.weight) / func.sum(Grade.max_score * Grade.weight) * 100).label('avg_grade')
    ).filter(
        Grade.course_id == course_id
    ).group_by(
        Grade.student_id
    ).first()
    
    if not overall_stats:
        return None
    
    return {
        'min_grade': overall_stats.min_grade,
        'max_grade': overall_stats.max_grade,
        'avg_grade': overall_stats.avg_grade,
        'by_assignment': [
            {
                'name': stat.assignment_name,
                'min_grade': stat.min_grade,
                'max_grade': stat.max_grade,
                'avg_grade': stat.avg_grade,
                'count': stat.count
            }
            for stat in stats_by_assignment
        ]
    }

def get_letter_grade(percentage):
    """
    Convert percentage to letter grade.
    """
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
