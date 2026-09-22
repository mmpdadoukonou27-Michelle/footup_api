from fastapi import HTTPException

class UserAlreadyExists(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Cet email est déjà utilisé.")

class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Email ou mot de passe incorrect.")