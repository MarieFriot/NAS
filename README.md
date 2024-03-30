# NAS
Le fichier main.py permet de configurer les routeurs du projet GNS3 MPLS-VPN-AUTO.gns3.

La configuration se fait à l'aide de telnet : On lit les paramètres de configuration des routeurs dans le json DicoRouteur2.json, puis on récupère les commandes à écrire (sans les paramètres) dans le fichier commande.json. On insére dans les commandes pour chaques cas les bons paramètres puis on les écrit sur le routeur via telnet. De plus, après avoir écrit la commmande sur le terminal du routeur, on l'écrit également dans un fichier LastConfig.json. Ce fichier garde en mémoire les suites de commandes apliquées lors des dernières configurations. Si jamais on change les paramètres de configuration des routeurs, on peut les reconfigurer sans les réinitialiser à l'aide des fichiers lastConfig. Pour cela, avant d'écrire une commande avec telnet on regarde les choses suivantes :

Si elle est modifiable : cette information est sous la forme d'un entier dans le fichier commande.json
Si elle est différente que la précédente : si c'est le cas et qu'elle est modifiable, on applique "no" sur la commande précédente avant d'entrer la nouvelle commande et de la garder en mémoire. Cela permet de modifier dynamiquement la configuration des routeurs sans les eteindrent : changer d'as, changer de voisin, changer la relation avec les voisins...

En plus de la configuration dynamique voici les opérations possibles :
  - choix des élements que l'on souhaite configurer :  bgp pour trafic vpnv4, bgp pour trafic ipv4, mpls et les interfaces (adresses ip et protocole de routage).
  - suppression des configurations gardées en mémoire dans les fichiers LastConfig : Cela est important lorsque les routeurs sont redémarés sans avoir enregistré avec write les configurations précédentes.

    
Concernant le réseau voici son architecture :

1 AS principale (AS 111), contenant des PE et des P, reliées à 3 clients vpn et 2 clients internet.

Dans l'AS principale sont configurés Ospf, mpls et bgp vpn4  ainsi que des vrfs sur les interface des clients vpn pour permettre de faire passser du trafic vpn. BGPv4 est également configuré pour permettre de faire passer du trafic ipv4 sans vpn. Dans ce cas précis, les interfaces des routeurs de bordure en OSPF connectées aux clients ip sont en mode passive interface pour que les routeurs de l'AS connaissent le next hop en n'évitant de mélanger les deux as.

Le client vpn 3 peut communiquer avec les routeurs de son réseau mais aussi avec les clients 1 et 2. Les clients 1 et 2 peuvent communiquer avec les routeurs de leur réseau et donc aussi avec le client 3. En revanche, les clients 1 et 2 sont isolés même si leurs adresses ip se chevauchent car leurs routes sont distinguées pas un route target au niveau de leur vrf.
