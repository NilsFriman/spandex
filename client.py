import socket
import threading


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("192.168.0.83", 1234))



def reciever():
    while True:
        msg = s.recv(1024)
        print(msg.decode("utf-8"))

def writer():
    while True:
        message = input("")
        s.send(message.encode())


recieve_thread = threading.Thread(target=reciever)
recieve_thread.start()


writer_thread = threading.Thread(target=writer)
writer_thread.start()