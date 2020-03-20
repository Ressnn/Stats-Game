import socket
import threading
import socketserver
from ast import literal_eval
import math
import struct
from threading import Timer
import secrets
import random
import numpy as np

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


buffer_size = 100
run_on_client_data_list = []
active_clients = []
active_tanks = {}
heal_hurt = np.random.choice([True,False])



def buildnewtanksettings(tankid):
    data = {
    'tankid':tankid,
    'posx':-200,
    'posy':-300,
    'rot':0,
    'health':75,
    'bullets':[],
    'FT':heal_hurt,
    'Dash':False
    }
    active_tanks[tankid] = data

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def BulletUpdate():
    for i in active_clients:
        for a in range(0,len(active_tanks[i]['bullets'])):
            bulletspeed = 10
            active_tanks[i]['bullets'][a][0] = active_tanks[i]['bullets'][a][0]+bulletspeed*math.sin(active_tanks[i]['bullets'][a][2])
            active_tanks[i]['bullets'][a][1] = active_tanks[i]['bullets'][a][1]+bulletspeed*math.cos(active_tanks[i]['bullets'][a][2])
            active_tanks[i]['bullets'][a][3] = active_tanks[i]['bullets'][a][3]-1
            
            if active_tanks[i]['bullets'][a][3] <= 0:
                active_tanks[i]['bullets'].pop(a)
                
def HealHurtUpdate():
    switch = np.random.choice([True,False],p=[.3,.7])
    for i in list(active_tanks.keys()):
        if switch:
            active_tanks[i]['FT'] = not(active_tanks[i]['FT'])
smult = np.random.normal(15,2.5)
def smultupdate():
    global smult
    sstand = (smult-15)/5
    
    smult = np.random.normal(15-sstand*4,3)                
    if smult>20:
        smult = 20
    if smult<10:
        smult = 10
    print(smult)



RepeatedTimer(3,smultupdate)
RepeatedTimer(.0166,BulletUpdate)
RepeatedTimer(.5,HealHurtUpdate)

class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):

    def handle(self):
        kill = False
        while kill==False:
            dataz = str(self.request.recv(buffer_size), 'ascii').split("|")
            
            for data in dataz:
                if data:
                    self.speedmultipler = 7
                    cur_thread = threading.current_thread()
                    for i in run_on_client_data_list:
                        i(bytes(data,"utf-8"))
                    data = data.split(":")
                    if data[0] == "ServerTest":
                        self.request.sendall(bytes("Connected","utf-8"))
                        print((self.client_address[0],data[0],data[1]))
                        active_clients.append(data[1])
                        buildnewtanksettings(data[1])
                        print(active_clients)
                    if data[0] == "Disconnect":
                        try:
                            print("Disconnected:"+str(data[1]))
                            active_clients.remove(data[1])
                            active_tanks.pop(data[1])
                            kill = True
                            print(active_clients)
                        except:
                            print("Disconnect Failed")
                            
                            
                    if data[0] =="Dash":
                        tank = active_tanks[data[1]]
                        tank['Dash'] = not(tank['Dash'])
                    if data[0] =="DashQ":
                        tank = active_tanks[data[1]]
                        tank['Dash'] = False
                    if data[0] =="Update":
                        transmittion = bytes(str(active_tanks),'utf-8')
                        msg = transmittion
                        msg = struct.pack('>I', len(msg)) + msg
                        self.request.sendall(msg)
                    if data[0] == "w":
                        tank = active_tanks[data[1]]
                        if tank['Dash'] == True:
                            self.speedmultipler = smult
                        tank['posy'] = tank['posy'] + self.speedmultipler*math.cos(tank['rot'])
                        tank['posx'] = tank['posx'] + self.speedmultipler*math.sin(tank['rot'])
                    if data[0] == "s":
                        if tank['Dash'] == True:
                            self.speedmultipler = smult
                        tank = active_tanks[data[1]]
                        tank['posy'] = tank['posy'] - self.speedmultipler*math.cos(tank['rot'])
                        tank['posx'] = tank['posx'] - self.speedmultipler*math.sin(tank['rot'])
                    if data[0] == 'a':
                        tank = active_tanks[data[1]]
                        tank['rot'] = tank['rot']+math.radians(5)
                    if data[0] == 'd':
                        tank = active_tanks[data[1]]
                        tank['rot'] = tank['rot']-math.radians(5)
                    if data[0] == "Fire":
                        tank = active_tanks[data[1]]
                        tank['health'] = tank['health']-np.random.normal(2,2)
                        tank['bullets'].append([tank['posx'],tank['posy'],tank['rot'],200,secrets.token_hex(10),tank['tankid'],np.random.normal(20,10)])
                    if data[0] == "Dead":
                        tank = active_tanks[data[1]]
                        possible_spawn_locations = [[-258,-1181],[-1177,-1263],[-2525,-1005],[-2530,-339],[-1305,-232]]
                        
                        spawn_point = possible_spawn_locations[np.random.randint(0,5)]
                        tank['health'] = 75
                        tank['posx'] = spawn_point[0]
                        tank['posy'] = spawn_point[1]
                        
                        
                        
                        
                        
                    if data[0] == "Hit":
                        tank = active_tanks[data[1]]
                        tank['health'] = tank['health']-np.random.normal(5,2.5)
                        if np.random.choice([False,True],p=[.997,.003]):
                            tank['health'] = tank['health']-100
                            print("Critial Hit")
                    if data[0] == "Heal":
                        tank = active_tanks[data[1]]
                        ad = np.random.normal(5,3.5)
                        if tank['health']<100:
                            if tank['health']+ad>100:
                                tank['health'] = 100
                            else:
                                tank['health'] = tank['health']+ad
                        if np.random.choice([False,True],p=[.997,.003]):
                            tank['health'] = 200
                            print("Critial Heal")
                            
                            
                            
                            
                
            
        
        
        
        
        
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# Port 0 means to select an arbitrary unused port
HOST, PORT = str(input("What Is your IP?")), 10000
server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
ip, port = server.server_address
# Start a thread with the server -- that thread will then start one
# more thread for each request
server_thread = threading.Thread(target=server.serve_forever)
# Exit the server thread when the main thread terminates
server_thread.daemon = True
server_thread.start()


class GameServer():
    def __init__(self):
        self.s = 0
        run_on_client_data_list.append(self.clientdataloop)
        while True:
            self.RunLoop()
    def RunLoop(self):
        pass
    def clientdataloop(self,data):
        return True
            
        
        
        
        
G = GameServer()


#server.shutdown()
#server.server_close()