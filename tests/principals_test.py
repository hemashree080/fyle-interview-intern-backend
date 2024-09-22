import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():  # Ensure the application context is available
            yield client

@pytest.fixture
def h_principal():
    # Set up the headers for the principal user
    return {'X-Principal': '{"principal_id": 1, "user_id": 5}'}

@pytest.fixture
def setup_assignments():
    """Fixture to set up test assignments in the database."""
    with app.app_context():
        # Clear existing assignments for clean setup
        db.session.query(Assignment).delete()
        # Create test assignments with known IDs (4 and 5)
        assignment1 = Assignment(id=4, teacher_id=1, student_id=1, grade=GradeEnum.C, state=AssignmentStateEnum.GRADED)
        assignment2 = Assignment(id=5, teacher_id=1, student_id=1, grade=GradeEnum.DRAFT, state=AssignmentStateEnum.DRAFT)
        db.session.add(assignment1)
        db.session.add(assignment2)
        db.session.commit()

def test_get_assignments(client, h_principal, setup_assignments):
    """Test to get assignments for a principal."""
    response = client.get('/principal/assignments', headers=h_principal)

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

def test_grade_assignment_draft_assignment(client, h_principal, setup_assignments):
    """
    Failure case: If an assignment is in Draft state, it cannot be graded by the principal.
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,  # Ensure this assignment exists and is in Draft state
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400
    assert response.json['message'] == 'Assignment cannot be graded while in Draft state.'

def test_grade_assignment(client, h_principal, setup_assignments):
    """Test to grade an assignment."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,  # Ensure this assignment exists
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C.value

def test_regrade_assignment(client, h_principal, setup_assignments):
    """Test to re-grade an assignment."""
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,  # Ensure this assignment exists
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B.value

# Optionally, include a main block to run tests if needed
if __name__ == "__main__":
    pytest.main()
