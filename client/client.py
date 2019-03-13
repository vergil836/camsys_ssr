import socket
import os
import hashlib
import cv2
import numpy
from time import sleep

client = socket.socket()

ip_port =("127.0.0.1", 6964)  #地址和端口号

client.connect(ip_port)  #连接

print("服务器已连接")

if not os.path.exists("photo"):
    os.mkdir("photo")
while True:
    
    #手动挡,输入shoot拍摄
    #cmd = input(">>")
    #interval = 0
    
    #自动档
    cmd = "shoot"
    interval = 1

    if len(cmd)==0: continue
    else:
        client.send(cmd.encode("utf-8"))
        #接受拍摄时间
        img_time = client.recv(1024).decode("utf-8")
        client.send("time got".encode("utf-8"))

        #接收长度
        server_response = client.recv(1024)
        im_size = int(server_response.decode("utf-8"))
        print("接收到的大小：", im_size)
        client.send("size got".encode("utf-8"))

        #接受长宽
        frame_raw_num=int(client.recv(1024).decode("utf-8"))
        print("raw:",frame_raw_num)
        client.send("raw got".encode("utf-8"))
        frame_column_num=int(client.recv(1024).decode("utf-8"))
        print("column",frame_column_num)

        #接收文件内容
        client.send("ready".encode("utf-8"))  #接收确认
        
        received_size = 0
        m = hashlib.md5()
        frame_bytes=b""

        while received_size < im_size:
            size = 0  #准确接收数据大小，解决粘包
            if im_size - received_size > 1024: #多次接收
                size = 1024
            else:  #最后一次接收
                size = im_size - received_size

            data = client.recv(size)  # 多次接收内容，接收大数据
            frame_bytes += data
            data_len = len(data)
            received_size += data_len
            print("已接收：", int(received_size/im_size*100), "%")

            m.update(data)

        
        client.send("check".encode("utf-8"))
        #md5值校验
        md5_server = client.recv(1024).decode("utf-8")
        md5_client = m.hexdigest()
        print("服务器发来的md5:", md5_server)
        print("接收文件的md5:", md5_client)
        if md5_server == md5_client:
            print("MD5值校验成功")
        else:
            print("MD5值校验失败")
        #解码
        frame=numpy.frombuffer(frame_bytes,dtype=numpy.uint8).reshape(frame_raw_num,frame_column_num)
        cv2.imwrite("photo/%s.png"%img_time,frame)

        sleep(interval)

client.close()