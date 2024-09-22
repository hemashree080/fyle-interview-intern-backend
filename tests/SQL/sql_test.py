import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from sqlalchemy import text

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def setup_assignments():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()
        
        assignments = [
            Assignment(id=1, teacher_id=1, student_id=1, content='Assignment 1', state=AssignmentStateEnum.SUBMITTED),
            Assignment(id=2, teacher_id=1, student_id=1, grade=GradeEnum.C, state=AssignmentStateEnum.GRADED),
            Assignment(id=3, teacher_id=2, student_id=2, content='Assignment 3', state=AssignmentStateEnum.DRAFT),
        ]
        
        db.session.bulk_save_objects(assignments)
        db.session.commit()

def test_count_graded_assignments_by_teacher(client, setup_assignments):
    # This should be the SQL query that counts graded assignments for a specific teacher
    query = text("""
        SELECT COUNT(*) FROM assignments 
        WHERE teacher_id = :teacher_id AND state = :state
    """)

    teacher_id = 1
    state = AssignmentStateEnum.GRADED.value
    result = db.session.execute(query, {'teacher_id': teacher_id, 'state': state}).scalar()

    assert result == 1  # We expect 1 graded assignment for teacher_id 1

def test_count_assignments_per_student(client, setup_assignments):
    # This should be the SQL query that counts assignments per student
    query = text("""
        SELECT student_id, COUNT(*) FROM assignments 
        GROUP BY student_id
    """)

    result = db.session.execute(query).fetchall()
    
    # Expecting that student_id 1 has 2 assignments and student_id 2 has 1 assignment
    expected_result = {(1, 2), (2, 1)}  # (student_id, count)
    actual_result = {(row[0], row[1]) for row in result}

    assert actual_result == expected_result

def test_grade_count_for_specific_assignment(client, setup_assignments):
    # This should be the SQL query to check the grade of a specific assignment
    query = text("""
        SELECT grade FROM assignments 
        WHERE id = :assignment_id
    """)

    assignment_id = 2
    result = db.session.execute(query, {'assignment_id': assignment_id}).scalar()

    assert result == GradeEnum.C.value  # We expect the grade for assignment_id 2 to be C
