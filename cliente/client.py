# Echo client program

# importing the hashlib module
import hashlib
from asyncio import Queue
import socket
import struct
import threading
import time
import logging
import datetime
import os

barrier = None
n_conn = int(input('Ingrese el número de conexiones: '))
tipo_archivo = int(input('Ingrese "0" si desea recibir un archivo de 100MB y "1" si desea uno de 250MB: '))
#n_conn = 2
#tipo_archivo = "1"

# Creación del logger
## Fecha de la prueba
now = datetime.datetime.now()
#os.mkdir('Logs')

logging.basicConfig(filename=f'Logs\prueba{n_conn}-{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}-log.txt', 
                             encoding='utf-8',
                             format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                             level=logging.INFO,
                             datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("client_logger")

class ThreadedClient(threading.Thread):
    ### CONSTRUCTOR DE LA CLASE 
    
    def __init__(self,  numcliente, n_conn ,host, port, tipo_archivo, logger):
        threading.Thread.__init__(self)
        #set up queues
        self.send_q = Queue(maxsize = 10)
        #declare instance variables       
        self.numcliente= numcliente
        self.host = host
        self.port = port
        self.n_conn = n_conn
        self.tipo_archivo = tipo_archivo
        #connect to socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logger.info(f' Cliente #{self.numcliente}: Estableciendo conexión con el servidor.') 
        self.s.connect((self.host, self.port))
        logger.info(f' Cliente #{self.numcliente}: Conexión con el servidor exitosa en el puerto {self.port}.') 


    def run(self):
        #print(str(self.numcliente) + "\n")
        logger.info(f' Cliente #{self.numcliente}: A la espera de que los demás clientes se conecten. Van {barrier.n_waiting}') 
        barrier.wait()

        ################################################
    def start_receive_file(self):
        self.filepath = f"ArchivosRecibidos\Cliente{self.numcliente}-Prueba-{self.n_conn}.txt"
        th = threading.Thread(target=self.receive_file, args=(self.s, self.filepath,))
        print(f"Recibiendo archivo en el cliente{self.numcliente}...")
        th.start()
        print(f"Archivo recibido en el cliente{self.numcliente}.")
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
        
        logger.info(f' Cliente #{self.numcliente}: Se recibió el tamaño real ({filesize}B) del archivo que se recibirá.') 
        return filesize

    def receive_file(self, sck: socket.socket, filename):

        
        ### Envía el tipo de archivo que recibirá
        sck.sendall("{0}".format(tipo_archivo).encode())  
        logger.info(f' Cliente #{self.numcliente}: Se le envió al servidor el tipo de archivo que se desea recibir.')    
        
        
        #filename_server = sck.recv(1024).decode("utf-8")
        ### Recibe el mensaje de solicitud de confirmación del servidor
        mensaje_conf = sck.recv(1024).decode("utf-8")
        
        logger.info(f' Cliente #{self.numcliente}: Se recibió el mensaje de solicitud de confirmación.') 
        filename_server = mensaje_conf.split(" ")[-1]
        logger.info(f' Cliente #{self.numcliente}: Se recibió nombre del archivo que se recibirá, el cual es {filename_server}.') 
        #sck.sendall("{0}".format("0").encode())  
        
      
        
        ### Enviar la confirmación de listo
        sck.sendall("{0}".format("1").encode())    
        logger.info(f' Cliente #{self.numcliente}: Enviada la confirmación de listo para iniciar la transferencia.') 
        ### Leer primero del socket la cantidad de bytes que se recibirán del archivo.
        filesize = self.receive_file_size(self.s)
        # Abrir un nuevo archivo en donde guardar los datos recibidos.
        
        logger.info(f' Cliente #{self.numcliente}: Inicio de la transferencia del archivo.') 
        try:
            with open(filename, "wb") as f:
                received_bytes = 0
                # Recibir los datos del archivo en bloques de 1024 bytes hasta llegar
                # a la cantidad de bytes total informada por el cliente.
                
                time_start = time.time()
                while received_bytes < filesize:
                    chunk = sck.recv(1024)
                    if chunk:
                        f.write(chunk)
                        received_bytes += len(chunk)
                time_end = round(time.time()-time_start, 5)
            logger.info(f' Cliente #{self.numcliente}: El archivo fue recibido con exito. El tiempo de transferencia fue: {time_end} segundos.') 
        except:
            logger.info(f' Cliente #{self.numcliente}: La transferencia no fue exitosa.') 
        
        ## Integridad del archivo
        
        ### Recibe el hashcode calculado por el servidor.
        
        hashcode_server = sck.recv(1024).decode("utf-8")
        logger.info(f' Cliente #{self.numcliente}: Se recibió el codigo hash del archivo calculado por el servidor. Hashcode: "{hashcode_server}".') 

        ### Hashcode calculado por el cliente.
        hashcode_cliente = self.hash_file(self.filepath)
        logger.info(f' Cliente #{self.numcliente}: Se calculó el codigo hash del archivo recibido. Hashcode: "{hashcode_cliente}".') 
        
        if(hashcode_server == hashcode_cliente ):
            logger.info(f' Cliente #{self.numcliente}: La integridad del archivo se conservó, los hashcode entre servidor y cliente coinciden.')
        
        #barrier.wait()
    
    def hash_file(self, filename):
       """"This function returns the SHA-1 hash
       of the file passed into it"""
    
       # make a hash object
       h = hashlib.sha1()
    
       # open file for reading in binary mode
       with open(filename,'rb') as file:
    
           # loop till the end of the file
           chunk = 0
           while chunk != b'':
               # read only 1024 bytes at a time
               chunk = file.read(1024)
               h.update(chunk)
    
       # return the hex representation of digest
       return h.hexdigest()


if __name__ == '__main__':

    #We need one party for each thread we intend to create, five in this place, 
    #as well as an additional party for the main thread that will also wait for all threads to reach the barrier.
    barrier = threading.Barrier(n_conn+1 )
    
    # Get local machine name
    HOST = socket.gethostname() 
    PORT = 50000       
    logger.info(f' AppCliente: Iniciando la aplicación de clientes con el servidor {HOST} en el puerto {PORT}.') 
    
    i=1
    clientes_list = []
    while i <= n_conn:   
        print("Iniciando la conexión del cliente", i)
        logger.info(f' AppCliente: Iniciando la conexión del cliente {i}.') 
        s = ThreadedClient(i, n_conn, HOST, PORT, tipo_archivo, logging)
        s.start()
        clientes_list.append(s)
        i+=1
    print("Todos las conexiones fueron exitosas, listos para iniciar la recepción del archivo.")
    barrier.wait() ## barrier + 1 

    #barrier = threading.Barrier(n_conn+1 )
    for s in clientes_list:
        
        s.start_receive_file()
    #barrier.wait()
    #logger = None

#s.sendall(bytes('Hello, world', 'utf-8'))
#data = s.recv(1024)


#print ('Received', repr(data))