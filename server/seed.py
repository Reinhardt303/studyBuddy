from random import randint, choice as rc
from faker import Faker
from app import app
from models import db, Course, Student, Flashcard, Exam
import random

fake = Faker()

def create_students():
    students = []
    for _ in range(20):
        s = Student(
            username=fake.user_name(),
            password = fake.password()
        )
        students.append(s)
    return students

def create_courses():
    courses = []
    course_topics = [
    "Biology", "Psychology", "Philosophy", "Economics", "Computer Science",
    "Mathematics", "Anthropology", "Political Science", "Environmental Studies",
    "Artificial Intelligence", "Game Design", "Machine Learning", "Ethics"
    ]
    prefixes = random.choice(["Intro to", "Foundations of", "Advanced", "Seminar in", "Principles of"])
    for _ in range(25):
        c = Course(
            title=f'{random.choice(prefixes)} {random.choice(course_topics)}'
        )
        courses.append(c)
    return courses

def create_exams(students, courses):
    exams = []
    for _ in range(20):
        e = Exam(
            date=fake.date_this_year(),
            file_url=fake.url(),
            score=randint(65, 100),
            course_id=rc(courses).id,
            student_id=rc(students).id
        )
        exams.append(e)
    return exams

def create_flashcards(students, courses):
    flashcards = []
    course_topic = [
    "Biology", "Psychology", "Philosophy", "Economics", "Computer Science",
    "Mathematics", "Anthropology", "Political Science", "Environmental Studies",
    "Artificial Intelligence", "Game Design", "Machine Learning", "Ethics"
    ]
    for _ in range(40):
        f = Flashcard(
            front = random.choice(course_topic),
            back = fake.sentence(nb_words=8),
            course_id=rc(courses).id,
            student_id=rc(students).id
        )
        flashcards.append(f)
    return flashcards

if __name__ == '__main__':
    with app.app_context():
        print("Clearing existing data...")
        Flashcard.query.delete()
        Exam.query.delete()
        Student.query.delete()
        Course.query.delete()
        db.session.commit()  

        print("Seeding courses...")
        courses = create_courses()
        db.session.add_all(courses)
        db.session.commit()  

        print("Seeding students...")
        students = create_students()
        db.session.add_all(students)
        db.session.commit()  

        print("Seeding exams...")
        exams = create_exams(students, courses)
        db.session.add_all(exams)
        db.session.commit()

        print("Seeding flashcards...")
        flashcards = create_flashcards(students, courses)
        db.session.add_all(flashcards)
        db.session.commit()

        print("Seeding complete.")

