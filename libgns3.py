import time
import json





def ip_address(name,neighbor):
    """
    Parameters
    ----------
    name : Int : numéro de routeur
    neighbor : Int : numéro du routeur voisin
    Returns
    -------
    res : int :valeur correspondant au sous-réseau entre les deux routeurs
    Cette valeur est utilisée pur configurer leurs adresses ip.
    """
    if neighbor == "EXIT" :
        res = 1
    elif name < neighbor :
        res = name*10 + neighbor
    else :
        res = neighbor*10 + name
    return res 

def setNeighborVal(neighborType) :
    """
    Parameters
    ----------
    neighborType : Chaine de caractère (peer, provider ou customer)
    Returns
    -------
    res : Entier
        Retourne un entier en fonction du type de relation avec l'AS voisine.
        Cette entier est utilisé pour attribuer la localPref ainsi que les numéros
        de communauté.
    """
    if  neighborType == "customer" :
         res = 500
    elif  neighborType == "peer":
         res = 300
    elif  neighborType == "provider":
         res = 100
    else :
         res = 0
    return res

def write(lastConfig, key, com, lvl, indice, tn) :
    """
    Parameters
    ----------
    lastConfig : Dictionnaire contenant la dernière configuration du routeur
    key : Clef du dictionnaire lastConfig.
    com : String : Commande que l'on veut rentrer.
    lvl : Si lvl == 0, la commande est modifiable, si non, on ne peut pas la
        modifier (ex: configure terminal)
    indice : Int : Correspond à l'indice de la liste contenant la suite des
        anciennes commandes.
    tn : telnet
    -------
    Fonction vérifiant si la nouvelle commande est différente de la précédente.
    Si la commande est différente : on applique "no" devant l'ancienne et on 
    l'écrit sur le routeur pour la supprimer.
    Après avoir écrit la nouvelle commande sur le routeur, on la garde en mémoire
    dans le dictionnaire de LastConfig.
    """
    
    if lvl == 0 : #si la commande est changeable
        if key in lastConfig.keys() :
            if indice <= len(lastConfig[key])-1: #important pour la premiere config
                lastCom = lastConfig[key][indice]
                if com != lastCom: #Si la commande est différente de la précédente
                    if lastCom[0] == "n" and lastCom[1] == "o":
                        noCom = lastCom[2:]
                    else :
                        noCom = "no " + lastCom
                    #print(noCom)

                    tn.write(noCom.encode('utf-8')) #On enleve la commande précédente
                    tn.read_until(b"#")  
    print(com)
    tn.write(com.encode('utf-8')) #On écrit la nouvelle commande 
    tn.read_until(b"#")
    
    #On ajoute la nouvelle commande dans le fichier qui garde en mémoire les commandes entrées 
    if key not in lastConfig.keys() :
        lastConfig[key] = [com] 
    elif len(lastConfig[key]) -1 < indice : #important si l'indice dépasse la taille de la liste
        lastConfig[key].append(com) 
    else :
        lastConfig[key][indice] = com 
  
  




