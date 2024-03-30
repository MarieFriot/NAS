#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 14:43:41 2024

@author: mfriot
"""
import time
import telnetlib
from gns3fy import Gns3Connector, Project,Node
import json
import libgns3


def portRouteur(nameRouteur, projectName, projectID):
    """
    Parameters
    ----------
    nameRouteur : String : numéro du routeur
    projectName : String : nom du projet GNS3
    projectID : : String : identifiant du projet GNS3

    Returns
    -------
    routeur.console_host : nom du routeur sur le projet GNS3
    routeur.console : numéro de port dur routeur sur GNS3
    Ces paramètres permettent de se connecter à chaques routeur via telnet
    """
    server = Gns3Connector("http://localhost:3080")
    lab = Project(name=projectName, connector=server)
    lab.get()
    print(projectID)
    routeur = Node(project_id=projectID, name= nameRouteur, connector=server)
    routeur.get()
    return routeur.console_host, routeur.console
    

def configRouteur(routeur,data,cible):
    """
    Parameters
    ----------
    routeur : String : Numéro du routeur.
    data : Dictionnaire : Contient les paramètres de configuration de chaques routeurs
    cible : String : Indique quel élement on configure (interface, bgp, interface, bgpipv4, all)
    -------
    Fonction permettant de configurer un routeur via telnet.
    """
    conf = data[routeur] # dictionaire contenant la configuration du routeur 
    name = int(routeur)
    nameRouteur ="R"
    nameRouteur += str(name)
    #Récupération du nom et du numéro de port du routeur
    projectID = data["1"]["projectId"]
    projectName =  data["1"]["projectName"]
    nom, port = portRouteur(nameRouteur,projectName, projectID)
    
    #Lecture des commandes de configuration des routeurs 
    with open("commande.json", 'r') as fcommande :
        commande = json.load(fcommande) #dictionaire contenant les commandes de configuration
   
    try:
        with telnetlib.Telnet(nom, port , timeout=30) as tn: 
            print(f"connexion établie avec R{name} ")
            tn.write(b"\r")
            tn.read_until(b"#")
            tn.write(b"configure terminal\r")
            tn.read_until(b"#")
            tn.write(b"no logging console\r")
            tn.read_until(b"#")
            tn.write(b"end\r")
            tn.read_until(b"#")
            
           
                
            if cible =="interface":
                #### Configuratioon des interfaces ###
                libgns3.interfaceConfig(name, conf, commande,tn)
                time.sleep(1)
                
            elif cible == "ldp" :
                time.sleep(1)
                libgns3.labelProtocolConfig(name, conf, commande,tn)
                time.sleep(1)
                
            elif cible == "bgp" :
                libgns3.bgpConfig (name, conf, commande,tn)
                time.sleep(1)
            
            elif cible == "bgipv4":
                libgns3.ipv4BgpConfig(name, conf, commande,tn)
                time.sleep(1)
                
                
            else :
                time.sleep(1)
                libgns3.interfaceConfig(name, conf, commande,tn)
                time.sleep(1)
                libgns3.labelProtocolConfig(name, conf, commande,tn)
                time.sleep(1)
                libgns3.bgpConfig (name, conf, commande,tn)
                time.sleep(1)
                libgns3.ipv4BgpConfig(name, conf, commande,tn)
                
                
                
              
                    
    except ConnectionRefusedError:
        print(f"La connexion à R{name} a été refusée.")
    except Exception as e:
        print(f"Erreur de connexion a R{name}: {e}")
    

        
        
        
def clearLastConfig() :
       """
        Fonction permettant de vider les fichiers contenant la dernière config
        de chaques routeurs.
       """
       with open("DicoRouteur2.json", 'r') as fichier:
           data = json.load(fichier)
       for routeur in data.keys() :
           with open(f"lastConfig/lastConfig{routeur}.json","w") as fichier:
               lastConfig = {}
               json.dump(lastConfig, fichier)

def main():
    with open("DicoRouteur2.json", 'r') as fichier:
        data = json.load(fichier)

    routeur = input("Quel est le numéro du routeur que vous voulez configurer. Si vous voulez tout configurer : all ?")
    while routeur not in data.keys() and routeur !="all" :
        routeur = input("Quel est le numéro du routeur que vous voulez configurer. Si vous voulez tout configurer : all ?")

   
    cible =input("Quelle est votre cible : internalRouting, interface, bgp, all\n")
   
    if routeur == "all" :
            for routeur in data.keys() :
                configRouteur(routeur,data,cible)
    else : 
            configRouteur(routeur,data,cible)
   
     
if __name__ == "__main__" :
    answer = input("Voulez vous effacer les fichiers contenant la dernière config [oui/non] ?")
    if answer == "oui" :
        clearLastConfig()
    main()
    
    
    
