import random
from sqlalchemy import text
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def create_n_graded_assignments_for_teacher(number: int = 0, teacher_id: int = 1) -> int:
    with app.app_context():  # Ensure you're within the app context
        grade_a_counter: int = Assignment.filter(
            Assignment.teacher_id == teacher_id,
            Assignment.grade == GradeEnum.A
        ).count()

        for _ in range(number):
            grade = random.choice(list(GradeEnum))
            assignment = Assignment(
                teacher_id=teacher_id,
                student_id=1,
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
    with app.app_context():  # Ensure you're within the app context
        submitted_assignments = Assignment.filter(Assignment.student_id == 1)

        for assignment in submitted_assignments:
            assignment.state = AssignmentStateEnum.GRADED

        db.session.flush()
        db.session.commit()

        expected_result = [(1, 3)]  # Update based on your expectations

        with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
            sql = fo.read()

        sql_result = db.session.execute(text(sql)).fetchall()
        for itr, result in enumerate(expected_result):
            assert result[0] == sql_result[itr][0]


def test_get_grade_A_assignments_for_teacher_with_max_grading():
    with app.app_context():  # Ensure you're within the app context
        with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
            sql = fo.read()

        grade_a_count_1 = create_n_graded_assignments_for_teacher(5)
        
        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_1 == sql_result[0][0]

        grade_a_count_2 = create_n_graded_assignments_for_teacher(10, 2)

        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_2 == sql_result[0][0]
