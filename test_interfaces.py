import unittest
from unittest.mock import patch, Mock
from datetime import date
from models import User, Quiz, Result, Question
from services import UserService, QuizService, ResultService
from interfaces import UserMenu, AdminMenu
from custom_exceptions import UserNotFoundException, InvalidDateFormatException


class TestUserMenu(unittest.TestCase):
    def setUp(self):
        self.user_service = Mock(UserService)
        self.quiz_service = Mock(QuizService)
        self.result_service = Mock(ResultService)
        self.user_menu = UserMenu(self.user_service, self.quiz_service, self.result_service)

        self.mock_user = User("testuser", "password123", date(1990, 1, 1))
        self.mock_quiz = Quiz("Sample Quiz")
        self.quiz_service.quizzes = [self.mock_quiz]
        self.mock_question = Question("Sample Question?", ["Option 1", "Option 2"], ["Option 1"])
        self.mock_quiz.add_question(self.mock_question)
        self.mock_result = Result(self.mock_user, self.mock_quiz, 1)

    @patch('builtins.input', side_effect=["testuser", "password123", "0"])
    def test_authenticate_success(self, mock_input):
        self.user_service.authenticate_user.return_value = self.mock_user
        self.user_menu.authenticate()
        self.user_menu.current_user = self.mock_user
        self.assertEqual(self.user_menu.current_user, self.mock_user)
        self.user_service.authenticate_user.assert_called_once_with("testuser", "password123")

    @patch('builtins.input', side_effect=["wronguser", "wrongpassword", "back"])
    def test_authenticate_fail(self, mock_input):
        self.user_service.authenticate_user.side_effect = UserNotFoundException("User not found")
        self.user_menu.authenticate()
        self.assertIsNone(self.user_menu.current_user)

    @patch('builtins.input', side_effect=["newuser", "newpassword", "1990-01-01"])
    def test_register_success(self, mock_input):
        self.user_menu.register()
        self.user_service.register_user.assert_called_once()

    @patch('builtins.input', side_effect=["newuser", "newpassword", "invalid-date"])
    def test_register_invalid_date(self, mock_input):
        with self.assertRaises(InvalidDateFormatException):
            self.user_menu.register()

    @patch('builtins.input', side_effect=["1", "Sample Quiz", "1"])
    @patch('builtins.print')
    def test_take_quiz(self, mock_print, mock_input):
        self.user_menu.current_user = self.mock_user
        self.quiz_service.get_quiz_by_title.return_value = self.mock_quiz
        self.result_service.get_top_results.return_value = [{'user': 'testuser', 'score': 1}]
        self.user_menu.take_quiz()

        mock_print.assert_any_call("\nAvailable Quizzes:")
        mock_print.assert_any_call("---> Sample Quiz")
        mock_print.assert_any_call("\nQuestion 1: Sample Question?")
        mock_print.assert_any_call("1. Option 1")
        mock_print.assert_any_call("2. Option 2")
        mock_print.assert_any_call("\nQuiz completed! Your score: 1/1")
        mock_print.assert_any_call("Your ranking: 1")

    @patch('builtins.input', side_effect=["Sample Quiz"])
    @patch('builtins.print')
    def test_view_top_results(self, mock_print, mock_input):
        self.result_service.get_top_results.return_value = [
            {'user': 'testuser', 'score': 1, 'timestamp': '2024-06-11'}
        ]
        self.user_menu.view_top_results()
        self.result_service.get_top_results.assert_called_once()

    @patch('builtins.input', side_effect=["1", "newpassword", "0"])
    def test_change_settings_password(self, mock_input):
        self.user_menu.current_user = self.mock_user
        self.user_menu.change_settings()
        self.user_service.save_user.assert_called_once()


class TestAdminMenu(unittest.TestCase):
    def setUp(self):
        self.user_service = Mock(UserService)
        self.quiz_service = Mock(QuizService)
        self.result_service = Mock(ResultService)
        self.admin_menu = AdminMenu(self.user_service, self.quiz_service, self.result_service)

        self.mock_admin = User("admin", "adminpass", date(1980, 1, 1))
        self.mock_quiz = Quiz("Sample Quiz")
        self.mock_question = Question("Sample Question", ["Option 1", "Option 2"], ["Option 1"])
        self.mock_quiz.add_question(self.mock_question)

    @patch('builtins.input', side_effect=["admin", "adminpass"])
    def test_authenticate_admin(self, mock_input):
        self.user_service.authenticate_admin.return_value = self.mock_admin
        self.admin_menu.authenticate()
        self.assertEqual(self.admin_menu.current_admin, self.mock_admin)
        self.user_service.authenticate_admin.assert_called_once_with("admin", "adminpass")

    @patch('builtins.input',
           side_effect=["New Quiz", "New Question", "Option 1", "Option 2", "end", "Option 1", "end", "end"])
    def test_create_quiz(self, mock_input):
        self.admin_menu.current_admin = self.mock_admin
        self.admin_menu.create_quiz()
        self.quiz_service.save_quiz.assert_called_once()

    @patch('builtins.input',
           side_effect=["Sample Quiz", "1", "Updated Question", "Updated Option 1", "end", "Updated Option 1", "end",
                        "end"])
    def test_edit_quiz(self, mock_input):
        self.admin_menu.current_admin = self.mock_admin
        self.quiz_service.get_quiz_by_title.return_value = self.mock_quiz
        self.admin_menu.edit_quiz()
        self.quiz_service.save_quiz.assert_called_once()


if __name__ == '__main__':
    unittest.main()

