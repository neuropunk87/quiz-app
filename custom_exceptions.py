class UserAlreadyExistsException(Exception):
    def __init__(self, message="User already exists."):
        self.message = message
        super().__init__(self.message)


class UserNotFoundException(Exception):
    pass


class QuizNotFoundException(Exception):
    pass


class InvalidChoiceException(Exception):
    def __init__(self, message="Invalid choice. Please try again."):
        self.message = message
        super().__init__(self.message)


class InvalidDateFormatException(BaseException):
    def __init__(self, message="Invalid date format. Please use YYYY-MM-DD and try again."):
        self.message = message
        super().__init__(self.message)


class InvalidInputException(Exception):
    def __init__(self, message="Invalid input. Please enter numbers only."):
        self.message = message
        super().__init__(self.message)


class SavingErrorException(Exception):
    pass

