class AppException(Exception):
    def __init__(
            self,
            message: str,
            status_code: int = 400
    ):
        self.message = message
        self.status_code = status_code

        super().__init__(message)

class ConflictException(AppException):
    def __init__(self, message: str= "Resource already exist"):
        super().__init__(
            message=message,
            status_code=409
        )