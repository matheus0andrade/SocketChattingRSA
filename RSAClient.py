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

# Calcula as chaves
p1, p2 = 898786383457667206197046368158981884276004377885724162490725557499822194198051453400005909737230444720537, 202521804362139152326139566291737927779519979342264374276326396984636956656401768419713644985940066612647
modulo = p1 * p2
phi = (p1 - 1) * (p2 - 1)
exp = 65537
inv = pow(exp, -1, phi)
size = math.ceil(math.log(modulo, 256))

def crypt(msg):
    return binexp(msg, inv, modulo)

with socket(AF_INET, SOCK_STREAM) as sock:
    sock.bind((HOST, PORT))
    sock.listen()
    conn, addr = sock.accept()
    with conn:
        print('Connected by', addr)
        # Envia as chaves para o cliente
        conn.sendall(modulo.to_bytes(size, 'big'))
        conn.sendall(exp.to_bytes(size, 'big'))
        while True:
            data = conn.recv(1024)
            if not data: break
            recieved = b''
            for i in range(0, len(data), size):
                recieved += crypt(int.from_bytes(data[i:i + size], 'big')).to_bytes(size - 1, 'big')
            print("Recebido: ", end='')
            for b in recieved:
                if b == 0:
                    print()
                    break
                print(chr(b), end='')
            r = input("Envie uma mensagem: ")
            c = (r == 'exit')
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
            conn.sendall(new)
            if c:
                break
            print("Espere a resposta do outro lado...")
