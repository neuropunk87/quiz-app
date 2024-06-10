import os
import random
from models import User, Admin, Quiz, Result
from repositories import UserRepository, AdminRepository, QuizRepository, ResultRepository
from custom_exceptions import UserNotFoundException, UserAlreadyExistsException, QuizNotFoundException


class UserService:
    def __init__(self, user_repository: UserRepository, admin_repository: AdminRepository):
        self.user_repository = user_repository
        self.admin_repository = admin_repository
        self.users = self.user_repository.load()
        self.admins = self.admin_repository.load()

    def authenticate_user(self, login: str, password: str) -> User:
        for user in self.users:
            if user.login.lower() == login.lower() and user.password == password:
                return user
        raise UserNotFoundException(f"User '{login}' not found or invalid password.")

    def authenticate_admin(self, login: str, password: str) -> Admin:
        for admin in self.admins:
            if admin.login.lower() == login.lower() and admin.password == password:
                return admin
        raise UserNotFoundException(f"Admin '{login}' not found or invalid password.")

    def register_user(self, user: User) -> bool:
        if any(u.login.lower() == user.login.lower() for u in self.users):
            print(UserAlreadyExistsException())
        else:
            print("Registration successful. You can log in now.")
            self.users.append(user)
            self.user_repository.save(user)
            return True

    def save_user(self, user: User):
        for i, u in enumerate(self.users):
            if u.login == user.login:
                self.users[i] = user
                break
        self.user_repository.save_all(self.users)

    def save_admin(self, admin: Admin):
        self.admin_repository.save(admin)


class QuizService:
    def __init__(self, quiz_repository: QuizRepository):
        self.quiz_repository = quiz_repository
        self.quizzes = self.load_all_quizzes()

    def load_all_quizzes(self):
        quiz_files = self.quiz_repository.get_all_quiz_files()
        quizzes = [self.quiz_repository.load(filepath) for filepath in quiz_files]
        return [quiz for quiz in quizzes if quiz is not None]

    def refresh_quizzes(self):
        self.quizzes = self.load_all_quizzes()

    def get_quiz_by_title(self, title: str) -> Quiz:
        for quiz in self.quizzes:
            if quiz.title.lower() == title.lower():
                return quiz
        raise QuizNotFoundException(f"Quiz '{title}' not found.")

    def get_mixed_quiz_questions(self):
        all_questions = [question for quiz in self.quizzes for question in quiz.questions]
        # return random.sample(all_questions, len(all_questions))
        random.shuffle(all_questions)
        return all_questions[:20]

    def save_quiz(self, quiz: Quiz):
        # filename = f"quiz_{quiz.title.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.quiz_repository.quizzes_dir, f"quiz_{quiz.title.lower()}.json")
        self.quiz_repository.save(quiz, filepath)
        self.refresh_quizzes()


class ResultService:
    def __init__(self, result_repository: ResultRepository):
        self.result_repository = result_repository
        self.result_filepath = "results.json"
        self.top_num = 20

    def save_result(self, result: Result):
        self.result_repository.save(result, self.result_filepath)

    def get_user_results(self, user: User, quizzes):
        results = self.result_repository.load(self.result_filepath)
        user_results = [result for result in results if result['user'] == user.login]
        sorted_results = sorted(user_results, key=lambda x: x["score"], reverse=True)
        return sorted_results

    def get_top_results(self, title: str):
        results = self.result_repository.load(self.result_filepath)
        filtered_results = [result for result in results if result['quiz'].lower() == title.lower()]
        sorted_results = sorted(filtered_results, key=lambda x: x["score"], reverse=True)
        return sorted_results[:self.top_num]

    def get_total_top_results(self):
        results = self.result_repository.load(self.result_filepath)
        sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
        return sorted_results[:self.top_num]

