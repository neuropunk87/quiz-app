from datetime import date
from models import User, Result, Question, Quiz
from services import UserService, QuizService, ResultService
from custom_exceptions import (UserNotFoundException, InvalidDateFormatException, InvalidChoiceException,
                               QuizNotFoundException, InvalidInputException)


class UserMenu:
    def __init__(self, user_service: UserService, quiz_service: QuizService, result_service: ResultService):
        self.user_service = user_service
        self.quiz_service = quiz_service
        self.result_service = result_service
        self.current_user = None

    def authenticate(self):
        while True:
            login = input("Enter login: ")
            password = input("Enter password: ")
            try:
                self.current_user = self.user_service.authenticate_user(login, password)
                print(f"Welcome, {self.current_user.login}!")
                self.display_menu()
                break
            except UserNotFoundException as e:
                print(e)
                print("\nFor return to User Login Menu enter 'back' or any key for continue.")
                choice = input("Enter your choice: ")
                if choice.lower() == 'back':
                    break

    def register(self):
        login = input("Enter login: ")
        password = input("Enter password: ")

        try:
            birth_date_str = input("Enter birth date (YYYY-MM-DD): ")
            birth_date = date.fromisoformat(birth_date_str)
            new_user = User(login, password, birth_date)
            self.user_service.register_user(new_user)
        except ValueError:
            print(InvalidDateFormatException())

    def log_in(self):
        while True:
            try:
                print("\n---> User Login Menu")
                print("1. Authenticate")
                print("2. Register")
                print("0. Exit")

                choice = input("Select an option: ")
                if choice == '1':
                    self.authenticate()
                elif choice == '2':
                    self.register()
                elif choice == '0':
                    exit()
                else:
                    raise InvalidChoiceException()
            except InvalidChoiceException as e:
                print(e)

    def display_menu(self):
        while True:
            try:
                print("\n---> User Quiz Menu")
                print("1. Take a Quiz")
                print("2. View My Results")
                print("3. View Top-20 Results for Quiz")
                print("4. View Total Top-20 Results for all Quizzes")
                print("5. Settings")
                print("0. Logout")

                choice = input("Select an option: ")
                if choice == '1':
                    self.take_quiz()
                elif choice == '2':
                    self.view_results()
                elif choice == '3':
                    self.view_top_results()
                elif choice == '4':
                    self.view_total_top_results()
                elif choice == '5':
                    self.change_settings()
                elif choice == '0':
                    print("See you again!")
                    self.current_user = None
                    break
                else:
                    raise InvalidChoiceException()
            except InvalidChoiceException as e:
                print(e)

    def take_quiz(self):
        print("\nAvailable Quizzes:")
        for quiz in self.quiz_service.quizzes:
            print(f"---> {quiz.title}")

        title = input("Enter quiz title (or 'mix' for a mixed quiz): ")

        quiz = None

        if title.lower() == 'mix':
            questions = self.quiz_service.get_mixed_quiz_questions()
            quiz_title = "Mix"
        else:
            try:
                quiz = self.quiz_service.get_quiz_by_title(title)
                questions = quiz.questions
                quiz_title = quiz.title
            except QuizNotFoundException as e:
                print(e)
                return

        score = 0
        for i, question in enumerate(questions, start=1):
            print(f"\nQuestion {i}: {question.text}")
            for j, option in enumerate(question.options, start=1):
                print(f"{j}. {option}")

            while True:
                user_answer = input("Your answer (comma separated for multiple answers): ").split(',')
                try:
                    user_answer_indices = [int(num.strip()) - 1 for num in user_answer]
                    if all(0 <= index < len(question.options) for index in user_answer_indices):
                        break
                    else:
                        print("Invalid answer. Please enter valid option numbers.")
                except ValueError:
                    print(InvalidInputException())

            user_answer = [question.options[index] for index in user_answer_indices]

            if set(user_answer) == set(question.correct_answers):
                score += 1

        print(f"\nQuiz completed! Your score: {score}/{len(questions)}")

        result = Result(self.current_user, quiz, score)
        self.result_service.save_result(result)

        top_results = self.result_service.get_top_results(quiz_title)
        user_rank = next((index + 1 for index, res in enumerate(top_results) if res['user'] == self.current_user.login),
                         None)

        if user_rank:
            print(f"Your ranking: {user_rank}")
        else:
            print("You did not make it to the Top-20.")

    def view_results(self, header="\nYour Results:"):
        results = self.result_service.get_user_results(self.current_user, self.quiz_service.quizzes)
        user_results = [result for result in results if result['user'] == self.current_user.login]

        if user_results:
            print(header)
            print(f"\n{'Rank':<10}{'Quiz':<20}{'Score':<15}{'Date':<40}")
            print("-" * 85)
            for i, result in enumerate(user_results, start=1):
                print(f"{i:<10}{result['quiz']:<20}{result['score']:<15}{result['timestamp']:<40}")
        else:
            print("\nNo results found.")

    def view_top_results(self):
        title = input("Enter quiz title to view top results: ")
        try:
            top_results = self.result_service.get_top_results(title)
            print(f"\nTOP-20 results for quiz '{title}':")
            print(f"\n{'Rank':<10}{'User':<15}{'Score':<15}{'Timestamp':<40}")
            print("-" * 80)
            for i, result in enumerate(top_results, start=1):
                print(f"{i:<10}{result['user']:<15}{result['score']:<15}{result['timestamp']:<40}")
        except QuizNotFoundException as e:
            print(e)

    def view_total_top_results(self, header="\nTOP-20 results for all quizzes:"):
        top_results = self.result_service.get_total_top_results()
        print(header)
        print(f"\n{'Rank':<10}{'User':<15}{'Quiz':<20}{'Score':<15}{'Timestamp':<40}")
        print("-" * 100)
        for i, result in enumerate(top_results, start=1):
            print(f"{i:<10}{result['user']:<15}{result['quiz']:<20}{result['score']:<15}{result['timestamp']:<40}")

    def change_settings(self):
        try:
            print("\n---> User Settings Menu")
            print(f"1. Change Password (current: {self.current_user.password})")
            print(f"2. Change Birth Date (current: {self.current_user.birth_date})")
            print("0. Exit")

            choice = input("Select an option: ")
            if choice == '1':
                new_password = input("Enter new password: ")
                self.current_user.password = new_password
            elif choice == '2':
                new_birth_date = input("Enter new birth date (YYYY-MM-DD): ")
                try:
                    self.current_user.birth_date = date.fromisoformat(new_birth_date)
                except ValueError:
                    print(InvalidDateFormatException())
            elif choice == '0':
                return
            else:
                raise InvalidChoiceException()
            self.user_service.save_user(self.current_user)
            print("Settings updated.")
        except InvalidChoiceException as e:
            print(e)
        except InvalidDateFormatException as e:
            print(e)


