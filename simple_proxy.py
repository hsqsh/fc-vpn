import socket
import threading
import select

LISTEN_HOST = '0.0.0.0'
LISTEN_PORT = 8888

def handle_client(client_sock):
    try:
        # 1. 握手阶段
        ver, nmethods = client_sock.recv(2)
        methods = client_sock.recv(nmethods)
        # 只支持无认证
        client_sock.sendall(b'\x05\x00')

        # 2. 请求阶段
        ver, cmd, _, atyp = client_sock.recv(4)
        if atyp == 1:  # IPv4
            addr = socket.inet_ntoa(client_sock.recv(4))
        elif atyp == 3:  # 域名
            domain_len = client_sock.recv(1)[0]
            addr = client_sock.recv(domain_len).decode()
        else:
            client_sock.close()
            return
        port = int.from_bytes(client_sock.recv(2), 'big')

        # 只支持 CONNECT
        if cmd != 1:
            client_sock.close()
            return

        # 连接目标服务器
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((addr, port))
        # 回复客户端连接成功
        reply = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + (8888).to_bytes(2, 'big')
        client_sock.sendall(reply)

        # 开始转发数据
        sockets = [client_sock, remote]
        while True:
            r, _, _ = select.select(sockets, [], [])
            for s in r:
                data = s.recv(4096)
                if not data:
                    client_sock.close()
                    remote.close()
                    return
                if s is client_sock:
                    remote.sendall(data)
                    print(f"[FORWARD] {addr}:{port} <- 客户端发来 {len(data)} 字节")
                else:
                    client_sock.sendall(data)
                    print(f"[FORWARD] {addr}:{port} -> 返回客户端 {len(data)} 字节")
    except Exception as e:
        print("Error:", e)
        client_sock.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LISTEN_HOST, LISTEN_PORT))
    server.listen(5)
    print(f"SOCKS5 proxy listening on {LISTEN_HOST}:{LISTEN_PORT}")
    while True:
        client_sock, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    main()
