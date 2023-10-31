import socket
import sys
from io import StringIO

localIP     = "0.0.0.0"
bufferSize  = 8192
# Listen for incoming datagrams
def main(prefix: str,port: int):

    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


    # Bind to address and ip
    UDPServerSocket.bind((localIP, port))

 

    print(f"[{prefix}] UDP server up and listening")
    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        string_io = StringIO(message.decode())

        for line in string_io.readlines():
            print(f"[{prefix}] [{address[0]}] {line}",end='')


if __name__ == '__main__':
    main(sys.argv[1],int(sys.argv[2]))