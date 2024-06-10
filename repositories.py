import os
import json
from datetime import date
from custom_exceptions import SavingErrorException
from models import User, Admin, Quiz, Question, Result


class UserRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        users = []
        try:
            with open(self.filepath, 'r') as file:
                users_data = json.load(file)
                for user_data in users_data:
                    login = user_data['login']
                    password = user_data['password']
                    birth_date = date.fromisoformat(user_data['birth_date'])
                    users.append(User(login, password, birth_date))
        except FileNotFoundError:
            print(f"User file '{self.filepath}' not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{self.filepath}'.")
        return users

    def save(self, user: User):
        users = self.load()
        users.append(user)
        try:
            with open(self.filepath, 'w') as file:
                json.dump([u.to_dict() for u in users], file, indent=4)
        except SavingErrorException as e:
            print(f"Error saving user: {e}.")

    def save_all(self, users: list):
        try:
            with open(self.filepath, 'w') as file:
                json.dump([u.to_dict() for u in users], file, indent=4)
        except SavingErrorException as e:
            print(f"Error saving users: {e}.")


class AdminRepository:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self):
        admins = []
        try:
            with open(self.filepath, 'r') as file:
                admins_data = json.load(file)
                for admin_data in admins_data:
                    login = admin_data['login']
                    password = admin_data['password']
                    admins.append(Admin(login, password))
        except FileNotFoundError:
            print(f"Admin file '{self.filepath}' not found.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{self.filepath}'.")
        return admins

    def save(self, admin: Admin):
        admins = self.load()
        admins.append(admin)
        try:
            with open(self.filepath, 'w') as file:
                json.dump([a.to_dict() for a in admins], file, indent=4)
        except SavingErrorException as e:
            print(f"Error saving admin: {e}.")


class QuizRepository:
    def __init__(self, quizzes_dir: str):
        self.quizzes_dir = quizzes_dir
        os.makedirs(self.quizzes_dir, exist_ok=True)

    def load(self, filepath: str):
        try:
            with open(filepath, 'r') as file:
                quiz_data = json.load(file)
                quiz = Quiz(quiz_data['title'])
                for question_data in quiz_data['questions']:
                    question = Question(question_data['text'], question_data['options'], question_data['correct_answers'])
                    quiz.add_question(question)
                return quiz
        except FileNotFoundError:
            print(f"Quiz file '{filepath}' not found.")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{filepath}'.")
            return None

    def save(self, quiz: Quiz, filepath: str):
        try:
            with open(filepath, 'w') as file:
                json.dump(quiz.to_dict(), file, indent=4, separators=(',', ': '))
        except SavingErrorException as e:
            print(f"Error saving quiz to '{filepath}': {e}.")

    def get_all_quiz_files(self):
        return [os.path.join(self.quizzes_dir, file) for file in os.listdir(self.quizzes_dir) if file.endswith('.json')]


class ResultRepository:
    def load(self, filepath: str):
        try:
            with open(filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from '{filepath}'.")
            return []

    def save(self, result: Result, filepath: str):
        try:
            results = self.load(filepath)
            results.append(result.to_dict())
            with open(filepath, 'w') as file:
                json.dump(results, file, indent=4)
        except SavingErrorException as e:
            print(f"Error saving result to '{filepath}': {e}.")

