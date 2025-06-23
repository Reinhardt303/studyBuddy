from models import Student, Course, Flashcard, Exam
from flask import request, make_response, Flask, jsonify, session
from config import app, db, api
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

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
        student_id = session.get('student_id')
        if not student_id:
            return make_response({'error': 'Please log in'})
        
        student = Student.query.get(student_id)
        if not student:
            return make_response({'error': 'Student not found'})
        courses = [c.to_dict(rules=('-exams', '-flashcards', )) for c in student.courses]
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

class ExamsByStudentsCourse(Resource):
    def get(self, id):
        student_id = session.get('student_id')
        if not student_id:
            return {'error': 'Please log in'}, 401
        
        course = Course.query.get(id)
        if not course:
            return {'error': 'Course not found'}
        
        exams = [e.to_dict(rules=('-student', '-course')) for e in course.exams if e.student_id == student_id]

        return {'exams': exams}, 200
    
class FlashcardsByStudentsCourse(Resource):
    def get(self, id):
        student_id = session.get('student_id')
        if not student_id:
            return {'error': 'Please log in'}, 401
        
        course = Course.query.get(id)
        if not course:
            return {'error': 'Course not found'}, 404
        flashcards = [f.to_dict(rules=('-student', '-course')) for f in course.flashcards if f.student_id == student_id]

        return {'flashcards': flashcards}, 200

api.add_resource(Courses, '/courses')
api.add_resource(ExamsByStudentsCourse, '/courses/<int:course_id>/exams')
api.add_resource(FlashcardsByStudentsCourse, '/courses/<int:course_id>/flashcards')

class Signup(Resource):
    def post(self):
        req_json = request.get_json()

        if req_json.get("password") != req_json.get("password_confirmation"): # type: ignore
            return {"error": "Password confirmation does not match password"}, 400
        
        try:
            student = Student(
                username = req_json["username"], # type: ignore
                password = req_json.get("password"), # type: ignore
            )
            db.session.add(student)
            db.session.commit()
            session['student_id'] = student.id
            return {
                'id': student.id,
                'username': student.username,
            }, 201

        except (KeyError, ValueError, IntegrityError) as e:
            db.session.rollback()
            return {"error": f"Invalid signup: {str(e)}"}, 422
        
class CheckSession(Resource):
    def get(self):
        student_id = session.get('student_id')
        if student_id:
            student = Student.query.get(student_id)
            if student:
                return {
                    'id': student.id,
                    'username': student.username,
                }, 200
        return {'error': "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        req_json = request.get_json()

        if not req_json or 'username' not in req_json or 'password' not in req_json:
            return {'error': 'Missing username or password'}, 400

        student = Student.query.filter_by(username=req_json['username']).first()

        if student and student.authenticate(req_json['password']):
            session['student_id'] = student.id
            return {
                'id': student.id,
                'username': student.username,
            }, 200
        else:
            return {'error': 'Invalid username or password'}, 401
        
class Logout(Resource):
    def delete(self):
        student_id = session.get('student_id')
        if student_id:
            session.pop('student_id', None)
            return {}, 204
        else:
            return {'error': 'Not logged in'}, 401 
        
class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204
    
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(ClearSession, '/clear', endpoint='clear')

@app.route('/')
def index():
    return '<h1>Project Server</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)

