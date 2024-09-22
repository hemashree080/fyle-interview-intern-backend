import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

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
        assignment1 = Assignment(id=1, teacher_id=1, student_id=1, content='Assignment 1', state=AssignmentStateEnum.SUBMITTED)
        assignment2 = Assignment(id=2, teacher_id=1, student_id=1, content='Assignment 2', state=AssignmentStateEnum.DRAFT)
        assignment3 = Assignment(id=3, teacher_id=2, student_id=2, content='Assignment 3', state=AssignmentStateEnum.SUBMITTED)
        
        db.session.add(assignment1)
        db.session.add(assignment2)
        db.session.add(assignment3)
        db.session.commit()

def test_get_assignments_teacher_1(client, h_teacher_1, setup_assignments):
    response = client.get('/teacher/assignments', headers=h_teacher_1)

    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1

def test_get_assignments_teacher_2(client, h_teacher_2, setup_assignments):
    response = client.get('/teacher/assignments', headers=h_teacher_2)

    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']

def test_grade_assignment_cross(client, h_teacher_2):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={"id": 1, "grade": "A"}
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'

def test_grade_assignment_bad_grade(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 1, "grade": "AB"}
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'

def test_grade_assignment_bad_assignment(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 100000, "grade": "A"}
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'

def test_grade_assignment_draft_assignment(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={"id": 2, "grade": "A"}
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'
