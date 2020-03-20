# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 17:37:08 2019

@author: Pranav Devarinti
"""

import socket
import sys
import socketserver



import socketserver

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        
        
        
        
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())
        
HOST, PORT = "localhost", 10000
server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)
server.serve_forever()