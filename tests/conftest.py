import pytest
import json
from core import app  # Import your Flask app

@pytest.fixture
def client():
    """Fixture for the test client."""
    with app.test_client() as client:
        with app.app_context():  # Ensure application context is available
            yield client

@pytest.fixture
def h_student_1():
    """Fixture for headers of student 1."""
    headers = {
        'X-Principal': json.dumps({
            'student_id': 1,
            'user_id': 1
        })
    }
    return headers

@pytest.fixture
def h_student_2():
    """Fixture for headers of student 2."""
    headers = {
        'X-Principal': json.dumps({
            'student_id': 2,
            'user_id': 2
        })
    }
    return headers

@pytest.fixture
def h_teacher_1():
    """Fixture for headers of teacher 1."""
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 1,
            'user_id': 3
        })
    }
    return headers

@pytest.fixture
def h_teacher_2():
    """Fixture for headers of teacher 2."""
    headers = {
        'X-Principal': json.dumps({
            'teacher_id': 2,
            'user_id': 4
        })
    }
    return headers

@pytest.fixture
def h_principal():
    """Fixture for headers of the principal."""
    headers = {
        'X-Principal': json.dumps({
            'principal_id': 1,
            'user_id': 5
        })
    }
    return headers
