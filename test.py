import socket
try:
    socket.create_connection(('PLABSQLW19S1', 49172), timeout=5)
    print("Сервер доступен")
except Exception as e:
    print(f"Сервер недоступен: {e}")