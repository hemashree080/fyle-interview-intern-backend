from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    teacher_id = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)

@app.route('/teacher/assignments', methods=['GET'])
def get_assignments():
    assignments = Assignment.query.all()
    return jsonify([{'id': a.id, 'content': a.content} for a in assignments])

@app.route('/teacher/assignments/grade', methods=['POST'])
def grade_assignment():
    data = request.json
    assignment = Assignment.query.get(data['id'])
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404
    # Example grading logic could go here
    return jsonify({'message': 'Assignment graded successfully'}), 200

def create_app():
    db.create_all()
    return app

if __name__ == '__main__':
    app.run(debug=True)