def interfaceConfig(name, conf, commande,tn):
    """
    Parameters
    ----------
    name: Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure chaques interface des routeurs.
    """
    compteurRd = name*10 
        
 
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
   
    AS = conf['as']
    neighbors = conf['neighbors']
    
    
    for interface, neighbor in neighbors.items() :
        if interface == "loopback" :
            masque = "255.255.255.255"
        
        else :
            masque = "255.255.255.252"
            
            
      
        if neighbor[0] != "NULL" :
            ip_val = ip_address(name, neighbor[0])
    
            ######Configuration des vrfs#################
           
            if neighbor[1] != AS and neighbor[2] != "passive" :
                numClient = neighbor[2]
                for i in range(len(commande['vrf']['config'])):
                    comDico = commande['vrf']['config'][i]
                    for com, lvl in comDico.items():
                        com= com.format(numClient = numClient, compteur = compteurRd, AS = AS, asClient = neighbor[1])
                        compteurRd = compteurRd +1
                        if 'vrf' not in lastConfig.keys():
                            lastConfig['vrf'] = {}
                        write(lastConfig['vrf'], numClient ,com, lvl, i, tn)
                        
                importRT = conf['import']
                if len(importRT) > 0:
                    for infoClient in importRT :
                        for j in range(len(commande['vrf']['importRT'])):
                            if infoClient[0] == numClient : #on vérifie qu'on est sur la bonne vrf
                                i = i+1
                                comDico = commande['vrf']['importRT'][j]
                                for com, lvl in comDico.items():
                                    com= com.format(numClient = infoClient[1] , asClient = infoClient[2])
                                    write(lastConfig['vrf'], numClient ,com, lvl, i, tn)
                     
                #Si la nouvelle suite de commande est plus petite que la précédente
                if i < len(lastConfig['vrf'][numClient])  :
                     for j in range(i +1, len(lastConfig['vrf'][numClient])):
                         del lastConfig['vrf'][numClient][i+1] 
                
                
                
            ##### Configuration des interfaces ###########

            ## Ecriture de commande obligatoire pour accéder aux interfaces
            for i in range(len(commande['interface'][interface])):
                if neighbor[1] != AS and i == 0  and neighbor[2] != "passive":
                    pass
                else :
                    comDico = commande['interface'][interface][i]
                    for com, _ in comDico.items():
                        tn.write(com.encode('utf-8'))
                        tn.read_until(b"#")
            
            numClient = 0
            if conf['routerType'] == "CE"  or conf['routerType'] == "CEIP":
                interfaceType = "noIGP"
            elif neighbor[1] == AS :
                interfaceType =  conf['routing_protocol']
            elif neighbor[2] == "passive" :
                interfaceType = "passive"
            else :
                interfaceType = "vrf"
                numClient = neighbor[2]
         
            for i in range(len(commande['interface'][interfaceType])):
                comDico = commande['interface'][interfaceType][i]
                for com, lvl in comDico.items():
                    com= com.format(name= name%2 +1,numClient = numClient, ip_val = ip_val, AS = neighbor[1], masque = masque, interface = interface)
                    if 'interface' not in lastConfig.keys():
                        lastConfig['interface'] = {}
                    write(lastConfig['interface'], interface ,com, lvl, i, tn)
            
            tn.write(b"end\r") 
            tn.read_until(b"#")
            #Si la nouvelle suite de commande est plus petite que la précédente
            if i < len(lastConfig['interface'][interface])  :
                for j in range(i+1, len(lastConfig['interface'][interface])):
                    del lastConfig['interface'][interface][i+1]
         
            
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
   


                    
def labelProtocolConfig(name, conf, commande,tn):
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure ldp sur lles interfaces des PE et des P qui sont dans le coeur du réseau.
    """

    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    if conf['routerType'] != "CE" and conf['routerType'] != "CEIP":
        ######LDP SUR ROUTEUR##################
        for i in range(len(commande['labelProtocol']['ldp'])):
                comDico = commande['labelProtocol']['ldp'][i]
                for com, lvl in comDico.items():
                    if 'labelProtocol' not in lastConfig.keys():
                        lastConfig['labelProtocol'] = {}
                    write(lastConfig['labelProtocol'], 'router' ,com, lvl, i, tn)
                    
        tn.write(b"end\r") 
        tn.read_until(b"#")
        
        #Si la nouvelle suite de commande est plus petite que la précédente
        if i < len(lastConfig['labelProtocol']['router'])  :
            for j in range(i+1, len(lastConfig['labelProtocol']['router'])):
                del lastConfig['labelProtocol']['router'][i+1] 
        
        time.sleep(1)
        ##############LDP SUR INTERFACE##################
        
        neighbors = conf['neighbors']
        AS = conf['as']
        for interface, neighbor in neighbors.items() :
            if interface != "loopback" and neighbor[1] == AS :  #pas sur loopback ni sur interface non dans coeur
                if neighbor[0] != "NULL"  : 
                    ## Ecriture de commande obligatoire pour accéder aux interfaces
                    for i in range(len(commande['interface'][interface])):
                        comDico = commande['interface'][interface][i]
                        for com, _ in comDico.items():
                            tn.write(com.encode('utf-8'))
                            tn.read_until(b"#")
                
                    for i in range(len(commande['labelProtocol']['ldpInterface'])):
                            comDico = commande['labelProtocol']['ldpInterface'][i]
                            
                            for com, lvl in comDico.items():
                                if 'labelProtocol' not in lastConfig.keys():
                                    lastConfig['labelProtocol'] = {}
                                write(lastConfig['labelProtocol'], interface ,com, lvl, i, tn)
                                
                    tn.write(b"end\r") 
                    tn.read_until(b"#")
                  
                    
                    #Si la nouvelle suite de commande est plus petite que la précédente
                    if i < len(lastConfig['labelProtocol'][interface])  :
                      
                        for j in range(i+1, len(lastConfig['labelProtocol'][interface])):
                            del lastConfig['labelProtocol'][interface][i+1] 
    
                 
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
    
     

def bgpConfig (name, conf, commande,tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure bgp sur les routeurs (pour du trafic vpnv4).
    """
    
   
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    AS = conf['as']
    routerType = conf['routerType']
    
    
    
    indice = 0
    
    #ecriture des commandes obligatoires pour BGP
    for i in range(len(commande['bgp']['config'])):
        comDico = commande['bgp']['config'][i]
        for com, lvl in comDico.items():
            com = com.format(name=name, AS = AS)
            write(lastConfig, 'bgp',com, lvl, indice, tn)
        indice +=1
          
    if routerType != "CEIP" :
   
        if routerType == "PE" :
            PErouter = conf['PErouter']
            for router in PErouter :
                ip_val = ip_address(router, router)
                #configuration des sessions iBGP
                for i in range(len(commande['bgp']['internalSession'])) :
                    comDico = commande['bgp']['internalSession'][i]
                    for com, lvl in comDico.items():
                        com= com.format(namePe=router%2 +1, AS = AS, ip_val = ip_val)
                        write(lastConfig, 'bgp',com, lvl, indice, tn)
                    indice +=1
                time.sleep(1)
                
            #configuration des sessions eBGP
            CErouter = conf['CErouter']
            for router in CErouter :
                ip_val = ip_address(router[0], name)
                for i in range(len(commande['bgp']['externalSessionPE'])) :
                    comDico = commande['bgp']['externalSessionPE'][i]
                    for com, lvl in comDico.items():
                        com= com.format(name=router[0]%2 +1, ASNeighbor = router[1] , ip_val = ip_val, numClient = router[2])
                        write(lastConfig, 'bgp',com, lvl, indice, tn)
                    indice +=1
            time.sleep(1)
                
                
        ##Configuration des sessions bgp sur les CE
        if routerType == "CE" :
            PErouter = conf['PErouter']
            for router in PErouter :
                ip_val = ip_address(router[0], name)
                for i in range(len(commande['bgp']['externalSessionCE'])) :
                    comDico = commande['bgp']['externalSessionCE'][i]
                    for com, lvl in comDico.items():
                        com= com.format(name=router[0]%2 +1, AS= AS, ASNeighbor= router[1] , ip_val = ip_val)
                        write(lastConfig, 'bgp',com, lvl, indice, tn)
                    indice +=1
                    
            for subnet in conf['advertise'] :
                for i in range(len(commande['bgp']['advertiseCE'])) :
                    comDico = commande['bgp']['advertiseCE'][i]
                    for com, lvl in comDico.items():
                        com= com.format(subnet = subnet, AS = AS)
                        write(lastConfig, 'bgp',com, lvl, indice, tn)
                    indice +=1
            
            time.sleep(1)
 
                
    tn.write(b"end\r") 
    tn.read_until(b"#")
    #Si la nouvelle suite de commande est plus petite que la précédente
    if indice < len(lastConfig['bgp'])  :
        for j in range(indice+1, len(lastConfig['bgp'])):
            del lastConfig['bgp'][indice+1]   
            
    
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
    
