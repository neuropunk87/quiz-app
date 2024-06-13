import unittest
from unittest.mock import mock_open, patch, MagicMock
from datetime import date, datetime
import os
from models import User, Admin, Quiz, Question, Result
from repositories import UserRepository, AdminRepository, QuizRepository, ResultRepository
from custom_exceptions import SavingErrorException


class TestUserRepository(unittest.TestCase):
    def setUp(self):
        self.filepath = "test_users.json"
        self.user_repo = UserRepository(self.filepath)
        self.user = User("testuser", "password", date(2000, 1, 1))

    @patch("builtins.open", new_callable=mock_open, read_data='[]')
    def test_load_empty(self, mock_file):
        users = self.user_repo.load()
        self.assertEqual(users, [])
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", new_callable=mock_open, read_data='[{"login": "testuser", "password": "password", '
                                                              '"birth_date": "2000-01-01"}]')
    def test_load_non_empty(self, mock_file):
        users = self.user_repo.load()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].login, "testuser")
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save(self, mock_json_dump, mock_file):
        self.user_repo.save(self.user)
        mock_file.assert_called_with(self.filepath, 'w')
        mock_json_dump.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_all(self, mock_json_dump, mock_file):
        users = [self.user]
        self.user_repo.save_all(users)
        mock_file.assert_called_with(self.filepath, 'w')
        mock_json_dump.assert_called_once()


class TestAdminRepository(unittest.TestCase):
    def setUp(self):
        self.filepath = "test_admins.json"
        self.admin_repo = AdminRepository(self.filepath)
        self.admin = Admin("admin", "password")

    @patch("builtins.open", new_callable=mock_open, read_data='[]')
    def test_load_empty(self, mock_file):
        admins = self.admin_repo.load()
        self.assertEqual(admins, [])
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", new_callable=mock_open, read_data='[{"login": "admin", "password": "password"}]')
    def test_load_non_empty(self, mock_file):
        admins = self.admin_repo.load()
        self.assertEqual(len(admins), 1)
        self.assertEqual(admins[0].login, "admin")
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save(self, mock_json_dump, mock_file):
        self.admin_repo.save(self.admin)
        mock_file.assert_called_with(self.filepath, 'w')
        mock_json_dump.assert_called_once()


class TestQuizRepository(unittest.TestCase):
    def setUp(self):
        self.quizzes_dir = "test_quizzes"
        self.quiz_repo = QuizRepository(self.quizzes_dir)
        self.quiz = Quiz("Test Quiz")
        self.question = Question("Sample Question?", ["Option 1", "Option 2"], ["Option 1"])
        self.quiz.add_question(self.question)

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_quiz_not_found(self, mock_file):
        quiz = self.quiz_repo.load("non_existent_quiz.json")
        self.assertIsNone(quiz)
        mock_file.assert_called_with("non_existent_quiz.json", 'r')

    @patch("builtins.open", new_callable=mock_open, read_data='{"title": "Test Quiz", "questions": '
                                                              '[{"text": "Sample Question?", '
                                                              '"options": ["Option 1", "Option 2"], '
                                                              '"correct_answers": ["Option 1"]}] }')
    def test_load_quiz(self, mock_file):
        quiz = self.quiz_repo.load("quiz_test.json")
        self.assertEqual(quiz.title, "Test Quiz")
        self.assertEqual(len(quiz.questions), 1)
        self.assertEqual(quiz.questions[0].text, "Sample Question?")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_quiz(self, mock_json_dump, mock_file):
        filepath = os.path.join(self.quizzes_dir, "quiz_test.json")
        self.quiz_repo.save(self.quiz, filepath)
        mock_file.assert_called_with(filepath, 'w')
        mock_json_dump.assert_called_once()

    @patch("os.listdir", return_value=["quiz1.json", "quiz2.json"])
    def test_get_all_quiz_files(self, mock_listdir):
        quiz_files = self.quiz_repo.get_all_quiz_files()
        expected_files = [os.path.join(self.quizzes_dir, "quiz1.json"), os.path.join(self.quizzes_dir, "quiz2.json")]
        self.assertEqual(quiz_files, expected_files)


class TestResultRepository(unittest.TestCase):
    def setUp(self):
        self.result_repo = ResultRepository()
        self.filepath = "test_results.json"
        self.user = User(login="testuser", password="password", birth_date=datetime(2000, 1, 1))
        self.quiz = Quiz(title="testquiz")
        self.result = Result(user=self.user, quiz=self.quiz, score=100)

    @patch("builtins.open", new_callable=mock_open,
           read_data='[{"user": "testuser", "quiz": "testquiz", "score": 100, "date": "2024-01-01T00:00:00"}]')
    def test_load_results(self, mock_file):
        results = self.result_repo.load(self.filepath)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user'], "testuser")
        self.assertEqual(results[0]['quiz'], "testquiz")
        self.assertEqual(results[0]['score'], 100)
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_load_results_file_not_found(self, mock_file):
        results = self.result_repo.load(self.filepath)
        self.assertEqual(results, [])
        mock_file.assert_called_with(self.filepath, 'r')

    @patch("builtins.open", new_callable=mock_open, read_data='invalid_json')
    def test_load_results_json_decode_error(self, mock_file):
        with patch("builtins.print") as mock_print:
            results = self.result_repo.load(self.filepath)
            self.assertEqual(results, [])
            mock_print.assert_called_with(f"Error decoding JSON from '{self.filepath}'.")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_result(self, mock_json_dump, mock_file):
        self.result_repo.load = MagicMock(return_value=[])
        # self.result_repo.load = patch("repositories.ResultRepository.load", return_value=[]).start()
        self.result_repo.save(self.result, self.filepath)
        mock_file.assert_called_with(self.filepath, 'w')
        mock_json_dump.assert_called_once_with([self.result.to_dict()], mock_file(), indent=4)
        # mock_json_dump.assert_called_once()
        # patch.stopall()

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump", side_effect=SavingErrorException("Mock Saving Error"))
    def test_save_result_saving_error(self, mock_json_dump, mock_file):
        with patch("builtins.print") as mock_print:
            self.result_repo.save(self.result, self.filepath)
            mock_print.assert_called_with(f"Error saving result to '{self.filepath}': Mock Saving Error.")
            mock_json_dump.assert_called_once()


if __name__ == '__main__':
    unittest.main()

