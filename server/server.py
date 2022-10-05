import hashlib
import os
import socket
import struct
import threading
import logging
import datetime
import time


def send_file(sck: socket.socket, filename):
    # Obtener el tamaño del archivo a enviar.
    filesize = os.path.getsize(filename)
    # Informar primero al servidor la cantidad
    # de bytes que serán enviados.
    sck.sendall(struct.pack("<Q", filesize))
    time_start = time.time()
    # Enviar el archivo en bloques de 1024 bytes.
    with open(filename, "rb") as f:
        while read_bytes := f.read(1024):
            sck.sendall(read_bytes)
    return time.time() - time_start

def on_new_client(clientsocket,addr, num_cliente):
    while True:
        
        logger_s.info(f' Server-Cliente #{num_cliente}:' + 
                     f'Inicio del manejador de la conexión, la dirección y puerto asociados son {addr}.')
        
   
        #do some checks and if msg == someWeirdSignal: break:
        tipo_archivo = clientsocket.recv(1024).decode("utf-8")
        
        filename = filename_0 if str(tipo_archivo ) == '0' else filename_1
        
        logger_s.info(f' Server-Cliente #{num_cliente}: ' 
                     +  f'El tipo de archivo solicitado por el cliente es {filename} ({tipo_archivo}) cuyo tamaño es de {os.path.getsize(filename)}B .')
        
        
             
        logger_s.info(f' Server-Cliente #{num_cliente}:' + 
                     'Enviando el nombre del archivo al cliente.')
        
        clientsocket.sendall("Envie un 1 si se encuentra listo para la recepcion del archivo {0}".format(filename).encode())   
           
        logger_s.info(f' Server-Cliente #{num_cliente}: Se le envió la solicitud de confirmación al cliente. En espera.')

        confirmacion = clientsocket.recv(1024).decode("utf-8")
        if confirmacion == '1': 
            logger_s.info(f' Server-Cliente #{num_cliente}: El cliente ha confirmado que esta listo para recibir el archivo.')  
  
        

        logger_s.info(f' Server-Cliente #{num_cliente}: Enviando archivo...')  
        try:
            tiempo_envio = send_file(clientsocket, filename)
            tiempo_envio = round(tiempo_envio, 5)
            logger_s.info(f' Server-Cliente #{num_cliente}: Envio finalizado con exito. El tiempo de transferencia fue de {tiempo_envio} segundos.') 
        except:
            logger_s.info(f' Server-Cliente #{num_cliente}: Envio finalizado sin exito.') 
        ## Envío del hashcode
        hash_code = hash_file(filename)
        clientsocket.sendall(hash_code.encode())
        logger_s.info(f' Server-Cliente #{num_cliente}: El hash del archivo enviado es {hash_code}. Se envió el codigo hash calculado al cliente.')
        break
      
    clientsocket.close()


def hash_file(filename):
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



now = datetime.datetime.now()
## Creación del logger_s
logging.basicConfig(filename=f'{now.year}-{now.month}-{now.day}-{now.hour}-{now.minute}-{now.second}-log.txt', 
                             encoding='utf-8',
                             format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                             level=logging.INFO,
                             datefmt='%Y-%m-%d %H:%M:%S')
logger_s = logging.getLogger("server_logger")

filename_0 = "archivo_100mb.zip"

filename_1 = "archivo_250mb.zip"
filesize = 0
    
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
#host = "192.168.9.120"
port = 50000                # Reserve a port for your service.
logger_s.info(f' Server: El servidor {host} en el puerto {port} ha sido inicializado.')
logger_s.info(' Server: Esperando por clientes.')


s.bind((host, port))        # Bind to the port
s.listen(5)                 # Now wait for client connection.

num_cliente_actual = 1
while True:
    c, addr = s.accept()     # Establece la conexión con el cliente.
    logger_s.info(f' Server: Se ha recibido y aceptado la petición de conexión del cliente {num_cliente_actual}.')
    th = threading.Thread(target=on_new_client, args=(c,addr, num_cliente_actual))
    
    logger_s.info(f' Server: Se le ha asignado un hilo al cliente {num_cliente_actual} para el manejo de sus peticiones.')
    th.start()   
    num_cliente_actual+=1
s.close()