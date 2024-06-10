from datetime import date, datetime


class Question:
    def __init__(self, text: str, options: list, correct_answers: list):
        self.text = text
        self.options = options
        self.correct_answers = correct_answers

    def to_dict(self):
        return {
            "text": self.text,
            "options": self.options,
            "correct_answers": self.correct_answers
        }


class Quiz:
    def __init__(self, title: str):
        self.title = title
        self.questions = []

    def add_question(self, question: Question):
        self.questions.append(question)

    def to_dict(self):
        return {
            "title": self.title,
            "questions": [question.to_dict() for question in self.questions]
        }


class User:
    def __init__(self, login: str, password: str, birth_date: date):
        self.login = login
        self.password = password
        self.birth_date = birth_date

    def to_dict(self):
        return {
            "login": self.login,
            "password": self.password,
            "birth_date": self.birth_date.isoformat()
        }


class Admin:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def to_dict(self):
        return {
            "login": self.login,
            "password": self.password
        }


class Result:
    def __init__(self, user: User, quiz: Quiz, score: int):
        self.user = user
        self.quiz = quiz
        self.score = score
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            "user": self.user.login,
            "quiz": self.quiz.title if self.quiz else "",
            "score": self.score,
            "timestamp": self.timestamp
        }

