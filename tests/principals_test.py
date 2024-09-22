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
        assignments = [
            Assignment(id=1, teacher_id=1, student_id=1, grade=GradeEnum.C, state=AssignmentStateEnum.GRADED),
            Assignment(id=2, teacher_id=1, student_id=1, grade=GradeEnum.DRAFT, state=AssignmentStateEnum.DRAFT)
        ]
        db.session.bulk_save_objects(assignments)
        db.session.commit()

def test_get_assignments_in_graded_state_for_each_student(client, h_principal, setup_assignments):
    response = client.get('/principal/assignments', headers=h_principal)
    assert response.status_code == 200
    data = response.json['data']
    assert len(data) > 0

def test_grade_assignment_draft_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 2, 'grade': GradeEnum.A.value},
        headers=h_principal
    )
    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'

def test_grade_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={'id': 1, 'grade': GradeEnum.C.value},
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C.value
