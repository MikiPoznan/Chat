from math import exp
import socket
import threading
from random import randint

HOST = '127.0.0.1'
PORT = 2137

users = {}
users_con = {}
socks = []

def sendtoall(msg):
    try:
        for y in socks:
            if isinstance(msg, str):
                msg = bytes(msg,encoding='utf8')
            y.sendall(msg)
    except Exception as e:
        print(e)

def handle_client(conn, addr):
    nick_set = False
    print('> Connected by ->', addr)

    while nick_set == False:
        nick = "USER#"+str(randint(0, 1000))
        if not nick in str(users):
            nick_set=True
            
    users[addr] = nick
    users_con[users[addr]] = conn
    socks.append(conn)
    connected = True

    while connected:
        try:
            data = conn.recv(1024)
            if not data:
                break
            msg_decoded = data.decode("utf-8")
            msg = f"{users[addr]} : {msg_decoded}"
            sendtoall(msg)
        except:
            connected = False
            socks.remove(conn)
            conn.close()
    print('> Disconnected by ->', addr)
    connected = False        
    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    print(f"[INFO] Started server at -> {HOST}:{PORT}")
    s.listen()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"> Active connections -> {threading.activeCount() - 1}")

        
