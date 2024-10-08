import pytest
from core import app, db
from core.models.assignments import Assignment, AssignmentStateEnum

@pytest.fixture(scope='module')
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(scope='function', autouse=True)
def setup_database():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def h_student_1():
    return {'X-Student': '{"student_id": 1, "user_id": 1}'}

@pytest.fixture
def setup_assignments():
    with app.app_context():
        db.session.query(Assignment).delete()
        db.session.commit()
        assignments = [
            Assignment(id=1, student_id=1, content='Assignment 1', state=AssignmentStateEnum.DRAFT),
            Assignment(id=2, student_id=1, content='Assignment 2', state=AssignmentStateEnum.DRAFT),
            Assignment(id=3, student_id=2, content='Assignment 3', state=AssignmentStateEnum.DRAFT),
        ]
        db.session.bulk_save_objects(assignments)
        db.session.commit()

def test_get_assignments_student_1(client, h_student_1, setup_assignments):
    response = client.get('/student/assignments', headers=h_student_1)
    assert response.status_code == 200
    data = response.json['data']
    assert len(data) > 0
    for assignment in data:
        assert assignment['student_id'] == 1

def test_post_assignment_null_content(client, h_student_1):
    response = client.post('/student/assignments', headers=h_student_1, json={'content': None})
    assert response.status_code == 400

def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'
    response = client.post('/student/assignments', headers=h_student_1, json={'content': content})
    assert response.status_code == 201
    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == AssignmentStateEnum.DRAFT.value
    assert data['teacher_id'] is None

def test_submit_assignment_student_1(client, h_student_1, setup_assignments):
    response = client.post('/student/assignments/submit', headers=h_student_1, json={'id': 2, 'teacher_id': 2})
    assert response.status_code == 200
    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == AssignmentStateEnum.SUBMITTED.value
    assert data['teacher_id'] == 2

def test_assignment_resubmit_error(client, h_student_1, setup_assignments):
    client.post('/student/assignments/submit', headers=h_student_1, json={'id': 2, 'teacher_id': 2})
    response = client.post('/student/assignments/submit', headers=h_student_1, json={'id': 2, 'teacher_id': 2})
    assert response.status_code == 400
    assert response.json['error'] == 'FyleError'
    assert response.json["message"] == 'only a draft assignment can be submitted'
