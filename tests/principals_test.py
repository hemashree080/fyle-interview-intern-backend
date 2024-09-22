import pytest
from core import app  # Import your Flask app
from core.models.assignments import AssignmentStateEnum, GradeEnum

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():  # Ensure the application context is available
            yield client

@pytest.fixture
def h_principal():
    # Set up the headers for the principal user
    return {'X-Principal': '{"principal_id": 1, "user_id": 5}'}

def test_get_assignments(client, h_principal):
    """Test to get assignments for a principal."""
    response = client.get('/principal/assignments', headers=h_principal)

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

def test_grade_assignment_draft_assignment(client, h_principal):
    """
    Failure case: If an assignment is in Draft state, it cannot be graded by principal.
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

def test_grade_assignment(client, h_principal):
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

def test_regrade_assignment(client, h_principal):
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
