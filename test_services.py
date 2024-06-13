import unittest
from unittest.mock import MagicMock, patch
from datetime import date, datetime
import os
from models import User, Admin, Question, Quiz, Result
from services import UserService, QuizService, ResultService
from custom_exceptions import UserNotFoundException, UserAlreadyExistsException, QuizNotFoundException


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_repo = MagicMock()
        self.admin_repo = MagicMock()
        self.user_service = UserService(self.user_repo, self.admin_repo)
        self.user = User("testuser", "password", date(2000, 1, 1))
        self.admin = Admin("admin", "password")

    def test_authenticate_user_success(self):
        self.user_repo.load.return_value = [self.user]
        self.user_service.users = self.user_repo.load()
        user = self.user_service.authenticate_user("testuser", "password")
        self.assertEqual(user.login, "testuser")

    def test_authenticate_user_failure(self):
        self.user_repo.load.return_value = [self.user]
        self.user_service.users = self.user_repo.load()
        with self.assertRaises(UserNotFoundException):
            self.user_service.authenticate_user("wronguser", "password")

    def test_authenticate_admin_success(self):
        self.admin_repo.load.return_value = [self.admin]
        self.user_service.admins = self.admin_repo.load()
        admin = self.user_service.authenticate_admin("admin", "password")
        self.assertEqual(admin.login, "admin")

    def test_authenticate_admin_failure(self):
        self.admin_repo.load.return_value = [self.admin]
        self.user_service.admins = self.admin_repo.load()
        with self.assertRaises(UserNotFoundException):
            self.user_service.authenticate_admin("wrongadmin", "password")

    def test_register_user_success(self):
        self.user_repo.load.return_value = []
        self.user_service.users = self.user_repo.load()
        result = self.user_service.register_user(self.user)
        self.user_repo.save.assert_called_with(self.user)
        self.assertTrue(result)
        self.assertIn(self.user, self.user_service.users)

    def test_register_user_failure(self):
        self.user_repo.load.return_value = [self.user]
        self.user_service.users = self.user_repo.load()
        with self.assertRaises(UserAlreadyExistsException):
            self.user_service.register_user(self.user)


class TestQuizService(unittest.TestCase):
    def setUp(self):
        self.quiz_repo = MagicMock()
        self.quiz_service = QuizService(self.quiz_repo)
        self.quiz = Quiz("Test Quiz")
        self.question = Question("Sample Question?", ["Option 1", "Option 2"], ["Option 1"])
        self.quiz.add_question(self.question)

    def test_load_all_quizzes(self):
        self.quiz_repo.get_all_quiz_files.return_value = ["quiz_test.json"]
        self.quiz_repo.load.return_value = self.quiz
        quizzes = self.quiz_service.load_all_quizzes()
        self.assertEqual(len(quizzes), 1)
        self.assertEqual(quizzes[0].title, "Test Quiz")

    def test_get_quiz_by_title_success(self):
        self.quiz_service.quizzes = [self.quiz]
        quiz = self.quiz_service.get_quiz_by_title("Test Quiz")
        self.assertEqual(quiz.title, "Test Quiz")

    def test_get_quiz_by_title_failure(self):
        self.quiz_service.quizzes = [self.quiz]
        with self.assertRaises(QuizNotFoundException):
            self.quiz_service.get_quiz_by_title("Non-existent Quiz")

    def test_get_mixed_quiz_questions(self):
        self.quiz_service.quizzes = [self.quiz]
        questions = self.quiz_service.get_mixed_quiz_questions()
        self.assertTrue(len(questions) <= 20)
        self.assertIn(self.question, questions)

    def test_save_quiz(self):
        self.quiz_repo.quizzes_dir = "test_quizzes"
        expected_filepath = os.path.join(self.quiz_repo.quizzes_dir, "quiz_test quiz.json")
        self.quiz_service.save_quiz(self.quiz)
        self.quiz_repo.save.assert_called_with(self.quiz, expected_filepath)


class TestResultService(unittest.TestCase):
    def setUp(self):
        self.result_repo = MagicMock()
        self.result_service = ResultService(self.result_repo)
        self.user = User("testuser", "password", date(2000, 1, 1))
        self.quiz = Quiz("Test Quiz")
        self.result = Result(self.user, self.quiz, 10)

    @patch("datetime.datetime")
    def test_save_result(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 6, 12, 12, 0, 0)
        self.result_service.save_result(self.result)
        self.result_repo.save.assert_called()

    def test_get_user_results(self):
        self.result_repo.load.return_value = [self.result.to_dict()]
        results = self.result_service.get_user_results(self.user, [self.quiz])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["user"], "testuser")

    def test_get_top_results(self):
        self.result_repo.load.return_value = [self.result.to_dict()]
        top_results = self.result_service.get_top_results("Test Quiz")
        self.assertEqual(len(top_results), 1)
        self.assertEqual(top_results[0]["quiz"], "Test Quiz")

    def test_get_total_top_results(self):
        self.result_repo.load.return_value = [self.result.to_dict()]
        top_results = self.result_service.get_total_top_results()
        self.assertEqual(len(top_results), 1)
        self.assertEqual(top_results[0]["user"], "testuser")


if __name__ == '__main__':
    unittest.main()