class AdminMenu:
    def __init__(self, user_service: UserService, quiz_service: QuizService, result_service: ResultService):
        self.user_service = user_service
        self.quiz_service = quiz_service
        self.result_service = result_service
        self.current_admin = None

    def authenticate(self):
        if self.current_admin:
            print("You are already logged in to your admin account.")
            return

        while True:
            login = input("Enter admin login: ")
            password = input("Enter admin password: ")
            try:
                self.current_admin = self.user_service.authenticate_admin(login, password)
                print("\n---> Quiz Development Tool <---")
                print(f"\nWelcome, admin {self.current_admin.login}!")
                break
            except UserNotFoundException as e:
                print(e)
                self.display_menu()

    def display_menu(self):
        while True:
            try:
                print("\n---> Admin Menu")
                print("1. Authenticate")
                print("2. Create Quiz")
                print("3. Edit Quiz")
                print("0. Exit")

                choice = input("Select an option: ")
                if choice == '1':
                    self.authenticate()
                elif choice == '2':
                    if self.current_admin:
                        self.create_quiz()
                    else:
                        print("Please authenticate first.")
                elif choice == '3':
                    if self.current_admin:
                        self.edit_quiz()
                    else:
                        print("Please authenticate first.")
                elif choice == '0':
                    self.current_admin = None
                    print("Logged out of the admin account.")
                    break
                else:
                    raise InvalidChoiceException()
            except InvalidChoiceException as e:
                print(e)

    def create_quiz(self):
        title = input("Enter quiz title: ")
        if not title:
            print("Invalid input.")
            self.display_menu()
            return

        quiz = Quiz(title)

        while True:
            question_text = input("Enter question text (or 'end' to finish): ")
            if question_text.lower() == "end":
                break
            elif not question_text:
                print("Invalid input.")
                continue

            options = []
            while True:
                option = input("Enter option (or 'end' to finish): ")
                if option.lower() == 'end':
                    break
                elif not option:
                    print("Invalid input.")
                else:
                    options.append(option)

            correct_answers = []
            while True:
                correct_answer = input("Enter correct answer (or 'end' to finish): ")
                if correct_answer.lower() == 'end':
                    break
                elif not correct_answer:
                    print("Invalid input.")
                else:
                    correct_answers.append(correct_answer)

            if not options or not correct_answers:
                print("Options and correct answers cannot be empty.")
                continue

            question = Question(question_text, options, correct_answers)
            quiz.add_question(question)

        if quiz.questions:
            self.quiz_service.save_quiz(quiz)
            print(f"Quiz '{quiz.title}' created successfully.")
        else:
            print("Quiz must contain at least one question.")

    def edit_quiz(self):
        title = input("Enter quiz title to edit: ")
        if not title:
            print("Invalid input.")
            self.display_menu()
            return

        quiz = Quiz(title)

        try:
            quiz = self.quiz_service.get_quiz_by_title(title)
        except QuizNotFoundException as e:
            print(e)
            return

        print("\nCurrent Questions:")
        for i, question in enumerate(quiz.questions):
            print(f"{i + 1}. {question.text}")

        while True:
            choice = input("Enter question number to edit (or 'end' to finish): ")
            if choice.lower() == 'end':
                break
            try:
                question_index = int(choice) - 1
                if 0 <= question_index < len(quiz.questions):
                    question_text = input("Enter new question text: ")
                    options = []
                    while True:
                        option = input("Enter new option (or 'end' to finish): ")
                        if option.lower() == 'end':
                            break
                        options.append(option)

                    correct_answers = []
                    while True:
                        correct_answer = input("Enter new correct answer (or 'end' to finish): ")
                        if correct_answer.lower() == 'end':
                            break
                        try:
                            correct_answers.append(correct_answer)
                        except InvalidInputException as e:
                            print(e)

                    quiz.questions[question_index] = Question(question_text, options, correct_answers)
                else:
                    print("Invalid question number.")
            except ValueError:
                print(InvalidInputException())

        self.quiz_service.save_quiz(quiz)
        self.quiz_service.refresh_quizzes()
        print(f"Quiz '{title}' updated successfully!")

