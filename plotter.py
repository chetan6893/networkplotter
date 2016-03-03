from jsonrpclib import Server
import networkx as nx#
from bz2 import __author__
#
__author__="Chetan Ramachandra"
hostnames= {"10.85.128.101":"mt701","10.85.128.102":"mt702","10.85.128.103":"mt703","10.85.128.104":"mt704","10.85.128.105":"mt705","10.85.128.106":"mt706","10.85.128.107":"mt707","10.85.128.108":"mt708","10.85.128.109":"mt709","10.85.128.110":"mt710"}
#hostnames= {"10.85.128.101":"mt701","10.85.128.102":"mt702"}
switches=hostnames.keys()
username = "admin"
password = "deeban"
#
G=nx.MultiGraph()
#
def getlldpinfo(switch_ip):
    urlString = "https://{}:{}@{}/command-api".format(username, password, switch_ip) 
    switchReq = Server( urlString ) 
    response = switchReq.runCmds( 1, ["show lldp neighbors"] ) 
    neighbors=response[0]["lldpNeighbors"]
    return neighbors

def getspeed(interface_name,switch_ip):
    urlString = "https://{}:{}@{}/command-api".format(username, password, switch_ip) 
    switchReq = Server( urlString ) 
    response = switchReq.runCmds( 1, ["show interfaces status"] ) 
    speed=response[0]["interfaceStatuses"][interface_name]["bandwidth"]
    return (speed/1000000000)

for switch in switches:
    print "Obtaining lldp info for %s" %(switch)
    lldpinfo=getlldpinfo(switch)
    for neighbor in lldpinfo:
        print "Scanning details for neighbor %s" %(neighbor["neighborDevice"])
        localport=neighbor["port"]
        remoteport=neighbor["neighborPort"]
        speedint=getspeed(localport,switch)
        check_key=neighbor["neighborDevice"]+"_"+hostnames[switch]+".blr.aristanetworks.com"+"_"+remoteport+localport
        print "check_key is "+check_key
        if G.has_edge(neighbor["neighborDevice"],hostnames[switch]+".blr.aristanetworks.com",key=check_key)==False:
            add_key=check_key=hostnames[switch]+".blr.aristanetworks.com"+"_"+neighbor["neighborDevice"]+"_"+localport+remoteport
            print "\tAdding edge %s <-----------------------> %s with key %s\n" %(localport,remoteport,add_key)
            G.add_edge(hostnames[switch]+".blr.aristanetworks.com",neighbor["neighborDevice"],port=localport,neighborPort=remoteport,speed=speedint,key=add_key)
        
print G.edges()
nx.write_graphml(G,'network.graphml')

