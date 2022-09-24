#!/usr/bin/python           # This is server.py file                                                                                                                                                                           


import os
import socket
import struct
import threading

fileprueba = "prueba.tiff"
filename_1 = "archivo_100mb.zip"

filename_2 = "archivo_250mb.zip"

def send_file(sck: socket.socket, filename):
    # Obtener el tamaño del archivo a enviar.
    filesize = os.path.getsize(filename)
    # Informar primero al servidor la cantidad
    # de bytes que serán enviados.
    sck.sendall(struct.pack("<Q", filesize))
    # Enviar el archivo en bloques de 1024 bytes.
    with open(filename, "rb") as f:
        while read_bytes := f.read(1024):
            sck.sendall(read_bytes)


def on_new_client(clientsocket,addr):
    while True:
        #msg = clientsocket.recv(1024)
        #do some checks and if msg == someWeirdSignal: break:
      
        print (addr, ' >> ')
        #msg = 'SERVER >> '
        #Maybe some code to compute the last digit of PI, play game or anything else can go here and when you are done.
        #clientsocket.send(bytes(msg, 'utf-8'))
        #break
        
        
        print("Enviando archivo...")
        send_file(clientsocket, filename_1)
        print("Enviado.")
    clientsocket.close()



    
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 50000                # Reserve a port for your service.

print ('Server started!')
print ('Waiting for clients...')

s.bind((host, port))        # Bind to the port
s.listen(5)                 # Now wait for client connection.

#print ('Got connection from', addr)
while True:
    c, addr = s.accept()     # Establish connection with client.
    th = threading.Thread(target=on_new_client, args=(c,addr,))
    th.start()
    
    #Note it's (addr,) not (addr) because second parameter is a tuple
    #Edit: (c,addr)
    #that's how you pass arguments to functions when creating new threads using thread module.
s.close()