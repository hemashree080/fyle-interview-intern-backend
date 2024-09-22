import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def h_teacher_1():
    return {'X-Teacher': '{"teacher_id": 1, "user_id": 1}'}

@pytest.fixture
def h_teacher_2():
    return {'X-Teacher': '{"teacher_id": 2, "user_id": 2}'}

@pytest.fixture
def setup_assignments():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()
        assignments = [
            Assignment(id=1, teacher_id=1, student_id=1, content='Assignment 1', state=AssignmentStateEnum.SUBMITTED),
            Assignment(id=2, teacher_id=1, student_id=1, content='Assignment 2', state=AssignmentStateEnum.DRAFT),
            Assignment(id=3, teacher_id=2, student_id=2, content='Assignment 3', state=AssignmentStateEnum.SUBMITTED)
        ]
        db.session.bulk_save_objects(assignments)
        db.session.commit()

def test_get_assignments_teacher_1(client, h_teacher_1, setup_assignments):
    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    data = response.json.get('data', [])
    assert len(data) > 0
    for assignment in data:
        assert assignment['teacher_id'] == 1

def test_get_assignments_teacher_2(client, h_teacher_2, setup_assignments):
    response = client.get('/teacher/assignments', headers=h_teacher_2)
    assert response.status_code == 200
    data = response.json.get('data', [])
    assert len(data) > 0
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

def test_grade_assignment_cross(client, h_teacher_2):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={"id": 1, "grade": "A"}
    )
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert data['message'] == 'You cannot grade this assignment.'

def test_grade_assignment_bad_grade(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 1, "grade": "AB"}
    )
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'ValidationError'
    assert data['message'] == 'Invalid grade value.'

def test_grade_assignment_bad_assignment(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 100000, "grade": "A"}
    )
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'FyleError'
    assert data['message'] == 'Assignment not found.'

def test_grade_assignment_draft_assignment(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 2, "grade": "A"}
    )
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'FyleError'
    assert data['message'] == 'Only submitted assignments can be graded.'
