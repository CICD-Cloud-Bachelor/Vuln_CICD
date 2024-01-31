from faker import Faker
import os, random, hashlib

fake = Faker()
md5 = hashlib.new('md5')
md5.update(b"princess")

n = 1000
random_value = random.randint(1, n)

query = "INSERT INTO users (username, password) VALUES \n"
text = ""
for i in range(n):
    username = "Troll_Trollington" if i == random_value else fake.name().lower().replace(" ", "_").replace(".", "_")
    password = md5.hexdigest() if i == random_value else os.urandom(16).hex()
    text += f"('{username}', '{password}')" + ",\n" if i != n else ";\n"
    

query += text
with open("output.txt", "w") as f:
    f.write(query)