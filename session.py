class UserSession:
    def __init__(self):
        self.id = None
        self.username = None
        self.email = None
        self.role = None

# Глобальный экземпляр сессии
session = UserSession()