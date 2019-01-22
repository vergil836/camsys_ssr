import socket
import time
import hashlib
import camera
import cv2
import numpy

server = socket.socket()

server.bind(("127.0.0.1", 6964))    #地址和端口号

server.listen(5) #监听

print("监听开始..")

while True:
    conn, addr = server.accept()

    print("conn:", conn, "\naddr:", addr)

    while True:
        data = conn.recv(1024)
        if not data:
            print("客户端断开连接")
            break

        print("收到的命令：", data.decode("utf-8"))
        cmd = data.decode("utf-8")
        if cmd =="shoot":
                cap = cv2.VideoCapture(0)
                frame = cap.read()[1]
                frame_enc = frame[:,:,0].tostring()
                print("开始发送")
                #发送时间
                t = time.time()
                sec = (t - int(t))*1000
                t_str = time.strftime("%Y-%m-%d %H:%M:%S.",time.localtime(t))
                t_str += "%03d"%sec
                print(t_str)
                conn.send(t_str.encode("utf-8"))
                conn.recv(1024)
                #发送大小
                size = len(frame_enc)
                conn.send(str(size).encode("utf-8"))
                print("发送的大小：", size)
                conn.recv(1024)
                #发送长宽
                frame_raw_num=frame.shape[0]
                frame_column_num=frame.shape[1]
                conn.send(str(frame_raw_num).encode("utf-8"))
                conn.recv(1024)
                conn.send(str(frame_column_num).encode("utf-8"))
                conn.recv(1024)

                #发送文件内容
                m = hashlib.md5()
                conn.send(frame_enc)
                m.update(frame_enc)
                conn.recv(1024)

                #md5校验
                md5 = m.hexdigest()
                conn.send(md5.encode("utf-8"))
                print("md5:", md5)
        if cmd =="exit":
            server.close()
            exit()
