import socket
import threading


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

socket.connect(("10.158.18.141", 1234))


def receiver():
    while True:
        msg = socket.recv(1024)
        print(msg.decode("utf-8"))


def writer():
    while True:
        message = input("")
        socket.send(message.encode())


recieve_thread = threading.Thread(target=receiver)
recieve_thread.start()

writer_thread = threading.Thread(target=writer)
writer_thread.start()