def ipv4BgpConfig(name, conf, commande,tn) :
    """
    Parameters
    ----------
    name : Chaine de caractère : nom du routeur 
    conf : Dictionnaire contenant la configuration de chaques routeur du réseau.
    commande : Dictionnaire contenant les commandes de configuration d'un routeur cisco.
    tn : telnetlib.Telnet
    Returns
    -------
    Configure bgp sur les routeurs pour du trafic ipv4.
    """
    with open(f"lastConfig/lastConfig{name}.json","r") as f:
        lastConfig = json.load(f)
        
    AS = conf['as']
    routerType = conf['routerType']
    
    indice = 0
    
    #ecriture des commandes obligatoires pour BGP
    for i in range(len(commande['bgp']['config'])):
        comDico = commande['bgp']['config'][i]
        for com, lvl in comDico.items():
            com = com.format(name=name, AS = AS)
            write(lastConfig, 'bgpv4',com, lvl, indice, tn)
        indice +=1
   
    
    print("ixiiii")
    if routerType != "CE":
        
        ASrouter = conf['ASrouter']
        #Configuragion des sessions iBGP (ipv4) en full-mesh
        if len(ASrouter) > 0 :
            for router in ASrouter :
                ip_val = ip_address(router, router)
                #configuration des sessions iBGP
                for i in range(len(commande['bgp']['internalSessionIP'])) :
                    comDico = commande['bgp']['internalSessionIP'][i]
                    for com, lvl in comDico.items():
                        com= com.format(nameR=router%2 +1, AS = AS, ip_val = ip_val)
                        write(lastConfig, 'bgpv4',com, lvl, indice, tn)
                    indice +=1
                time.sleep(1)
            
        #configuration des sessions eBGP
        if routerType != "P" :
            eBGPRouter = conf['eBGPRouter']
            if len(eBGPRouter)> 0 :
                for router in eBGPRouter :
                    ip_val = ip_address(router[0], name)
                    for i in range(len(commande['bgp']['externalSessionIP'])) :
                        comDico = commande['bgp']['externalSessionIP'][i]
                        if AS == 111 :
                            ASvalue = router[1] 
                        else :
                            ASvalue = AS
                            
                        for com, lvl in comDico.items():
                            com= com.format(name=router[0]%2 +1, ASNeighbor =router[1] , ip_val = ip_val, AS = ASvalue)
                            
                            write(lastConfig, 'bgpv4',com, lvl, indice, tn)
                        indice +=1
                time.sleep(1)
                
        #advertise des CEIP
        if routerType == "CEIP" :
            for subnet in conf['advertise'] :
                for i in range(len(commande['bgp']['advertiseCE'])) :
                    comDico = commande['bgp']['advertiseCE'][i]
                    for com, lvl in comDico.items():
                        com= com.format(subnet = subnet, AS = AS)
                        write(lastConfig, 'bgpv4',com, lvl, indice, tn)
                    indice +=1
        
                
                
    tn.write(b"end\r") 
    tn.read_until(b"#")
    #Si la nouvelle suite de commande est plus petite que la précédente
    if indice < len(lastConfig['bgpv4'])  :
        for j in range(indice+1, len(lastConfig['bgpv4'])):
            del lastConfig['bgpv4'][indice+1]   
            
    
    with open(f"lastConfig/lastConfig{name}.json","w") as f:
        json.dump(lastConfig, f)
    