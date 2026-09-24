TOPIC_CRISIS = "yggdrasil/eir/alert/crisis"
TOPIC_STOCK = "yggdrasil/eir/stock/low"
TOPIC_INFIRMARY = "yggdrasil/mimir/security/infirmary"

EIR_TOPICS = (TOPIC_CRISIS, TOPIC_STOCK)

ALERTS = {
    "suricata_match": (
        "Marqueur de demonstration : flux fictif vers l'infirmerie. "
        "Aucune donnee medicale n'est copiee."
    ),
    "stock_tampering": (
        "Marqueur de demonstration : ecart de stock signale par le reseau. "
        "MIMIR ne modifie pas la base d'EIR."
    ),
    "wan_down": "Lien Terre coupe. Le reseau interne et MQTT restent locaux.",
    "broker_recovered": "Broker MQTT de nouveau joignable. La file locale est rejouee.",
}


def infirmary_payload(alert: str, drug_id: str | None = None) -> dict:
    if alert not in ALERTS:
        raise ValueError("Alerte inconnue")
    payload = {"alert": alert, "message": ALERTS[alert]}
    if drug_id:
        cleaned = "".join(ch for ch in drug_id if ch.isalnum() or ch in "-_")[:40]
        if cleaned:
            payload["drug_id"] = cleaned
    return payload
