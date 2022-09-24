# Echo client program
import socket
import struct
import threading


def receive_file_size(sck: socket.socket):
    
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()
    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)
    filesize = struct.unpack(fmt, stream)[0]
    return filesize

def receive_file(sck: socket.socket, filename):
    # Leer primero del socket la cantidad de bytes que se recibirán del archivo.

    filesize = receive_file_size(sck)
    # Abrir un nuevo archivo en donde guardar los datos recibidos.
    with open(filename, "wb") as f:
        received_bytes = 0
        # Recibir los datos del archivo en bloques de 1024 bytes hasta llegar
        # a la cantidad de bytes total informada por el cliente.
        while received_bytes < filesize:
            chunk = sck.recv(1024)
            if chunk:
                f.write(chunk)
                received_bytes += len(chunk)


# Get local machine name
HOST = socket.gethostname() 
# The same port as used by the server
PORT = 50000              

#s.sendall(bytes('Hello, world', 'utf-8'))
#data = s.recv(1024)

n_conn=5
#receive_file(s, f"Cliente{i}-Prueba-{n_conn}.txt")

i=1
while i <= n_conn:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    th = threading.Thread(target=receive_file, args=(s, f"Cliente{i}-Prueba-{n_conn}.txt",))
    
    print(f"Recibiendo archivo en el cliente{i}...")
    th.start()    
    print(f"Archivo recibido en el cliente{i}.")
    th.join()
    #Note it's (addr,) not (addr) because second parameter is a tuple
    #Edit: (c,addr)
    #that's how you pass arguments to functions when creating new threads using thread module.
    i+=1
s.close()

#print ('Received', repr(data))