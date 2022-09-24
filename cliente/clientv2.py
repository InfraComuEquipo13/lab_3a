# Echo client program

from asyncio import Queue
import socket
import struct
import threading
import time

class ThreadedClient(threading.Thread):
    def __init__(self,  numcliente, n_conn ,host, port):
        threading.Thread.__init__(self)
        #set up queues
        self.send_q = Queue(maxsize = 10)
        #declare instance variables       
        self.numcliente= numcliente
        self.host = host
        self.port = port
        self.n_conn = n_conn
        #connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    #LISTEN
    def listen(self):
        while True: #loop forever
            try:
                print ('checking for message...')
                # stops listening if there's a message to send
                if self.send_q.empty() == False:
                    self.send_message()
                else:
                    print ('no message')
                print ('listening...')
                message = self.s.recv(1024)
                print ('RECEIVED: ' + message)
            except socket.timeout:
                pass

    def start_listen(self):
        t = threading.Thread(target = self.listen())
        t.start()
        #t.join()
        print ('started listen')

    
    def start_receive_file(self):
        th = threading.Thread(target=self.receive_file, args=(self.s, f"Cliente{self.numcliente}-Prueba-{self.n_conn}.txt",))
        print(f"Recibiendo archivo en el cliente{i}...")
        th.start()
        print(f"Archivo recibido en el cliente{i}.")
        #t.join()  

    def receive_file_size(self, sck: socket.socket):
        
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

    def receive_file(self, sck: socket.socket, filename):
        # Leer primero del socket la cantidad de bytes que se recibirán del archivo.

        filesize = self.receive_file_size(self.s)
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

    

    #ADD MESSAGE
    def add_message(self, msg):
        #put message into the send queue
        self.send_q.put(msg)
        print ('ADDED MSG: ' + msg)
        #self.send_message()

    #SEND MESSAGE
    def send_message(self):
        #send message
        msg = self.get_send_q()
        if msg == "empty!":
            print ("nothing to send")
        else:
            self.s.sendall(msg)
            print ('SENDING: ' + msg)
            #restart the listening
            #self.start_listen()


    #SAFE QUEUE READING
    #if nothing in q, prints "empty" instead of stalling program
    def get_send_q(self):       
        if self.send_q.empty():
            print ("empty!")
            return "empty!"
        else:
            msg = self.send_q.get()
            return msg

if __name__ == '__main__':
    
    n_conn = int(input('Ingrese el número de conexiones: '))
    #receive_file(s, f"Cliente{i}-Prueba-{n_conn}.txt")
    
    # Get local machine name
    HOST = socket.gethostname() 
    # The same port as used by the server
    PORT = 50000           
    i=1
    while i <= n_conn:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        
        s = ThreadedClient(i, n_conn, HOST, PORT)
        s.start()
        print(f'Connection between client #{i} y el server started, port: {PORT}')

        #s.add_message('hello world')
        s.start_receive_file()
        #s.add_message('hello world')
        i+=1





#s.sendall(bytes('Hello, world', 'utf-8'))
#data = s.recv(1024)


#print ('Received', repr(data))