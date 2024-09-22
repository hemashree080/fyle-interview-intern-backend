import random
from sqlalchemy import text
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def create_n_graded_assignments_for_teacher(number: int = 0, teacher_id: int = 1) -> int:
    with app.app_context():
        grade_a_counter: int = Assignment.query.filter(
            Assignment.teacher_id == teacher_id,
            Assignment.grade == GradeEnum.A
        ).count()

        for _ in range(number):
            grade = random.choice(list(GradeEnum))
            assignment = Assignment(
                teacher_id=teacher_id,
                student_id=random.randint(1, 10),  # Random student ID for diversity
                grade=grade,
                content='test content',
                state=AssignmentStateEnum.GRADED
            )
            db.session.add(assignment)
            if grade == GradeEnum.A:
                grade_a_counter += 1

        db.session.commit()

    return grade_a_counter

def test_get_assignments_in_graded_state_for_each_student():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()

        # Create 5 graded assignments for student_id=1
        for _ in range(5):
            assignment = Assignment(
                student_id=1,
                teacher_id=random.randint(1, 3),  # Random teacher ID for diversity
                state=AssignmentStateEnum.GRADED,
                grade=random.choice(list(GradeEnum)),  # Assign random grade
                content='test content'
            )
            db.session.add(assignment)
        db.session.commit()

        expected_result = [(1, 5)]

        with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
            sql = fo.read()

        sql_result = db.session.execute(text(sql)).fetchall()
        assert expected_result[0][1] == sql_result[0][1]  # Compare the counts directly

def test_get_grade_A_assignments_for_teacher_with_max_grading():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()

        # Create 5 graded assignments for teacher_id=1
        grade_a_count_1 = create_n_graded_assignments_for_teacher(5)

        with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
            sql = fo.read()

        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_1 == sql_result[0][0], "Grade A count mismatch for teacher_id=1"

        # Create 10 graded assignments for teacher_id=2
        grade_a_count_2 = create_n_graded_assignments_for_teacher(10, 2)

        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_2 == sql_result[0][0], "Grade A count mismatch for teacher_id=2"
