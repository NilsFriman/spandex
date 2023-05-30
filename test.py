from cryptography.fernet import Fernet
import json


message = input()

key = Fernet.generate_key()

with open("encryptionkey.json", "w") as file:
    json.dump(str(key), file)

with open("encryptionkey.json", "r") as file:
    print(bytes(json.load(file), "utf-8"))

print(f"Generated key: {key}, {type(key)}, {bytes(str(key), 'utf-8')[2:-1]}, {type(bytes(str(key), 'utf-8')[2:-1])}")

fernet = Fernet(bytes(str(key)))

encrypted = fernet.encrypt(message.encode())

print(f"Original message: {message}")

print(f"Encrypted message: {encrypted}")

decrypted = fernet.decrypt(encrypted).decode()

print(f"Decrypted message: {decrypted}")
