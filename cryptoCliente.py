import math
from socket import *
HOST, PORT = "192.168.56.1", 40000

def binexp(a, b, n):
    r = 1
    while b:
        if b & 1:
            r = (r * a) % n
        a = (a * a) % n
        b >>= 1
    return r

modulo, exp, size = 0, 0, 0
def crypt(msg):
    return binexp(msg, exp, modulo)

with socket(AF_INET, SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))

    # Recebe a chave (mod, exp)
    data = sock.recv(1024)
    modulo = int.from_bytes(data, 'big')
    data = sock.recv(1024)
    exp = int.from_bytes(data, 'big')

    size = math.ceil(math.log(modulo, 256))
    while True:
        r = input("Digite a mensagem: ")
        new, block = b'', b''
        for i in range(0, len(r)):
            block += ord(r[i]).to_bytes(1, byteorder='big')
            if i % (size - 1) == (size - 2):

                block = int.from_bytes(block, byteorder='big')
                block = crypt(block)
                new = new + block.to_bytes(size, byteorder='big')
                block = b''
        if(len(block) > 0):
            block += b'\x00' * (size - 1 - len(block))
            block = int.from_bytes(block, byteorder='big')
            block = crypt(block)
            new = new + block.to_bytes(size, byteorder='big')
        sock.sendall(new)
        print("Espere a resposta do outro lado...")
        data = sock.recv(1024)
        recieved = b''
        for i in range(0, len(data), size):
            cur = int.from_bytes(data[i:i + size], 'big')
            recieved += crypt(cur).to_bytes(size - 1, 'big')
        print("Recebido: ", end='')
        for b in recieved:
            if b == 0:
                print()
                break
            print(chr(b), end='')
        if r == "exit":
            break