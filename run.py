from repositories import UserRepository, AdminRepository, QuizRepository, ResultRepository
from services import UserService, QuizService, ResultService
from interfaces import UserMenu, AdminMenu
from custom_exceptions import InvalidChoiceException


class QuizApp:
    def __init__(self):
        user_repo = UserRepository('user_credentials.json')
        admin_repo = AdminRepository('admin_credentials.json')
        quiz_repo = QuizRepository('quizzes')
        result_repo = ResultRepository()

        self.user_service = UserService(user_repo, admin_repo)
        self.quiz_service = QuizService(quiz_repo)
        self.result_service = ResultService(result_repo)

        self.user_menu = UserMenu(self.user_service, self.quiz_service, self.result_service)
        self.admin_menu = AdminMenu(self.user_service, self.quiz_service, self.result_service)

    def run(self):
        print("\nWelcome to the 'QuizApp'!")

        while True:
            try:
                print("\n---> Main Menu")
                print("1. User Interface")
                print("2. Admin Tools")
                print("0. Exit")

                choice = input("Select an option: ")
                if choice == '1':
                    self.user_menu.log_in()
                elif choice == '2':
                    self.admin_menu.display_menu()
                elif choice == '0':
                    print("Goodbye!")
                    break
                else:
                    raise InvalidChoiceException()
            except InvalidChoiceException as e:
                print(e)


if __name__ == '__main__':
    app = QuizApp()
    app.run()

