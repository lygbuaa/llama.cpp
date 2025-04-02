#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time, threading, socket, struct, sys, json
# import numpy as np

def GfCheckSocketBuffer(sock):
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
    rcvbuf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    sndbuf = sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
    print("rcvbuf: {}, sndbuf: {}".format(rcvbuf, sndbuf))

class ThreadBase(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        self.preprocess = kwargs.pop('preprocess')
        super(ThreadBase, self).__init__(target=self.loop_with_callback, *args, **kwargs)
        self.callback = callback
        self.callback_args = callback_args

    def loop_with_callback(self):
        while True:
            if self.preprocess is not None:
                self.preprocess()
            if self.callback is not None:
                self.callback(*self.callback_args)

class SocketServer(object):
    def __init__(self, host="127.0.0.1", port=10001, len=1024, type=socket.SOCK_STREAM):
        self.host = host
        self.port = port
        self.data_len = len
        self.msg = None
        self.counter = 0
        self.conn = None
        self.type = type
        self.client_addr = None

        # self.dst_addr = ("192.168.1.102", 10000)
        if type == socket.SOCK_DGRAM:
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_server.bind((host, port))
        elif type == socket.SOCK_STREAM:
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_server.bind((host, port))
            self.socket_server.listen()
            (self.conn, self.client_addr) = self.socket_server.accept()
            print("accept client address: {}".format(self.client_addr))
        else:
            raise SystemError("socket type {} not supported !".format(type))
        
        GfCheckSocketBuffer(self.socket_server)
        self.socket_server.setblocking(True)
        print("udp server listen on {}:{}".format(self.host, self.port))

    def recv_msg(self):
        if self.type == socket.SOCK_DGRAM:
            self.msg, addr = self.socket_server.recvfrom(self.data_len)
        elif self.type == socket.SOCK_STREAM:
            self.msg = self.conn.recv(self.data_len)
            addr = self.client_addr
        else:
            raise SystemError("socket type {} not supported !".format(type))

        if not self.msg:
            print("recv error, loop quit")
            # self.th._stop()
            sys.exit(1)
        recvtime = time.time()
        if self.counter % 1 == 0:
            print("recv [{}] msg from client {}, timestamp {}sec".format(self.counter, addr, recvtime))
        self.counter += 1

    def post_process(self, msg):
        print("this is SocketServer base stub!")

    def start_recv_thread(self, run_background=True):
        try: 
            self.th = ThreadBase(name="recv_thread", preprocess=self.recv_msg, callback=self.post_process, callback_args=(self.msg,))
            self.th.setDaemon(run_background)
            self.th.start()
            print("recv thread start")
        except Exception as err:
            print("start_recv_thread error: {}".format(err))

class SocketClient(object):
    def __init__(self, host="127.0.0.1", port=2369, type=socket.SOCK_STREAM):
        self.host = host
        self.port = port
        self.dst_addr = (host, port)
        self.type = type
        self.data_len = 3 ### 3 bytes for each chinese character.
        self.counter = 0
        self.msg = bytearray()
        self.full_resp = bytearray()

        if type == socket.SOCK_DGRAM:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #SOCK_STREAM
            GfCheckSocketBuffer(self.socket_client)
        elif type == socket.SOCK_STREAM:
            self.socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            GfCheckSocketBuffer(self.socket_client)
            self.socket_client.connect((host, port))
            print("client connect to {}:{}".format(host, port))
        else:
            raise SystemError("socket type {} not supported !".format(type))
        print("udp server will send to {}:{}".format(self.host, self.port))

    def send_list(self, data_list=[]):
        msg = bytearray(data_list)
        print("send msg: {}".format(msg))
        self.socket_client.sendto(msg, self.dst_addr)

    def send_array(self, data_array):
        self.socket_client.sendto(data_array, self.dst_addr)
        self.full_resp = bytearray()

    def recv_msg(self):
        if self.type == socket.SOCK_DGRAM:
            self.msg, addr = self.socket_client.recvfrom(self.data_len)
        elif self.type == socket.SOCK_STREAM:
            self.msg = self.socket_client.recv(self.data_len)
        else:
            raise SystemError("socket type {} not supported !".format(type))

        if not self.msg:
            print("recv error, loop quit")
            # self.th._stop()
            sys.exit(1)
        recvtime = time.time()
        if self.counter % 1 == 0:
            print("recv [{}] msg from server, timestamp {}sec".format(self.counter, recvtime))
        self.counter += 1

    def post_process(self, msg):
        # print("this is SocketServer base stub!")
        msg_str = str(self.msg, encoding='utf-8')
        print("recv msg_str: {}".format(msg_str))
        self.full_resp += self.msg

    def start_recv_thread(self, run_background=True):
        try: 
            self.th = ThreadBase(name="recv_thread", preprocess=self.recv_msg, callback=self.post_process, callback_args=(self.msg,))
            self.th.setDaemon(run_background)
            self.th.start()
            print("recv thread start")
        except Exception as err:
            print("start_recv_thread error: {}".format(err))


def run_client():
    s_client = SocketClient(host="192.18.34.101", port=10001, type=socket.SOCK_STREAM)
    s_client.start_recv_thread()
    counter = 0
    msg = bytearray(1024) #1024
    msg.__init__(len(msg))
    image1_path_json = {"image_filename": "bridge_640_360.jpg", "prompt": u"描述一下这张图片?"}
    image2_path_json = {"image_filename": "hhl_360_540.jpg", "prompt": u"描述一下这张图片?"}
    q1_prompt_json = {"prompt": u"刚才输入的图片是哪个地方?"}
    q2_prompt_json = {"prompt": u"刚才输入的图片中有几辆汽车?"}
    q3_prompt_json = {"prompt": u"刚才输入的图片中有几个行人?"}
    q4_prompt_json = {"prompt": u"刚才输入的图片中有几辆公交车?"}
    q5_prompt_json = {"prompt": u"刚才输入的图片中有几辆摩托车?"}

    msg = bytearray(1024) #1024
    msg.__init__(len(msg))
    # str_header = u"你好..."
    msg_str = bytearray(json.dumps(image1_path_json), "utf-8")
    # msg_str = bytearray(u"图片中是哪个景点", "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("image_filename: {}, prompt: {}".format(image1_path_json["image_filename"], image1_path_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(30.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q1_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q1_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(15.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q2_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q2_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q3_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q3_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q4_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q4_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q5_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q5_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(image2_path_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(image2_path_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(30.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q1_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q1_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(15.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q2_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q2_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))

    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q3_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q3_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q4_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q4_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


    msg.__init__(len(msg))
    msg_str = bytearray(json.dumps(q5_prompt_json), "utf-8")
    msg[0:len(msg_str)] = msg_str
    print("prompt: {}".format(q5_prompt_json["prompt"]))
    print("request: {}".format(msg_str))
    s_client.send_array(msg)
    time.sleep(5.0)
    print("response: {}".format(str(s_client.full_resp, encoding='utf-8')))


if __name__ == "__main__":
    print("********** running test ************")
    run_client()