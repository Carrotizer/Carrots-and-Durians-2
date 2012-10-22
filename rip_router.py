from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):

        #dictionary that maps from:
        #    K: destination
        #    V: another dictionary that maps from:
        #           K: neighboring port
        #           V: that neighbor's distance to the port
        self.forwarding_table = {}
        
        #dictionary that maps from: 
        #    K: destination to 
        #    V: min hop path distance in forwarding table
        self.min_dist_table = {}
        
        
        #dictionary that maps from: 
        #    K: neighbor port to 
        #    V: a set of destinations reachable by that port
        self.neighbor_paths = {}

        #TODO:
        # -poisoined reverse
        #should router info be erased when it goes down and comes back up?
        #right now it does, not sure if that is correct
        
    def handle_rx (self, packet, port):
        # Add your code here!
        if isinstance( packet , DiscoveryPacket):
            
            #link up case
            if packet.is_link_up:
                #add as a neighbor in forwarding table
                try:
                    self.forwarding_table[packet.src][port] = 1
                except KeyError:
                    self.forwarding_table[packet.src] = {}
                    self.forwarding_table[packet.src][port] = 1
                    
                # add to min distance table and neighbor paths dictionary    
                self.min_dist_table[packet.src] = 1
                self.neighbor_paths[port]  = set([])
            
            #link down case
            else:
                for dest in self.forwarding_table.keys():
                    try:
                        del(self.forwarding_table[dest][port])
                        self.resetMinDist(dest)
                    except KeyError:
                        pass
                try:
                    del(self.neighbor_paths[port])
                except:
                    pass
            
            
            #Send routing updates.
            #ERROR:Test fails with this line enabled
            #self.send_RoutingUpdates()
            
        elif isinstance(packet, RoutingUpdate):
            #TODO: handle Split horizon with poisoned reverse
            
            dests = packet.all_dests();
            for dest in dests:
                #add destination to set of dests reachable by that port
                self.neighbor_paths[port].add(dest)
                dist = packet.get_distance(dest)
                #update forwarding table
                try:
                    self.forwarding_table[dest][port] = dist+1
                except KeyError:
                    self.forwarding_table[dest] = {}
                    self.forwarding_table[dest][port] = dist+1
                
                #update min dist table
                self.resetMinDist(dest)
            
            
            #implicit withdrawl:
            for dest in self.neighbor_paths[port]:
                #if the destination isn't in the lastest update
                if not dest in dests:
                    #remove it from everything
                    self.neighbor_paths[port].remove(dest)
                    dist = self.forwarding_table[dest][port]
                    del(self.forwarding_table[dest][port])
                    
                    #reset our minimum table in case we lost the cheapest path
                    if(dist == self.min_dist_table[dest]): 
                        self.resetMinDist(dest)
                     
            #send updates
            self.send_RoutingUpdates()    
        else:
            # FORWARD THE PACKET CORRECTLY
            
            # If your router does not have a route for a particular destination -- Drop that packet!
            try:
                for fwdport in sorted(self.forwarding_table[packet.dst].keys()):  #sort so that tie broken by lowest port number
                    if self.forwarding_table[packet.dst][port] == self.min_dist_table[packet.dst]:
                        self.send(packet, fwdport)
            except KeyError:
                pass
    
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
    
    def send_RoutingUpdates(self):
        newRoutingUpdate = RoutingUpdate()
        for dest in self.min_dist_table.keys():
            newRoutingUpdate.add_destination(dest, self.min_dist_table[dest])
        self.send(newRoutingUpdate, self.neighbor_paths.keys())