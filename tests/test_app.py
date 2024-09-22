import pytest
from app import create_app, db, Assignment

@pytest.fixture(scope='module')
def app():
    app = create_app()
    with app.app_context():
        db.create_all()  # Create the database tables
        yield app  # Allow tests to run
        db.drop_all()  # Clean up after tests

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def setup_assignments(app):
    with app.app_context():
        db.session.query(Assignment).delete()  # Clear previous assignments
        db.session.commit()
        
        # Add test assignments
        assignment1 = Assignment(content='Assignment 1', teacher_id=1, student_id=1)
        assignment2 = Assignment(content='Assignment 2', teacher_id=1, student_id=2)
        db.session.add_all([assignment1, assignment2])
        db.session.commit()

def test_get_assignments(client, setup_assignments):
    response = client.get('/teacher/assignments')
    assert response.status_code == 200
    assert len(response.json) == 2  # Expecting 2 assignments

def test_grade_assignment(client, setup_assignments):
    response = client.post('/teacher/assignments/grade', json={"id": 1, "grade": "A"})
    assert response.status_code == 200
    assert response.json['message'] == 'Assignment graded successfully'

def test_grade_assignment_not_found(client):
    response = client.post('/teacher/assignments/grade', json={"id": 999, "grade": "A"})
    assert response.status_code == 404
    assert response.json['error'] == 'Assignment not found'
