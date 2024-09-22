import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def h_principal():
    return {'X-Principal': '{"principal_id": 1, "user_id": 5}'}

@pytest.fixture
def setup_assignments():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()
        assignment1 = Assignment(id=4, teacher_id=1, student_id=1, grade=GradeEnum.C, state=AssignmentStateEnum.GRADED)
        assignment2 = Assignment(id=5, teacher_id=1, student_id=1, grade=GradeEnum.DRAFT, state=AssignmentStateEnum.DRAFT)
        db.session.add(assignment1)
        db.session.add(assignment2)
        db.session.commit()

def test_get_assignments(client, h_principal, setup_assignments):
    response = client.get('/principal/assignments', headers=h_principal)
    assert response.status_code == 200
    data = response.json.get('data', [])
    assert len(data) > 0
    assert all(item['state'] == AssignmentStateEnum.GRADED.value for item in data if item['grade'] != GradeEnum.DRAFT.value)

def test_grade_draft_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 5, 'grade': GradeEnum.A.value},
        headers=h_principal
    )
    assert response.status_code == 400
    assert response.json['message'] == "Cannot grade a draft assignment"

def test_grade_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 4, 'grade': GradeEnum.C.value},
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C.value

def test_regrade_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 4, 'grade': GradeEnum.B.value},
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B.value

def test_grade_assignment_invalid_id(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 999, 'grade': GradeEnum.A.value},  # Non-existent ID
        headers=h_principal
    )
    assert response.status_code == 404
    assert response.json['message'] == "Assignment not found"

def test_grade_assignment_invalid_grade(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 4, 'grade': 'INVALID_GRADE'},  # Invalid grade value
        headers=h_principal
    )
    assert response.status_code == 400
    assert response.json['message'] == "Invalid grade value"
