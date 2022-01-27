from math import exp
import socket
import threading
from random import randint
import sys
import string
import random
import datetime 
from cProfile import run

HOST = '127.0.0.1'
PORT = 2137

users = {}
users_con = {}
socks = []
bans = []
admins = []
rooms = [] 
rooms.append("default")
room_passwords = {}
user_room= {}
user_room["default"] = []



def id_generator(size, chars=string.ascii_lowercase + string.digits):
   return ''.join(random.choice(chars) for _ in range(size))

admin_pass = id_generator(6)

def editlogfile(text,today):
    teraz = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    f = open(f"logs/{today}.txt", "a")
    f.write(f"\n{teraz} {text.strip()}")
    f.close()


def sendtoall(msg, conn):
    try:
        msg = bytes(msg,'utf8')
        for i in rooms:
            if conn in user_room[i]:
                for x in user_room[i]:
                    if x in socks:
                        x.sendall(msg)
    except Exception as e:
        print(e)

def handle_room_changing(id,conn,addr):
    for i in rooms:
        if conn in user_room[str(i)]:
            user_room[i].remove(conn)
    user_room[id].append(conn)
    for i in user_room[id]:
        if i in socks:
            i.sendall(bytes(f"[Room {id}] Hi {users[addr]}! \n", 'utf-8'))
    sys.exit()

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
    elif command_list[0].strip() == "!create":
        if len(command_list) > 2:
            id = command_list[1].strip()
            if not id in rooms:
                rooms.append(id.strip())
                room_passwords[id] = ""
                user_room[id] = []
                thread = threading.Thread(target=handle_room_changing, args=(id, conn,addr))
                thread.start()
            else:
                conn.sendall(bytes(f"There is a room named: {id} \n",'utf-8'))
        elif len(command_list) == 3:
            id = command_list[1].strip()
            if not id in rooms:
                password = command_list[2].strip()
                rooms.append(id)
                room_passwords[id] = password.strip()
                user_room[id] = []
                thread = threading.Thread(target=handle_room_changing, args=(id, conn,addr))
                thread.start()

    elif command_list[0].strip() == "!join":
        if len(command_list) > 1: 
            id = command_list[1].strip()
            if id in rooms:
                if id in room_passwords:
                    if len(command_list) > 2:
                        password = command_list[2].strip()
                        if room_passwords[id] == password:
                            thread = threading.Thread(target=handle_room_changing, args=(id, conn,addr))
                            thread.start()
                        else:
                            conn.sendall(bytes(f"You need to enter correct password to join room named: {id} \n",'utf-8'))
                else:
                    thread = threading.Thread(target=handle_room_changing, args=(id, conn,addr))
                    thread.start()
            else:
                conn.sendall(bytes(f"Couldn't join room named: {id} \n",'utf-8'))
    elif command_list[0].strip() == "!kick":
        if addr in admins:
            if not len(command_list) > 1: return
            if command_list[1].strip() in users_con:
                if command_list[1].strip() == users[addr]: 
                    txt = bytes(f"[ERROR] You can't kick yourself dummy! \n",encoding='utf8')
                    conn.sendall(txt) 
                    return
                users_con[command_list[1].strip()].close()
                txt = bytes(f"[Console] Kicked user {command_list[1].strip()} from the server \n",encoding='utf8')
                print(f"[Console] Kicked user {command_list[1].strip()} from the server \n")
                sendtoall(txt,conn)
            else:
                txt = bytes(f"[COMMAND] Couldn't find user {command_list[1].strip()} \n",encoding='utf8')
                conn.sendall(txt)
        else:
            txt = bytes(f"[COMMAND] You don't have premission to do that! \n",encoding='utf8')
            conn.sendall(txt)
    elif command_list[0].strip() == "!ban":
        if addr in admins:
            if not len(command_list) > 1: return
            if command_list[1].strip() in users_con:
                if command_list[1].strip() == users[addr]: 
                    txt = bytes(f"[ERROR] You can't ban yourself dummy! \n",encoding='utf8')
                    conn.sendall(txt) 
                    return
                users_con[command_list[1].strip()].close()
                txt = bytes(f"[Console] Banned user {command_list[1].strip()} from the server \n",encoding='utf8')
                print(f"[Console] Banned user {command_list[1].strip()} from the server \n")
                sendtoall(txt,conn)
                bans.append(addr[0])
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
    user_room["default"].append(conn)
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
        if addr[0] in bans:
            conn.close()
            return
        try:
            data = conn.recv(1024)
            if not data:
                break
            msg_decoded = data.decode("utf-8")
            editlogfile(msg_decoded,log_file_name)
            if msg_decoded.startswith("!"):
                thread = threading.Thread(target=handle_command, args=(msg_decoded, conn, addr))
                thread.start()
            else:
                msg = f"{users[addr]} : {msg_decoded}"
                print(msg.strip())
                sendtoall(msg,conn)
        except:
            connected = False
            socks.remove(conn)
            conn.close()
    print('> Disconnected by ->', addr)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    log_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    f = open(f"logs/{log_file_name}.txt", "a")
    teraz = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    f.write(f"{teraz} Started server!")
    f.close()
    print(f"[INFO] Started server at -> {HOST}:{PORT}")
    print(f"[INFO] Created log file -> {log_file_name}")
    print(f"[INFO] Created admin password -> {admin_pass}")
    s.listen()
    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"> Active connections -> {threading.activeCount() - 1}")

        
