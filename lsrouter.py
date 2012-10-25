from sim.api import *
from sim.basics import *
import copy
import Queue

'''
Create your RIP router in this file.
'''
class LSRouter (Entity):
    INFINITY = 100
    
    
    
    def __init__(self):
        self.forwardingTable = {}
        self.neighbors = {} #portmapping of neighbors
        self.nodes = {}
        
    def handle_rx (self, packet, port):
        
        if isinstance( packet , DiscoveryPacket):
            if packet.is_link_up:
                n = Node(packet.src)
                self.nodes[packet.src] = n
                self.neighbors[packet.src] = port
            else:
                del(self.nodes[packet.src])
                del(self.neighbors[packet.src])
            
            self.sendLSRoutingUpdates(self, self.neighbors.keys())
        elif isinstance(packet, LSRoutingUpdate):
            self.resetNodeConnections(packet.getSender())
            self.addNeighbors(packet.src, packet.getNeighbors())
            self.calculateBestPaths()
            
            self.sendLSRoutingUpdates(packet.getSender(), packet.getNeighbors())
        elif packet.dst in self.forwarding_table:
                self.send(packet, self.forwarding_table[packet.dst])
    
    
    def sendLSRoutingUpdates(self, entity, neighbors):
        update = LSRoutingUpdate()
        update.setSender(entity)
        update.setNeighbors(neighbors)
        self.send(update, None, True)
        
    def resetNodeConnections(self, loc):
        try:
            n = self.nodes[loc]
            for neighbor in n.getNeighbors():
                self.nodes[neighbor].removeNeighbor(loc)
                n.removeNeighbor(neighbor)
        except KeyError:
            pass
    
    def addNeighbors(self, loc, neighbors):
        if not loc in self.nodes.keys():
            n = Node(loc)
            self.nodes[loc] = n
        else:
            n = self.nodes[loc]
        for neighbor in neighbors:
            if not neighbor in self.nodes.keys():
                node = Node(neighbor)
                self.nodes[neighbor] = node
            else:
                node = self.nodes[neighbor]
            node.addNeighbor(loc)
            n.addNeighbor(neighbor)
    
    def calculateBestPaths(self):
        for dest in self.nodes.keys():
            outport = self.calculateBestPath(dest)
            self.forwardingTable[dest] = outport
        
    
    def calculateBestPath(self, dest):
        min = self.INFINITY
        outport = 0
        for neighbor in self.neighbors.keys():
            dist = self.calcHelp(dest, neighbor)
            if dist == min:
                outport = min(self.neighbors[neighbor], outport)
            elif dist < min:
                outport = self.neighbors[neighbor]
                min = dist
        
    def calcHelp(self, dest, start):
        visitedNodes = set([])
        visitedNodes.add(start)
        queue = bfsStack()
        queue.push((self.nodes[start], 1))
        minCount = self.INFINITY
        while(not queue.isEmpty()):
            loc, count = queue.get()
            if(loc == dest):
                if count < minCount:
                    minCount = count
            else:
                visitedNodes.add(loc)
                for neighbor in self.nodes[loc].getNeighbors():
                    if not neighbor in visitedNodes:
                        queue.push((neighbor, count+1))
        return minCount


class bfsStack():        
    def __init__(self):
        self.q = Queue.Queue()
        
    def push(self, node, cost):
        self.q._put((node, cost))
        
    def get(self):
        return self.q._get()

    def isEmpty(self):
        return self.q.empty()


class LSRoutingUpdate (Packet): 
    def __init__(self):
        Packet.__init__(self)
        self.neighbors = []
        self.sendingEntity = ""
    
    def setSender(self, entity):
        self.sendingEntity = entity
        
    def getSender(self):
        return self.sendingEntity
    
    def setNeighbors(self, neighbors):
        self.neighbors = neighbors
    
    def getNeighbors(self):
        return self.neighbors

class Node:
    def __init__(self, location):
        self.location = location
        self.neighbors = {}
    
    def getNeighbors(self):
        ns = []
        for neighbor in self.neighbors.keys():
            ns.append(neighbor)
        return ns;
    
    def addNeighbor(self, neighbor, nodes):
        try:
            self.neighbors[neighbor] = nodes[neighbor]
        except KeyError:
            self.neighbors[neighbor] = Node(neighbor)
        
    def removeNeighbor(self, neighbor):
        try:
            del(self.neighbors[neighbor])
        except KeyError:
            pass