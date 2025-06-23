from models import Student, Course, Flashcard, Exam

# Standard library imports

# Remote library imports
from flask import request
from flask_restful import Resource

# Local imports
from config import app, db, api
# Add your model imports

class Students(Resource):
    def get(self):
        students = [s.to_dict(rules('-exams', '-flashcards', )) for s in Student.query.all()]

# Views go here!

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)

