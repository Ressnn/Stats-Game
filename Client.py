 # -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 10:25:29 2019

@author: Pranav Devarinti
"""
import pygame
import socket
from ast import literal_eval
import time
import secrets
import struct
import numpy as np
#import matplotlib.pyplot as plt
import math
import asyncio
import nest_asyncio
nest_asyncio.apply()
loopmelist = []
loop = asyncio.get_event_loop()
from threading import Thread
async def loopme():
    for i in loopmelist:
        i()
        print("looped")
    
    
loop.create_task(loopme())


pygame.init()
class Datahandler():
    def __init__(self):
        self.updates = []
        self.id = str(secrets.token_hex(10))
        connection_worked = False
        while connection_worked == False:
            self.TCP_IP = input("What is the ip?")
            self.TCP_PORT = int(input("What is the port?"))
            self.BUFFER_SIZE = 100
            self.serverconnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverconnection.connect((self.TCP_IP,self.TCP_PORT))
            self.serverconnection.send(bytes("ServerTest:"+self.id,"utf-8"))
            data = str(self.serverconnection.recv(self.BUFFER_SIZE),"utf-8")
            if data:
                print(data)
                connection_worked = True
            else:
                print("Connection Failed Try Again")
        self.logs = []
        self.AskUpdate()
        loopmelist.append(self.AskUpdate)
        self.NewConnection()
        self.serverconnection.send(bytes("|Update",'utf-8'))
        data = self.recv_msg()
        self.updates = eval(str(self.Decode(data)))
#        print("updated")
    def NewConnection(self):
        return True

    def Encode(self,encode):
        return bytes("|"+str(encode),"utf-8")
    def Decode(self,decode):
        return str(bytes(decode),"utf-8")
    async def askupdate(self):
        loop.run_until_complete(self.AskUpdate())
#        print('update_asked')
        return True
    async def AskUpdate(self):
        self.NewConnection()
        self.serverconnection.send(self.Encode("Update"))
        data = self.recv_msg()
        try:
            self.updates = eval(str(self.Decode(data)))
        except:
            pass 
#        print("updated")
        return True
    
    def PostToServer(self,data):
        self.serverconnection.send(self.Encode(data))
    def AskSpecific(self,data):
        self.NewConnection()
        self.serverconnection.send(self.Encode(data))
        return self.serverconnection.recv(self.BUFFER_SIZE)
    
    def recv_msg(self):
        sock = self.serverconnection
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(4)
#        print(raw_msglen)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        
        # Read the message data
        return self.recvall(msglen)

    def recvall(self,n):
        # Helper function to recv n bytes or return None if EOF is hit
        sock = self.serverconnection
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
#            print(packet)
            if not packet:
                return None
            data.extend(packet)
        return data

class Fountain(pygame.sprite.Sprite):
    def __init__(self,display,mode):
        self.healimg = pygame.image.load("Assets/Pool/Heal.png")
        self.hurtimg = pygame.image.load("Assets/Pool/Hurt.png")
        self.healimg = pygame.transform.scale(self.healimg, (450,450))
        self.hurtimg = pygame.transform.scale(self.hurtimg, (450,450))
        self.display = display
        self.rect = self.healimg.get_rect()
    def update(self,mode,z,tank):
        x,y = z
        if mode:
            self.display.blit(self.healimg,(x,y))
        else:
            self.display.blit(self.hurtimg,(x,y))
        self.rect = self.healimg.get_rect(topleft=(x,y))
        
        collisions = pygame.sprite.spritecollide(self,[tank],False)
        
        if collisions:
            return True
        else:
            return False
        print(collisions)
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location,display):
        self.length = 3000
        self.height = 1500
        self.display = display
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left = location 
        self.rect.top = location
        self.image = pygame.transform.scale(self.image, (self.length,self.height))
        self.getshadowmap("Assets/ShadowMap.png")
    def loopfunc(self,x,y,renderdistance):
        self.x = x
        self.y = y
        self.display.fill([255, 255, 255])
        self.display.blit(self.image, (self.x+500,self.y+400))
        
        
    def getshadowmap(self,img_file):
        self.shadow = pygame.image.load(img_file)
        self.shadow = pygame.transform.scale(self.shadow, (self.length,self.height))
        self.hitmap = np.array(pygame.surfarray.array3d(self.shadow))[:,:,0]
        self.hitmap = np.transpose(self.hitmap)
    
    
    
    def collisioncheck(self,x,y):
        rect = ((0,0),(100,-100))
#        print(x)
        xi = int(-x+rect[1][0])
        yi = int(-(y+rect[1][1]))
        self.h = self.hitmap[int(-y):yi,int(-x):xi]
#        print(xi,yi)
        if np.std(self.h.reshape(-1))>0:
            return False
        else:
            return True
    
        
        
#        print((rect.topleft,rect.bottomright))


class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,image_file,display,bid,dmg,tankid):
        self.display = display
        self.tankid = tankid
        self.x = x
        self.y = y
        self.bid = bid
        self.dmg = dmg
        self.imageo = image_file
        self.display.blit(self.imageo,(self.x,self.y))
        self.rect = self.imageo.get_rect(topleft=(self.x, self.y))
    def update(self,x,y):
        self.x = x
        self.y = y
        self.display.blit(self.imageo, (self.x,self.y))
    def HitCheck(self,tank):
        collisions = pygame.sprite.spritecollide(self,[tank],False)
        if collisions:
            if self.tankid == tank.tankid:
                return False
                
            else:
                print("Hit Detected")
                return True
        else:
            return False
        print(collisions)
class Tanks(pygame.sprite.Sprite):
    def __init__(self,tankid,x,y,rot,image_file,display):
        self.lastx = 0
        self.lasty = 0
        self.display = display
        self.tankid = tankid
        self.x = x
        self.y = y
        self.rot = rot
        self.imageo = pygame.image.load(image_file)
        self.imageo = pygame.transform.scale(self.imageo, (100,100))
        self.rect = self.imageo.get_rect()
    def update(self,x,y,rot,health):
        self.x = x
        self.y = y
        self.image = pygame.transform.rotate(self.imageo,math.degrees(rot))
        self.display.blit(self.image, (self.x,self.y))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.healthbar(health)
    def delete(self):
        self.kill()
    def healthbar(self,health):
        if health<0:
            return True
        bar_length = 100
        r = (bar_length-health)/100
        g = 1-r
        b = 0
        if health>99 and health<200:
            colour = [51,171,240]
        elif health<=99:
            colour = [int(255*r),int(255*g),int(255*b)]
        elif health>=200:
            colour = [0,0,0]
        pygame.draw.line(self.display, colour, [self.x, self.y-10], [self.x+100, self.y-10], 10)
        
class ButtonBar():
    def __init__(self,img_using,img_unable,img_able,x,y,display,s1,s2):           
        self.R = pygame.image.load(img_able)
        self.NR = pygame.image.load(img_unable)
        self.U = pygame.image.load(img_using)
        self.x = x
        self.y = y
        self.disp = display
        self.R = pygame.transform.scale(self.R, (s1, s2))
        self.NR = pygame.transform.scale(self.NR, (s1, s2))
        self.U = pygame.transform.scale(self.U, (s1, s2))
    def update(self,State):
        if State == 0:
            self.disp.blit(self.NR, (self.x,self.y))
        if State == 1:
            self.disp.blit(self.R, (self.x,self.y))
        if State == 2:
            self.disp.blit(self.U, (self.x,self.y))

class ProgressBar():
    def __init__(self,x1,x2,y1,y2,thickness,display):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.display = display
        self.thickness = thickness
    def update(self,pct):
        pct = 1-pct
        self.endy = (abs(self.y1-self.y2))*pct+self.y1
        colour = [255,0,0]
        colour2 = [0,255,0]
        pygame.draw.line(self.display, colour2, [self.x1,self.y1], [self.x2,self.y2], self.thickness)
        pygame.draw.line(self.display, colour, [self.x1,self.y1], [self.x2,self.endy], self.thickness)
        
        
        
class Game():
    def __init__(self):
        print("Game-Starting")
        self.DH = Datahandler()
        self.framelooplist = []
        self.w =1000
        self.h = 800
        self.gameDisplay = pygame.display.set_mode((self.w,self.h))
        pygame.display.set_caption('Tanks')
        self.clock = pygame.time.Clock()
        self.Bkg = Background("Assets/Map.png",0,self.gameDisplay)
        self.x = 0
        self.y = 0
        self.health = 0
        self.rot = 0
        self.render_distance = 30
        self.speed_multipler = 10
        self.active_tank_dict = dict()
        self.active_bullet_dict = dict()
        self.bullet = pygame.image.load("Assets/Bullet.png")
        self.cooldown = 0
        self.FTS = 0
        self.FTSS = 0
        self.SFIRE = np.random.geometric(.3)
        self.SpecialUse = False
        self.FT = Fountain(self.gameDisplay,False)
        self.gameCounter = 0
        self.speedmeter = 100
        self.past = False
        self.SPU = False
        self.RapidFire = ButtonBar("Assets/Buttons/RapidFire/Charging.png","Assets/Buttons/RapidFire/Full.png","Assets/Buttons/RapidFire/Charging.png",750,700,self.gameDisplay,175,100)
        self.GasMeter = ProgressBar(1000,1000,600,800,100,self.gameDisplay)
        
        
        print(self.DH.id)
        while True:
            self.frameloop()
        pygame.key.set_repeat(0,10)
        thread = Thread(target=lambda: self.Renderloop())
        thread.start()
    def Renderloop(self):
        self.Bkg.loopfunc(self.x,self.y,self.render_distance)
    
    
    
    
    def Update_Own_Values(self,updatearray):
        value_set = updatearray[self.DH.id]
        self.x = value_set['posx']
        self.y = value_set['posy']
        self.health = value_set['health']
        self.rot = value_set['rot']
        
    def start_event_loop(self):
        while True:
            self.DH.askupdate()   
    
    
    
    
    def frameloop(self):
        self.gameCounter = self.gameCounter+1
        if self.cooldown >0:
            self.cooldown =self.cooldown-1
        asyncio.run(self.DH.AskUpdate())
        self.update_array = self.DH.updates
        self.Update_Own_Values(self.update_array)
        self.GasMeter.update(self.speedmeter/100)
        for i in self.framelooplist:
            i()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.DH.PostToServer("Disconnect:"+self.DH.id)
                time.sleep(.1)
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.cooldown == 0:
                        print("spacebar was pressed")
                        self.DH.PostToServer("Fire:"+self.DH.id)
                        self.cooldown = 30
                if event.key == pygame.K_z:
                    if self.FTS == 0:
                        self.SFIRE = np.random.geometric(.3)
                        self.SpecialUse = True
                        self.FTS = 300
                if event.key == pygame.K_x:
                    if self.speedmeter>0:
                        self.DH.PostToServer("Dash:"+self.DH.id)
                        self.SPU = not(self.SPU)
        if self.FTS == 0:
            self.RapidFire.update(0)
        else:
            self.RapidFire.update(1)
        if self.SPU == True:
            self.speedmeter = self.speedmeter-np.random.binomial(np.random.rayleigh(abs(np.random.normal(1,10))),.3)
        if self.speedmeter<=0:
            self.DH.PostToServer("DashQ:"+self.DH.id)
            self.SPU = False
        if self.FTS != 0:
            self.FTS =self.FTS-1
        if self.gameCounter % 10 == 0 :
            if self.SFIRE != 0:
                self.SFIRE = self.SFIRE-1
                self.DH.PostToServer("Fire:"+self.DH.id)
            
                
        self.Update_Own_Values(self.update_array)
        events = pygame.key.get_pressed()
        if events[pygame.K_UP]:
            done = True
            if self.Bkg.collisioncheck(self.x+self.speed_multipler*math.sin(self.rot),self.y+self.speed_multipler*math.cos(self.rot)) == True:
                self.DH.PostToServer("w:"+self.DH.id)
        if events[pygame.K_DOWN]:
            done = True
            if self.Bkg.collisioncheck(self.x-self.speed_multipler*math.sin(self.rot),self.y-self.speed_multipler*math.cos(self.rot)) == True:
                self.DH.PostToServer("s:"+self.DH.id)
        if events[pygame.K_LEFT]:
            self.DH.PostToServer("a:"+self.DH.id)
            done = True
        if events[pygame.K_RIGHT]:
            self.DH.PostToServer("d:"+self.DH.id)
            done = True
        if self.speedmeter<100:
            self.speedmeter = self.speedmeter+np.random.uniform(0,2)
            
#        print(self.clock.get_fps())
        
        pygame.display.flip()
        self.clock.tick(30)
        tanks = list()
        for i in list(self.update_array.values()):
            tanks.append(i["tankid"])
        self.Renderloop()
        self.LocalTankSetup(tanks)
        self.Update_Tanks()
        self.Update_Own_Values(self.update_array)
        if self.FT.update(self.update_array[self.DH.id]['FT'],self.local_global_conversion(-1000,-650),self.active_tank_dict[self.DH.id]):
            if self.update_array[self.DH.id]['FT']==True:
                self.DH.PostToServer("Heal:"+self.DH.id)
            else:
                self.DH.PostToServer("Hit:"+self.DH.id)
        
        
        
    def LocalTankSetup(self,tanks):
        for i in tanks:
            if i not in self.active_tank_dict:
                data =self.update_array[i]
                TK = Tanks(i,data["posx"],data["posy"],data["rot"],"Assets\Tank.png",self.gameDisplay)
                self.active_tank_dict[i] = TK
                
                
            

    def Update_Tanks(self):
        try:
            self.Update_Own_Values(self.update_array)
            if self.health <= 0:
                self.DH.PostToServer("Dead:"+self.DH.id)
            
            tanks = list(self.active_tank_dict.values())
            for i in tanks:
                data = self.update_array[i.tankid]
                x,y = self.local_global_conversion(data['posx'],data['posy'])
                i.update(x,y,data['rot'],data['health'])
                self.Bkg.collisioncheck(data["posx"],data["posy"])
                for a in data['bullets']:
                    self.img = self.bullet
                    self.img = pygame.transform.scale(self.img,(10,20))
                    self.img = pygame.transform.rotate(self.img,math.degrees(a[2]))
                    
                    a[2] = a[2]
                    
                    q,w = self.local_global_conversion((a[0]-50)+50*math.sin(a[2]),(a[1]-50)+50*math.cos(a[2]))
                    bullet = Bullet(q,w,self.img,self.gameDisplay,a[4],a[6],a[5])
                    if bullet.HitCheck(self.active_tank_dict[self.DH.id]) == True:
                        self.DH.PostToServer("Hit:"+self.DH.id)
        except:
            pass
                
    def local_global_conversion(self,xi,yi):
        x = self.update_array[self.DH.id]["posx"]
        y = self.update_array[self.DH.id]["posy"]
        return ((x-xi)+self.w/2,(y-yi)+self.h/2)
    
        
            
G = Game()

