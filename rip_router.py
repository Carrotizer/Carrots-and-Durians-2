from sim.api import *
from sim.basics import *
import copy

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    INFINITY = 100
    
    DEBUG = True
    
    
    """
    IMPORTANT
    
    From Piazza
    -Please don't advertise a neighbor to himself, i.e. if A is connected to B, please don't include B in A's update to B.
    -You should send RoutingUpdates whenever your routing table changes.
    -If your router does not have a route for a particular destination -- Drop that packet!
    """
    
    def __init__(self):

        #dictionary that maps from:
        #    K: destination
        #    to
        #    V: port to send it out to
        self.forwarding_table = {}
        
        #dictionary that maps from: 
        #    K: destination 
        #    to 
        #    V: min hop path distance in forwarding table
        self.paths = {}
        
        #dictionary that maps from: 
        #    K: neighbor  
        #    to 
        #    V: a DICTIONARY of destinations reachable by that port
        self.neighbors_distances = {}
        
    def handle_rx (self, packet, port):
        # Add your code here!
        if isinstance( packet , DiscoveryPacket):
            if self.DEBUG:
                debugLinkUp = "LINK_UP" if packet.is_link_up else "LINK DOWN" 
                print "######## Received a %s DiscoveryPacket thru PORT: %i from SRC: %s #######" % (debugLinkUp, port, packet.src.name) 
            
            #link up case
            if packet.is_link_up:
                #add as a neighbor in forwarding table
                self.paths[packet.src] = 1
                self.forwarding_table[packet.src] = port
                self.neighbors_distances[packet.src] = {}
                # I wouldn't have to update any other distances.  (Right?)
                # RoutingUpdates case should take care of it for me
                
            #link down case
            else:
                del(self.neighbors_distances[packet.src])
                del(self.paths[packet.src])
                del(self.forwarding_table[packet.src])    
                # Find new min distance and proper port
                # We need to recalculate everything from what we have.  
                # This is why we need RoutingUpdates' information stored
            self.recalculateMinDist()
                            
            # Send routing update IF THE ROUTING TABLE CHANGED
            self.send_RoutingUpdates(self.neighbors_distances.keys())
            
        elif isinstance(packet, RoutingUpdate):
            #TODO: handle Split horizon with poisoned reverse
            
            tempMap = {}
            for dest in packet.all_dests():
                tempMap[dest] = packet.get_distance(dest)
            
            self.neighbors_distances[packet.src] = tempMap 
            self.recalculateMinDist()
            
            #send updates
            self.send_RoutingUpdates(self.neighbors_distances.keys())
        else:
            # FORWARD THE PACKET CORRECTLY
            
            if packet.dst in self.forwarding_table:
                self.send(packet, self.forwarding_table[packet.dst])
            else:
                if self.DEBUG:
                    print "Dropping packet from %s" % packet.src
                pass
                
            """
            # If your router does not have a route for a particular destination -- Drop that packet!
            try:
                for fwdport in sorted(self.forwarding_table[packet.dst].keys()):  #sort so that tie broken by lowest port number
                    if self.forwarding_table[packet.dst][port] == self.min_dist_table[packet.dst]:
                        self.send(packet, fwdport)
            except KeyError:
                pass
            """
    
    def recalculateMinDist(self):
        for neighbor in self.neighbors_distances.keys():
            for dest in self.neighbors_distances[neighbor].keys():
                hop_count = self.neighbors_distances[neighbor][dest]
                distFromSelf = hop_count + 1
                if not (dest in self.paths.keys()) or distFromSelf < self.paths[dest]:
                    # ^ getting a key error above means it's not updated when it should have
                    self.paths[dest] = distFromSelf
                    self.forwarding_table[dest] = self.forwarding_table[neighbor]       
                elif distFromSelf == self.paths[dest]:
                    # Break ties by lower port ID
                    current_port = self.forwarding_table[dest]
                    new_port = self.forwarding_table[neighbor]
                    self.forwarding_table[dest] = min(current_port, new_port)
    
    
    #iterates over the forwarding table for a particular destination and reset the minum.  
    #Deletes the entry if no entries in forwarding table
    def resetMinDist(self, dest, ignorePort = None):
        distances = []
        ports = self.forwarding_table[dest].keys()
        if len(ports) > 0:
            for port in ports:
                if port not in ignorePort:
                    distances.append(self.forwarding_table[dest][port])
            self.min_dist_table[dest] = min(distances)
        else:
            del(self.min_dist_table[dest])
    
    #similar to restMinDist except for whole table
    def resetMinDistTable(self):
        for dest in self.forwarding_table.keys():
            self.resetMinDist(dest)
    
    # Send routing updates to neighbors (a list of neighbors, NOT PORTS)
    # NOTE: Please don't advertise a neighbor to himself, 
    # i.e. if A is connected to B, please don't include B in A's update to B.
    def send_RoutingUpdates(self, neighbors):
        # Because of the above constraint, we need to make each a routing update for
        # POISON REVERSE:
        # IF BEST ROUTE TO X IS THROUGH N
        # ADVERTISE X:100 TO N
        for neighbor in neighbors:
            newRoutingUpdate = RoutingUpdate()                
            for dest in self.paths.keys():
                if dest != neighbor:
                    if self.forwarding_table[dest] == self.forwarding_table[neighbor]:   
                        newRoutingUpdate.add_destination(dest, 100)
                    else:
                        newRoutingUpdate.add_destination(dest, self.paths[dest])
        
            self.send(newRoutingUpdate, self.forwarding_table[neighbor])
            if self.DEBUG:
                print "#~#~#~#~# Sending RoutingUpdates to %s" % neighbor
                print "thru port: %s #~#~#~#~#" % self.forwarding_table[neighbor]
        
        
        
        