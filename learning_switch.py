from sim.api import *
from sim.basics import *

'''
Create your learning switch in this file.
'''
class LearningSwitch(Entity):
    def __init__(self):
        # Add your code here!
        self.dst_to_port_map = {}
        # if we see a packet with new src, then add it to the map.

    def handle_rx (self, packet, port):
        # Add your code here!
        self.dst_to_port_map[packet.src] = port
        if (packet.dst in self.dst_to_port_map.keys()):
            self.send(packet, self.dst_to_port_map[packet.dst])
        else:
            # Flood all ports, EXCEPT the one that the packet arrived from
            self.send(packet, port , True)
            
