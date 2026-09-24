# MIMIR — cahier des charges developpeur

Depot: [github.com/angoularaphael/space-net](https://github.com/angoularaphael/space-net)  
Nom de bord: MIMIR (aussi ecrit MYMYR a l'oral)  
Pilier: DeepTech, cas CyberSpace et OfflineSpace  
Vaisseau: Yggdrasil  
Pharmacie couplee: [EIR / medichat](https://github.com/angoularaphael/medichat)

Version: prototype console du 24 septembre 2026.  
Le depot contient le contrat, le plan, et la console MQTT `services/mimir-bus`. Le laboratoire pfSense / Suricata reste un exercice de salle, pas un binaire dans ce depot.

## 1. Role

MIMIR est le reseau de la capsule.

- Il filtre, observe et journalise le trafic interne.
- Il maintient DHCP, DNS local et MQTT quand la passerelle Terre est coupee.
- Il previent EIR si l'infirmerie est visee (alerte securite), pour que le journal medical montre la meme alerte.

MIMIR ne soigne pas, ne prescrit pas, et ne fabrique pas de medicament. Le stock, les plantes et les cuves restent dans EIR.

## 2. Hors perimetre

- Pas d'outil d'intrusion, d'exfiltration reelle, ni de charge offensive.
- Pas de copie du dossier medical. MIMIR transporte des alertes, pas les symptomes.
- Pas de decision clinique. Une alerte stock bas s'affiche; elle ne change pas une dose.
- La demonstration reseau, le jour ou elle sera codee, ne devra emettre qu'un marqueur fictif explicite, jamais des donnees reelles.

## 3. Comment MIMIR se connecte a EIR

Les deux programmes ne partagent pas leur base. Le seul lien est le bus MQTT local.

```
[Poste Windows / UI EIR] -- HTTP local --> [API EIR]
[API EIR] -- publie crise et stock bas --> [Mosquitto :1883]
[MIMIR] -- publie alerte infirmerie -----> [Mosquitto :1883]
[API EIR] -- s'abonne a l'alerte --------> journal security_alerts
```

| Qui | Topic | Sens |
|---|---|---|
| EIR | `yggdrasil/eir/alert/crisis` | publie |
| EIR | `yggdrasil/eir/stock/low` | publie |
| MIMIR | `yggdrasil/mimir/security/infirmary` | publie, EIR s'abonne |

Payloads, QoS et panne du broker: [contrat-mqtt-eir.md](./contrat-mqtt-eir.md).

Cote EIR, c'est deja branche dans `backend/app/services/mqtt_service.py`:

- abonnement a `yggdrasil/mimir/security/infirmary`
- publication crise et stock bas
- file `offline_outbox.jsonl` si le broker ne repond pas

Cote MIMIR, la console `services/mimir-bus` ecoute ces deux topics et publie l'alerte infirmerie. Elle ne contient pas Suricata: le bouton publie un marqueur de demonstration, pas une detection reelle.

## 4. Reseau de laboratoire a livrer

| Hote | IP | Role |
|---|---|---|
| pfSense | passerelle LAN | DHCP, DNS local, filtrage, miroir de port |
| Windows 10 | 192.168.10.20 | Poste operateur et interface EIR |
| Kali | 192.168.10.100 | Mosquitto, console MIMIR |
| Objets IoT | 192.168.10.x | Capteurs publies uniquement en local |

Configuration pfSense attendue:

- LAN `192.168.10.1/24`
- DHCP `192.168.10.50` a `192.168.10.150`, reservations `.20` et `.100`
- DNS local seulement
- LAN autorise vers MQTT `1883` sur Kali
- Port miroir vers l'ecoute IDS
- Scenario coupure: desactiver le WAN sans toucher le LAN
- Export XML du labo, sans mot de passe reel

## 5. Cas a demontrer

### Cas 1 — alerte infirmerie visible dans EIR

1. Un flux de demonstration est marque de facon explicite (en-tete de labo, pas une attaque reelle).
2. L'IDS du labo leve une alerte.
3. pfSense bloque ensuite ce flux de demonstration.
4. MIMIR publie sur `yggdrasil/mimir/security/infirmary`.
5. EIR enregistre l'alerte et l'affiche dans le journal administrateur.

Critere: la meme alerte est visible cote reseau et dans EIR.

### Cas 2 — coupure du lien Terre

1. Desactiver la passerelle WAN.
2. DHCP et DNS internes repondent encore.
3. Windows, Kali et EIR continuent de publier sur Mosquitto local.
4. Si le broker tombe, chaque cote conserve sa file et la rejoue au retour.

Critere: le chat EIR et un message MQTT restent possibles sans WAN.

### Cas 3 — stock bas

1. Dans EIR, un medicament passe a zero.
2. EIR publie `yggdrasil/eir/stock/low`.
3. MIMIR affiche le code medicament et la quantite.
4. MIMIR ne modifie pas PostgreSQL d'EIR.

La reponse clinique (serre, cuve, protocole) est entierement dans EIR. Voir `docs/pharmacie-vivante.md` du depot medichat.

## 6. Ordre de realisation

Deja dans le depot:

1. Console qui s'abonne aux topics EIR et affiche un stock bas ou une crise.
2. Publication d'une alerte infirmerie, relue dans EIR (`GET /api/security/alerts` ou le journal admin).
3. File d'attente si Mosquitto est arrete, rejouee au retour.

Encore en salle, pas dans le code:

4. Ping et MQTT entre Windows et Kali sans Internet, avec pfSense.
5. Couper le WAN et refaire un echange local.
6. Trois captures et un oral de 60 secondes.

## 7. Arborescence

```
docs/cahier-des-charges-dev.md
docs/contrat-mqtt-eir.md
services/mimir-bus/    console MQTT: ecoute EIR, publie l'alerte, file locale
infra/                 reserve au labo, sans secret et sans XML de mot de passe
```

Ne pas versionner de mot de passe, de `.env`, ni de capture contenant autre chose que le trafic de demonstration.

## 8. Critere de fini pour le couple

- Un message `stock/low` parti d'EIR apparait sur la console MIMIR.
- Un message `security/infirmary` parti de MIMIR apparait dans le journal EIR.
- Les deux echangent encore apres coupure du WAN.
- Aucun des deux depots ne contient de procedure de fabrication de medicament ni d'outil d'attaque.

## 9. Phrase de soutenance

MIMIR empeche une fuite de donnees de capsule et maintient le dialogue interne quand la Terre disparait. EIR recoit l'alerte et continue de soigner avec le stock local, puis avec la serre si les flacons sont vides.
