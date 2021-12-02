import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

#HOST = '10.98.0.95' 
HOST = '127.0.0.1'
PORT = 2137      

connected = False

def create_room():
    password = " "
    id = roomid.get("1.0", "end").strip()
    password = passwordbox.get()
    command = f"!create {id} {password}"
    sock.sendall(bytes(command, 'utf-8'))
    new_window1.destroy()

def join_room():
    password = " "
    id = roomid.get("1.0", "end").strip()
    password = passwordbox.get()
    command = f"!join {id} {password}"
    sock.sendall(bytes(command, 'utf-8'))
    new_window.destroy()


def drawjoingui():
    global roomid
    global passwordbox
    global new_window
    new_window = tk.Tk()
    new_window.title("Change room")   
    new_window.geometry("225x75")
    new_window.resizable(False,False)
    tk.Label(new_window,text="Room ID: ").grid(row=5,column=4)
    tk.Label(new_window,text="Password: ").grid(row=10,column=4)
    roomid = tk.Text(new_window,width=20,height=1)
    roomid.grid(row=5, column=5)
    passwordbox = tk.Entry(new_window,show="\u2022",width=25)
    passwordbox.grid(row=10, column=5)
    button1 = tk.Button(new_window, height=1,width=5, text="Join", command=join_room).grid(row=20,column=4)

def drawcreatgui():
    global roomid
    global passwordbox
    global new_window1
    new_window1 = tk.Tk()
    new_window1.title("Create room")   
    new_window1.geometry("225x75")
    new_window1.resizable(False,False)
    tk.Label(new_window1,text="Room ID: ").grid(row=5,column=4)
    tk.Label(new_window1,text="Password: ").grid(row=10,column=4)
    roomid = tk.Text(new_window1,width=20,height=1)
    roomid.grid(row=5, column=5)
    passwordbox = tk.Entry(new_window1,show="\u2022",width=25)
    passwordbox.grid(row=10, column=5)
    button1 = tk.Button(new_window1, height=1,width=5, text="Create", command=create_room).grid(row=20,column=4)

    
def print_messages(e):
    if connected:
        txt = textbox.get(1.0, tk.END+"-1c")
        if not txt.isspace(): 
            sock.sendall(bytes(txt, 'utf-8'))
        textbox.delete('1.0', tk.END)
    else:
        txt =f"[ERROR] Can't send message to server. You're disconnected \n"
        insert_text(txt)
        textbox.delete('1.0', tk.END)

def showEnd(event):
    textw.see(tk.END)
    textw.edit_modified(0)

def insert_text(txt):
    textw.configure(state='normal')
    textw.insert(tk.INSERT, txt)
    textw.configure(state='disabled')

def gui():
    global textbox
    global textw    
    global root
    root = tk.Tk()
    root.geometry("500x300")
    root.title("[Connecting] Chat")
    root.resizable(False,False)
    root.bind('<Return>',print_messages)
    textw = ScrolledText(root,height=15)
    textw.pack(fill=tk.X,side=tk.TOP,ipadx=5, ipady=5)
    textw.bind('<<Modified>>',showEnd)
    textw.config(state=tk.DISABLED)
    textbox=tk.Text(root, height=2)
    menu = tk.Menu(root) 
    cascade = tk.Menu(menu) 
    menu.add_cascade(label="Rooms", menu = cascade)      
    cascade.add_command(label = "Join", command=drawjoingui)  
    cascade.add_command(label = "Create",command=drawcreatgui) 
    root.config( menu = menu)
    textbox.pack(fill=tk.X,side=tk.BOTTOM,ipadx=5, ipady=5)  
    root.mainloop()


start_gui = threading.Thread(target=gui)
start_gui.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    global sock
    sock = s
    def get_messages():
        running = True
        while running:
            try:
                msg = s.recv(1024)
                msg = msg.decode('utf-8')
                insert_text(msg)
            except Exception as e:
                global connected
                txt =f"[ERROR] Disconnected with error: {e} \n"
                root.title("[Disonnected] Chat")
                connected = False
                insert_text(txt)
                running = False
    try:
        s.connect((HOST, PORT))
        txt=f"[CONNECTION] CONNECTED TO SERVER {HOST} {PORT} \n"
        root.title("[Connected] Chat")
        connected = True
        insert_text(txt)
        txt = "-"*50+f"\n"
        insert_text(txt)
        thread = threading.Thread(target=get_messages)
        thread.start()
        while True:
           pass

    except Exception as e:
       txt=f"[ERROR] Couldn't join server. ERROR: {e} \n"
       root.title("[ERROR] Chat")
       connected = False
       insert_text(txt)



