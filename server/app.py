from models import Student, Course, Flashcard, Exam
from flask import request, make_response, Flask, jsonify, session

# Standard library imports

# Remote library imports
from flask import request
from flask_restful import Resource

# Local imports
from config import app, db, api
# Add your model imports

class Students(Resource):
    def get(self):
        students = [s.to_dict(rules=('-exams', '-flashcards', )) for s in Student.query.all()]
        return make_response(students, 200)
    
    def post(self):
        req_data = request.get_json()
        try:
            student = Student(**req_data) #type: ignore
            db.session.add(student)
            db.session.commit()
            return make_response(student.to_dict(), 201)
        except ValueError as e:
            return make_response({'error': str(e)}, 400)
        
class Courses(Resource):
    def get(self):
        courses = [c.to_dict(rules=('-exams', '-flashcards', )) for c in Course.query.all()]
        return make_response(courses, 200)
    
    def post(self):
        req_data = request.get_json()
        try:
            course = Course(**req_data) #type: ignore
            db.session.add(course)
            db.session.commit()
            return make_response(course.to_dict(), 201)
        except ValueError as e:
            return make_response({'error': str(e)}, 400)

# Views go here!

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)

