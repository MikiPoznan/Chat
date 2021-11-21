from math import exp
import socket
import threading
from random import randint
import sys
import string
import random

HOST = '127.0.0.1'
PORT = 2137

users = {}
users_con = {}
socks = []
admins = []

def id_generator(size, chars=string.ascii_lowercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

admin_pass = id_generator(6)

def sendtoall(msg):
    try:
        for y in socks:
            if isinstance(msg, str):
                msg = bytes(msg,encoding='utf8')
            y.sendall(msg)
    except Exception as e:
        print(e)

def handle_command(msg, conn, addr):
    command_list = list(msg.split(' '))
    if command_list[0].strip() == "!hi":
        txt = bytes(f"[COMMAND] Hi {users[addr]} \n",encoding='utf8')
        conn.sendall(txt)
    elif command_list[0].strip() =="!login":    
        if len(command_list) > 1:
            if command_list[1].strip() == admin_pass:
                admins.append(addr)
                txt = bytes(f"[COMMAND] Succesfully Logged in! \n",encoding='utf8')
                conn.sendall(txt)
                print(f"[INFO] Added new admin: {users[addr]} \n")
            else: 
                txt = bytes(f"[ERROR] Password {command_list[1].strip()} isn't valid \n",encoding='utf8')
                conn.sendall(txt)
    elif command_list[0].strip() == "!kick":
        if addr in admins:
            if not len(command_list) > 1: return
            if command_list[1].strip() in users_con:
                users_con[command_list[1].strip()].close()
                txt = bytes(f"[Console] Kicked user {command_list[1].strip()} from the server \n",encoding='utf8')
                sendtoall(txt)
            else:
                txt = bytes(f"[COMMAND] Couldn't find user {command_list[1].strip()} \n",encoding='utf8')
                conn.sendall(txt)
        else:
            txt = bytes(f"[COMMAND] You don't have premission to do that! \n",encoding='utf8')
            conn.sendall(txt)
    else:
        txt = bytes(f"Couldn't find command: {command_list[0].strip()} \n",encoding='utf8')
        conn.sendall(txt)
    sys.exit()


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
            if msg_decoded.startswith("!"):
                thread = threading.Thread(target=handle_command, args=(msg_decoded, conn, addr))
                thread.start()
            else:
                msg = f"{users[addr]} : {msg_decoded}"
                print(msg)
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
    print(f"[INFO] Created admin password -> {admin_pass}")
    s.listen()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"> Active connections -> {threading.activeCount() - 1}")

        
