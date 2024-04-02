# NAS
Le fichier main.py permet de configurer les routeurs du projet GNS3 MPLS-VPN-AUTO.gns3.

La configuration se fait à l'aide de telnet : On lit les paramètres de configuration des routeurs dans le JSON DicoRouteur2.json, puis on récupère les commandes à écrire (sans les paramètres) dans le fichier commande.json. On insère dans les commandes pour chaque cas les bons paramètres puis on les écrit sur le routeur via telnet. De plus, après avoir écrit la commande sur le terminal du routeur, on l'écrit également dans un fichier LastConfig.json. Ce fichier garde en mémoire les suites de commandes appliquées lors des dernières configurations. Si jamais on change les paramètres de configuration des routeurs, on peut les reconfigurer sans les réinitialiser à l'aide des fichiers lastConfig. Pour cela, avant d'écrire une commande avec telnet, on regarde les choses suivantes :

Si elle est modifiable : cette information est sous la forme d'un entier dans le fichier commande.json. Si elle est différente de la précédente : si c'est le cas et qu'elle est modifiable, on applique "no" sur la commande précédente avant d'entrer la nouvelle commande et de la garder en mémoire. Cela permet de modifier dynamiquement la configuration des routeurs sans les éteindre : changer d'AS, changer de voisin, changer la relation avec les voisins...

En plus de la configuration dynamique, voici les opérations possibles :

Choix des éléments que l'on souhaite configurer : BGP pour trafic VPNv4, BGP pour trafic IPv4, MPLS et les interfaces (adresses IP et protocole de routage).
Suppression des configurations gardées en mémoire dans les fichiers LastConfig : cela est important lorsque les routeurs sont redémarrés sans avoir enregistré avec write les configurations précédentes.
Concernant le réseau, voici son architecture :

1 AS principale (AS 111), contenant des PE et des P, reliées à 3 clients VPN et 2 clients Internet.
Dans l'AS principale sont configurés OSPF, MPLS et BGP VPNv4 ainsi que des VRF sur les interfaces des clients VPN pour permettre de faire passer du trafic VPN. BGPv4 est également configuré pour permettre de faire passer du trafic IPv4 sans VPN. Dans ce cas précis, les interfaces des routeurs de bordure en OSPF connectées aux clients IP sont en mode passive interface pour que les routeurs de l'AS connaissent le next hop en évitant de mélanger les deux AS.

Le client VPN 3 peut communiquer avec les routeurs de son réseau mais aussi avec les clients 1 et 2. Les clients 1 et 2 peuvent communiquer avec les routeurs de leur réseau et donc aussi avec le client 3. En revanche, les clients 1 et 2 sont isolés même si leurs adresses IP se chevauchent car leurs routes sont distinguées par un route target au niveau de leur VRF
