from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        # Add your code here!
        
        self.distance_table = {}
        
        self.neighbors = []
        self.neighbor_to_routingUpdates = {}
        # Every time a RoutingUpdate is received, update neighbor_to_routingUpdates
        # I think every time we get a new RoutingUpdates, we need to check:
        # -Implicit withdrawals
        # -Poison reverse
        # in some ways.
        pass

    def handle_rx (self, packet, port):
        # Add your code here!
        if isinstance( packet , DiscoveryPacket):
            # HANDLE DISCOVERY
            packetData = packet.__repr__()
            #<%s from %s->%s is restOfData
            restOfData = packetData.split(", ")[0]
            packet_src = restOfData.split("->")[0].split(" from ")[1]
            #packet_dst = restOfData.split("->")[1]
            is_link_up = packetData.split(", ")[1][:-1]
            
            self.distance_table.append((packet_src, 1))
            self.send_RoutingUpdates()
            
        elif isinstance(packet, RoutingUpdate):
            # HANDLE ROUTING UPDATE
            if packet.src == None:
                print ""
            self.neighbor_to_routingUpdates[packet.src]
            
            # SEND RoutingUpdates to NEIGHBORS
            # Steps:
            # 1. Need to figure out what paths we can take to all destinations
            
            
            # 2. Send those values in RoutingUpdate class to all neighbors
            self.send_RoutingUpdates()    
        else:
            # FORWARD THE PACKET CORRECTLY
            
            # FROM PIAZZA: If your router does not have a route for a particular destination -- Drop that packet!
            #self.send(packet, SOURCE, )
            
        
            raise NotImplementedError

    def send_RoutingUpdates(self):
        newRoutingUpdate = RoutingUpdate(PACKET)
        for(dest, distance in SOME MAPPING):
            newRoutingUpdate.add_destination(dest, distance)
            
        
        
        raise NotImplementedError