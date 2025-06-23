from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields, SQLAlchemyAutoSchema

from config import db

class Student(db.Model, SerializerMixin):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String) 
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, username, password):
        self.username = username
        self._password_hash = password

    exams = db.relationship('Exam', back_populates='student', cascade='all, delete-orphan')
    flashcards = db.relationship('Flashcard', back_populates='student', cascade='all, delete-orphan')
    courses = association_proxy('exams', 'courses') #Could be an error in here

    serialize_rules = ('-exams.student', '-flashcards.student', '-exams,student.exams', '-flashcards.student.flashcards', '-_password_hash')

class StudentSchema(SQLAlchemyAutoSchema):
    class Meta:
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

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    def __init__(self, title):
        self.title = title