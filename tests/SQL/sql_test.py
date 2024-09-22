import random
from sqlalchemy import text
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def create_n_graded_assignments_for_teacher(number: int = 0, teacher_id: int = 1) -> int:
    with app.app_context():  # Ensure you're within the app context
        # Count existing grade A assignments for the teacher
        grade_a_counter: int = Assignment.query.filter(
            Assignment.teacher_id == teacher_id,
            Assignment.grade == GradeEnum.A
        ).count()

        # Create new assignments
        for _ in range(number):
            grade = random.choice(list(GradeEnum))
            assignment = Assignment(
                teacher_id=teacher_id,
                student_id=1,  # Adjust as necessary to match your student IDs
                grade=grade,
                content='test content',
                state=AssignmentStateEnum.GRADED
            )
            db.session.add(assignment)
            if grade == GradeEnum.A:
                grade_a_counter += 1

        db.session.commit()  # Commit the session once after adding all assignments

    return grade_a_counter

def test_get_assignments_in_graded_state_for_each_student():
    with app.app_context():  # Ensure you're within the app context
        # Set assignments to graded for the student
        submitted_assignments = Assignment.query.filter(Assignment.student_id == 1).all()
        for assignment in submitted_assignments:
            assignment.state = AssignmentStateEnum.GRADED
        db.session.commit()  # Commit changes

        expected_result = [(1, 3)]  # Replace with your expected result format

        with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
            sql = fo.read()

        # Execute the SQL query and compare results
        sql_result = db.session.execute(text(sql)).fetchall()
        for itr, result in enumerate(expected_result):
            assert result[0] == sql_result[itr][0]

def test_get_grade_A_assignments_for_teacher_with_max_grading():
    with app.app_context():  # Ensure you're within the app context
        with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
            sql = fo.read()

        # Create graded assignments for teacher 1
        grade_a_count_1 = create_n_graded_assignments_for_teacher(5)
        
        # Execute the SQL query and check the count of grade A assignments
        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_1 == sql_result[0][0]

        # Create graded assignments for teacher 2
        grade_a_count_2 = create_n_graded_assignments_for_teacher(10, 2)
        
        # Execute the SQL query again and check the count of grade A assignments
        sql_result = db.session.execute(text(sql)).fetchall()
        assert grade_a_count_2 == sql_result[0][0]

# Optionally, include a main block to run tests if needed
if __name__ == "__main__":
    pytest.main()
