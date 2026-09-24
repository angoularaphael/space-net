# MIMIR

Systeme nerveux numerique du vaisseau Yggdrasil (workshop EPSI Horizon 2080, pilier DeepTech).

MIMIR securise le reseau de capsule et garde les echanges internes quand le lien Terre est coupe. La pharmacie est un autre depot: [EIR / medichat](https://github.com/angoularaphael/medichat).

Cahier des charges developpeur: [docs/cahier-des-charges-dev.md](docs/cahier-des-charges-dev.md).

Contrat MQTT partage: [docs/contrat-mqtt-eir.md](docs/contrat-mqtt-eir.md).

## Console locale

Le prototype executable est la console `services/mimir-bus`. Elle ecoute Mosquitto (celui d'EIR, port 1883), affiche crise et stock bas, et publie une alerte infirmerie de demonstration. Si le broker est arrete, l'alerte reste dans `data/outbox.jsonl`.

Le laboratoire pfSense / Suricata n'est pas dans ce depot: pas d'export de mot de passe, pas d'outil d'attaque. La console simule le message que l'IDS enverrait, avec un texte explicite de demonstration.

```powershell
cd services\mimir-bus
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m mimir_bus
```

Ouvrir http://127.0.0.1:8090 pendant que `docker compose` d'EIR tourne. Puis, dans EIR, journal administrateur: les alertes MIMIR apparaissent au canal securite.
