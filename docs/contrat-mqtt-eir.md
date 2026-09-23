# Contrat MQTT MIMIR - EIR

Broker: Mosquitto sur le LAN de capsule, port 1883.  
QoS: 1. Encodage: JSON UTF-8.  
LAN de laboratoire: `192.168.10.0/24`. Aucun de ces messages ne doit dependre d'Internet.

EIR publie. MIMIR ecoute et affiche. MIMIR ne reecrit pas le stock pharmacie.

## EIR vers le bus

### `yggdrasil/eir/alert/crisis`

```json
{
  "level": "epidemic",
  "sick_ratio": 0.15,
  "autonomy_days": 9
}
```

### `yggdrasil/eir/stock/low`

```json
{
  "drug_id": "paracetamol",
  "remaining_units": 0
}
```

`drug_id` est le code medicament EIR (`paracetamol`, `amoxicillin`, etc.).

## MIMIR vers le bus

### `yggdrasil/mimir/security/infirmary`

EIR enregistre le JSON dans `security_alerts` et l'expose sur `GET /api/security/alerts`.

```json
{
  "alert": "stock_tampering",
  "drug_id": "paracetamol",
  "message": "Tentative de falsification des donnees de stock infirmerie"
}
```

Autres valeurs utiles de `alert` pour la demo: `suricata_match`, `wan_down`, `broker_recovered`.

## Panne du broker

EIR empile les publications dans `backend/data/offline_outbox.jsonl` et les rejoue au retour du broker. MIMIR doit faire l'equivalent de son cote: ne pas perdre une alerte infirmerie si Mosquitto est arrete, et la publier quand il revient.

Le lien Terre peut rester coupe pendant tout ce cycle.
