import socket
import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

HOST = '127.0.0.1' 
PORT = 2137      

connected = False

    
def print_messages(e):
    if connected:
        sock.sendall(bytes(textbox.get(1.0, tk.END+"-1c"), 'utf-8'))
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
            msg = input()

    except Exception as e:
       txt=f"[ERROR] Couldn't join server. ERROR: {e} \n"
       root.title("[ERROR] Chat")
       connected = False
       insert_text(txt)



