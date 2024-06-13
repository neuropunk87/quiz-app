import unittest
from datetime import date, datetime
from models import Question, Quiz, User, Admin, Result


class TestQuestion(unittest.TestCase):
    def setUp(self):
        self.question = Question("Sample Question?", ["Option 1", "Option 2"], ["Option 1"])

    def test_to_dict(self):
        expected_dict = {
            "text": "Sample Question?",
            "options": ["Option 1", "Option 2"],
            "correct_answers": ["Option 1"]
        }
        self.assertEqual(self.question.to_dict(), expected_dict)


class TestQuiz(unittest.TestCase):
    def setUp(self):
        self.quiz = Quiz("Test Quiz")
        self.question = Question("Sample Question?", ["Option 1", "Option 2"], ["Option 1"])
        self.quiz.add_question(self.question)

    def test_add_question(self):
        new_question = Question("New Question?", ["Option A", "Option B"], ["Option A"])
        self.quiz.add_question(new_question)
        self.assertEqual(len(self.quiz.questions), 2)

    def test_to_dict(self):
        expected_dict = {
            "title": "Test Quiz",
            "questions": [self.question.to_dict()]
        }
        self.assertEqual(self.quiz.to_dict(), expected_dict)


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User("testuser", "password", date(2000, 1, 1))

    def test_to_dict(self):
        expected_dict = {
            "login": "testuser",
            "password": "password",
            "birth_date": "2000-01-01"
        }
        self.assertEqual(self.user.to_dict(), expected_dict)


class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.admin = Admin("admin", "password")

    def test_to_dict(self):
        expected_dict = {
            "login": "admin",
            "password": "password"
        }
        self.assertEqual(self.admin.to_dict(), expected_dict)


class TestResult(unittest.TestCase):
    def setUp(self):
        self.user = User("testuser", "password", date(2000, 1, 1))
        self.quiz = Quiz("Test Quiz")
        self.result = Result(self.user, self.quiz, 10)
        self.timestamp = datetime.now().isoformat()

    def test_to_dict(self):
        self.result.date = datetime(2024, 6, 12, 12, 0, 0)
        expected_dict = {
            "user": "testuser",
            "quiz": "Test Quiz",
            "score": 10,
            "timestamp": self.timestamp
        }
        self.assertEqual(self.result.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()

