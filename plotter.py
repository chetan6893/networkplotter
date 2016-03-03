from jsonrpclib import Server
import networkx as nx#
from bz2 import __author__
#
__author__="Chetan Ramachandra"
# List of hostnames. This can be read from a mongodb database in a scaled setup
hostnames= {"10.85.128.101":"mt701","10.85.128.102":"mt702","10.85.128.103":"mt703","10.85.128.104":"mt704","10.85.128.105":"mt705","10.85.128.106":"mt706","10.85.128.107":"mt707","10.85.128.108":"mt708","10.85.128.109":"mt709","10.85.128.110":"mt710"}
#obtain only the list of IP addresses of the switches
switches=hostnames.keys()
username = "admin"
password = "deeban"
#
G=nx.MultiGraph()
#get list of neighbours from a Arista Switch
def getlldpinfo(switch_ip):
    urlString = "https://{}:{}@{}/command-api".format(username, password, switch_ip) 
    switchReq = Server( urlString ) 
    response = switchReq.runCmds( 1, ["show lldp neighbors"] ) 
    neighbors=response[0]["lldpNeighbors"]
    return neighbors

#get the operating speed of a interface from a Arista switch
def getspeed(interface_name,switch_ip):
    urlString = "https://{}:{}@{}/command-api".format(username, password, switch_ip) 
    switchReq = Server( urlString ) 
    response = switchReq.runCmds( 1, ["show interfaces status"] ) 
    speed=response[0]["interfaceStatuses"][interface_name]["bandwidth"]
    return (speed/1000000000)

#add the switch as nodes of a graph and the links as edges of a graph
for switch in switches:
    print "Obtaining lldp info for %s" %(switch)
    lldpinfo=getlldpinfo(switch)
    for neighbor in lldpinfo:
        print "Scanning details for neighbor %s" %(neighbor["neighborDevice"])
        #localport, remoteport and the speed of the port are added as attributes of the edges of the graph
        localport=neighbor["port"]
        remoteport=neighbor["neighborPort"]
        speedint=getspeed(localport,switch)
        #key is added to prevent duplicate of edges
        check_key=neighbor["neighborDevice"]+"_"+hostnames[switch]+".blr.aristanetworks.com"+"_"+remoteport+localport
        print "check_key is "+check_key
        #If the key is already present, skip adding the edge, else add them
        if G.has_edge(neighbor["neighborDevice"],hostnames[switch]+".blr.aristanetworks.com",key=check_key)==False:
            add_key=check_key=hostnames[switch]+".blr.aristanetworks.com"+"_"+neighbor["neighborDevice"]+"_"+localport+remoteport
            print "\tAdding edge %s <-----------------------> %s with key %s\n" %(localport,remoteport,add_key)
            G.add_edge(hostnames[switch]+".blr.aristanetworks.com",neighbor["neighborDevice"],port=localport,neighborPort=remoteport,speed=speedint,key=add_key)
        
print G.edges()
#generate a graphml file that can be opened using cytoscape/yED
nx.write_graphml(G,'network.graphml')

