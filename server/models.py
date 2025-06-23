from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import fields
from config import bcrypt, db
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class Student(db.Model, SerializerMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String) 
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

  #  def __init__(self, username, password):
   #     self.username = username
  #      self._password_hash = password

    @validates("username")
    def validate_username(self, key, value):
        if not isinstance(value, str) or not (3 <= len(value) <= 15):
            raise ValueError("Username must be present and between 3 and 15 characters.")
        return value
    
    @hybrid_property
    def password(self): # type: ignore
        raise AttributeError('Password hashes may not be viewed.')

    @password.setter # type: ignore
    def password(self, password):
        if password:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            self._password_hash = password_hash
        else:
            raise ValueError("Password must not be empty.")

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    exams = db.relationship('Exam', back_populates='student', cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', back_populates='student', cascade='all, delete-orphan')
    courses = association_proxy('exams', 'course') #Could be an error in here

    serialize_rules = ('-exams.student', '-flashcards.student', '-exams,student.exams', '-flashcards.student.flashcards', '-_password_hash')

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta: #type: ignore
        model = Student
        load_instance = True
        include_relationships = True
        include_fk = True
        exclude = ('_password_hash',)
    
    # Related objects (exams, flashcards, and courses)
    exams = fields.Nested('ExamSchema', many=True, exclude=('student',))  # Nested Exam Schema, exclude student field to avoid circular reference
    flashcards = fields.Nested('FlashcardSchema', many=True, exclude=('student',))  # Nested Flashcard Schema
    courses = fields.List(fields.Str())  # Assuming 'courses' is a list of strings (could change based on actual data)

class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

  #  id = db.Column(db.Integer, primary_key=True)
  #  title = db.Column(db.String, unique=True, nullable=False)
  #  created_at = db.Column(db.DateTime, server_default=db.func.now())
  #  updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, title):
        self.title = title

    exams = db.relationship('Exam', back_populates='course', cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', back_populates='course', cascade='all, delete-orphan')
    students = association_proxy('exams', 'student') #Could be an error in here
    serialize_rules = ('-exams.student', '-flashcards.student', '-exams,student.exams', '-flashcards.student.flashcards', '-_password_hash')

class CourseSchema(SQLAlchemyAutoSchema):
    class Meta: #type: ignore
        model = Course
        load_instance = True
        include_relationships = True
        include_fk = True
        
    exams = fields.Nested('ExamSchema', many = True, exclude=('student',))
    flashcards = fields.Nested('FlashcardSchema', many = True, exclude=('student',))
    students = fields.List(fields.Str())

class Flashcard(db.Model, SerializerMixin):
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String, nullable=False)
    back = db.Column(db.String, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

#     def __init__(self, front, back, course_id=None, student_id=None):
#        self.front = front
 #       self.back = back
#        self.student_id = student_id 
 #       self.course_id = course_id 

    course = db.relationship('Course', back_populates='flashcards')
    student = db.relationship('Student', back_populates='flashcards')

class FlashcardSchema(SQLAlchemyAutoSchema):
    class Meta: #type: ignore
        model = Flashcard
        load_instance = True
        include_relationships = True
        include_fk = True
        
    student = fields.Nested('StudentSchema', only=('id', 'username'))  # avoid circular refs
    course = fields.Nested('CourseSchema', only=('id', 'title'))

class Exam(db.Model, SerializerMixin):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    file_url = db.Column(db.String, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    course = db.relationship('Course', back_populates='exams')
    student = db.relationship('Student', back_populates='exams')

class ExamSchema(SQLAlchemyAutoSchema):
    class Meta: #type: ignore
        model = Exam
        load_instance = True
        include_relationships = True
        include_fk = True
        
    student = fields.Nested('StudentSchema', only=('id', 'username')) 
    course = fields.Nested('CourseSchema', only=('id', 'title'))
    file_url = fields.String()