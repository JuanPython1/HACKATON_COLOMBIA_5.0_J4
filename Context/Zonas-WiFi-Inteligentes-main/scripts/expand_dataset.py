"""
Expansion del dataset de eventos de red para la Hackathon Zonas WiFi Inteligentes.

Lee los CSV originales (en ../originals si existen, si no en el directorio raiz),
genera eventos sinteticos realistas siguiendo los patrones de Cisco Meraki
(autenticacion -> asociacion -> desasociacion) y reemplaza:

  - network_events_curated.csv  (>= 5000 filas)
  - clients_curated.csv         (clientes existentes + nuevos)
  - ap_hourly_metrics_curated.csv (recomputado)

Mantiene la distribucion observada por AP, agrega ventanas de tiempo extendidas
y produce algunos picos de carga, intermitencias y ventanas con menos trafico
para simular comportamiento realista.
"""

from __future__ import annotations

import hashlib
import os
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RNG_SEED = 2026
TARGET_TOTAL_EVENTS = 5500  # margen sobre 5000
NEW_CLIENTS = 220
SSID = "Zona Wifi Rural Gratis-Alcaldia"

random.seed(RNG_SEED)
np.random.seed(RNG_SEED)


# ----------------------------- utilidades ----------------------------- #

def project_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def load_originals() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    root = project_root()
    src = os.path.join(root, "originals")
    if not os.path.isdir(src):
        src = root
    events = pd.read_csv(os.path.join(src, "network_events_curated.csv"))
    clients = pd.read_csv(os.path.join(src, "clients_curated.csv"))
    aps = pd.read_csv(os.path.join(src, "access_points_curated.csv"))
    try:
        hourly = pd.read_csv(os.path.join(src, "ap_hourly_metrics_curated.csv"))
    except FileNotFoundError:
        hourly = pd.DataFrame()
    events["timestamp"] = pd.to_datetime(events["timestamp"])
    if "last_seen" in clients.columns:
        clients["last_seen"] = pd.to_datetime(clients["last_seen"])
    return events, clients, aps, hourly


def random_mac(rng: random.Random) -> str:
    return ":".join(f"{rng.randint(0, 255):02X}" for _ in range(6))


def hash_client_id(seed: str) -> str:
    return hashlib.md5(seed.encode("utf-8")).hexdigest()[:16]


# ----------------------------- generacion ----------------------------- #

DEVICE_TEMPLATES = [
    ("Android", "Android"),
    ("Samsung Galaxy A16, Android 16", "Samsung"),
    ("Samsung Galaxy A55, Android 14", "Samsung"),
    ("Apple iPhone 13, iOS18.5", "Apple iPhone"),
    ("Apple iPhone 11, iOS18.6.2", "Apple iPhone"),
    ("Apple iPhone 15, iOS18.6", "Apple iPhone"),
    ("Redmi-Note-14", "Android"),
    ("Redmi-13C", "Android"),
    ("HONOR-X5b", "Android"),
    ("OPPO-A38", "Android"),
    ("ZTE-Blade-A34", "Android"),
    ("moto-g04s", "Other"),
    ("TECNO-SPARK-40-Pro", "Android"),
    ("Windows-10", "Windows 10"),
    ("Generic Linux", "Generic Linux"),
]


def generate_new_clients(existing: pd.DataFrame, ap_names: list[str], n: int,
                         rng: random.Random) -> pd.DataFrame:
    rows = []
    for i in range(n):
        desc_template, dev_type = rng.choice(DEVICE_TEMPLATES)
        suffix = rng.choice(["A", "B", "C", "D", "E"]) + str(rng.randint(100, 999))
        description = f"{desc_template.split(',')[0]}-{suffix}"
        mac_seed = f"synthetic-{i}-{rng.random()}"
        cid = hash_client_id(mac_seed)
        rows.append(
            {
                "client_id": cid,
                "status": rng.choices(["Online", "Offline"], weights=[0.35, 0.65])[0],
                "client_description": description,
                "last_seen": pd.NaT,  # se completara con el ultimo evento generado
                "usage_mb": round(np.random.exponential(scale=300.0), 4),
                "device_type": dev_type,
                "ap_name": rng.choice(ap_names),
                "policy": "normal",
                "onboarding": rng.choice([np.nan, 75.0, 78.0, 80.0, 83.0, 96.0, 100.0]),
            }
        )
    df_new = pd.DataFrame(rows)
    existing_ids = set(existing["client_id"].astype(str).tolist())
    df_new = df_new[~df_new["client_id"].isin(existing_ids)].reset_index(drop=True)
    return df_new


def build_event_session(
    ap: str,
    client_id: str,
    client_description: str,
    start_ts: datetime,
    rng: random.Random,
    is_unstable_ap: bool,
) -> list[dict]:
    """Crea una sesion realista (auth -> association -> [splash] -> disassociation)."""
    events: list[dict] = []
    band = rng.choices([2, 5], weights=[0.55, 0.45])[0]
    channel = rng.choice([1, 6, 11]) if band == 2 else rng.choice([36, 40, 44, 149, 153, 157, 161])
    rssi = rng.randint(5, 60)
    mac = random_mac(rng)
    aid = rng.randint(100_000_000, 2_147_483_647)

    # 1) 802.1X authentication
    events.append(
        {
            "timestamp": start_ts,
            "ap_name": ap,
            "ssid": SSID,
            "client_id": client_id,
            "client_description": client_description,
            "event_category": "802.1X",
            "event_type": "802.1X authentication",
            "event_detail": f'"radio: {0 if band == 2 else 1}, vap: 0, client_mac: {mac}, aid: {aid}"',
        }
    )
    # 2) 802.11 association (mismo segundo o +1)
    assoc_ts = start_ts + timedelta(seconds=rng.choice([0, 0, 0, 1]))
    events.append(
        {
            "timestamp": assoc_ts,
            "ap_name": ap,
            "ssid": SSID,
            "client_id": client_id,
            "client_description": client_description,
            "event_category": "802.11",
            "event_type": "802.11 association",
            "event_detail": f'"channel: {channel}, rssi: {rssi}, band: {band}"',
        }
    )
    # 3) Splash auth opcional (~15%)
    if rng.random() < 0.15:
        events.append(
            {
                "timestamp": assoc_ts + timedelta(seconds=rng.randint(0, 2)),
                "ap_name": ap,
                "ssid": SSID,
                "client_id": client_id,
                "client_description": client_description,
                "event_category": "Auth",
                "event_type": "Splash authentication",
                "event_detail": '"duration: 3600"',
            }
        )

    # 4) Una o mas desasociaciones (mas si es AP inestable)
    n_disassoc = 1 + (1 if rng.random() < (0.45 if is_unstable_ap else 0.20) else 0)
    last_ts = assoc_ts
    detail_pool = [
        '"client was deauthenticated"',
        '"previous authentication expired"',
        '"client has left AP"',
        '"client not responding"',
    ]
    for _ in range(n_disassoc):
        gap = rng.randint(2, 600 if not is_unstable_ap else 90)
        last_ts = last_ts + timedelta(seconds=gap)
        events.append(
            {
                "timestamp": last_ts,
                "ap_name": ap,
                "ssid": SSID,
                "client_id": client_id,
                "client_description": client_description,
                "event_category": "802.11",
                "event_type": "802.11 disassociation",
                "event_detail": rng.choice(detail_pool),
            }
        )
    return events


def hour_weight(hour: int) -> float:
    """Patron tipico de uso WiFi publico: pico 9-12 y 18-22."""
    base = 0.2
    if 6 <= hour <= 8:
        return base + 0.6
    if 9 <= hour <= 12:
        return base + 1.0
    if 13 <= hour <= 17:
        return base + 0.7
    if 18 <= hour <= 22:
        return base + 1.1
    return base + 0.05


def random_session_start(start: datetime, end: datetime, rng: random.Random) -> datetime:
    total_seconds = int((end - start).total_seconds())
    while True:
        offset = rng.randint(0, total_seconds)
        candidate = start + timedelta(seconds=offset)
        if rng.random() < hour_weight(candidate.hour) / 1.3:
            return candidate.replace(microsecond=0)


def build_ap_weights(events: pd.DataFrame, ap_names: list[str]) -> dict[str, float]:
    """Pesos por AP basados en la distribucion observada + suavizado."""
    counts = Counter(events["ap_name"].tolist())
    total = sum(counts.values()) or 1
    weights = {}
    for ap in ap_names:
        observed = counts.get(ap, 0) / total
        weights[ap] = max(observed, 0.01)  # piso para que todos los AP tengan algo
    return weights


def assign_clients_to_ap(clients_df: pd.DataFrame) -> dict[str, list[tuple[str, str]]]:
    pool: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for _, row in clients_df.iterrows():
        pool[str(row["ap_name"])].append((str(row["client_id"]), str(row["client_description"])))
    return pool


# ------------------------- metricas horarias -------------------------- #

def recompute_hourly_metrics(events: pd.DataFrame, aps: pd.DataFrame) -> pd.DataFrame:
    df = events.copy()
    df["timestamp_hour"] = df["timestamp"].dt.floor("h")
    grouped = df.groupby(["timestamp_hour", "ap_name"])
    rows = []
    for (hour, ap), grp in grouped:
        total_events = len(grp)
        total_connections = int((grp["event_type"] == "802.11 association").sum())
        total_disconnections = int((grp["event_type"] == "802.11 disassociation").sum())
        total_auth = int((grp["event_type"] == "802.1X authentication").sum())
        unique_clients = grp["client_id"].nunique()
        rate = (total_disconnections / total_connections) if total_connections else np.nan
        rows.append(
            {
                "timestamp_hour": hour,
                "ap_name": ap,
                "total_events": total_events,
                "total_connections": total_connections,
                "total_disconnections": total_disconnections,
                "total_auth": total_auth,
                "unique_clients": unique_clients,
                "disconnection_rate": rate,
            }
        )
    metrics = pd.DataFrame(rows)
    status_map = dict(zip(aps["ap_name"], aps["status"]))
    metrics["status"] = metrics["ap_name"].map(status_map).fillna("online")
    metrics = metrics.sort_values(["timestamp_hour", "ap_name"]).reset_index(drop=True)
    return metrics


# ------------------------------ main ---------------------------------- #

def main() -> None:
    rng = random.Random(RNG_SEED)
    events_orig, clients_orig, aps, hourly_orig = load_originals()

    ap_names = aps["ap_name"].tolist()
    unstable_aps = set(aps.loc[aps["status"].isin(["offline", "dormant"]), "ap_name"].tolist())

    new_clients_df = generate_new_clients(clients_orig, ap_names, NEW_CLIENTS, rng)
    clients_full = pd.concat([clients_orig, new_clients_df], ignore_index=True)

    client_pool = assign_clients_to_ap(clients_full)
    for ap in ap_names:
        if not client_pool[ap]:
            client_pool[ap] = [
                (cid, desc)
                for cid, desc in zip(
                    clients_full["client_id"].astype(str), clients_full["client_description"].astype(str)
                )
            ][:25]

    weights = build_ap_weights(events_orig, ap_names)
    weighted_aps = list(weights.keys())
    weighted_vals = list(weights.values())

    existing_count = len(events_orig)
    needed_sessions_target = max(TARGET_TOTAL_EVENTS - existing_count, 0)

    start_window = events_orig["timestamp"].min()
    end_window = datetime(2026, 4, 28, 8, 0, 0)

    new_event_dicts: list[dict] = []
    sessions_created = 0
    while len(new_event_dicts) + existing_count < TARGET_TOTAL_EVENTS:
        ap = rng.choices(weighted_aps, weights=weighted_vals, k=1)[0]
        candidates = client_pool[ap]
        client_id, client_description = rng.choice(candidates)
        ts = random_session_start(start_window, end_window, rng)
        is_unstable = ap in unstable_aps
        session_events = build_event_session(
            ap=ap,
            client_id=client_id,
            client_description=client_description,
            start_ts=ts,
            rng=rng,
            is_unstable_ap=is_unstable,
        )
        new_event_dicts.extend(session_events)
        sessions_created += 1

    new_events = pd.DataFrame(new_event_dicts)
    new_events["timestamp"] = pd.to_datetime(new_events["timestamp"])
    combined = pd.concat([events_orig, new_events], ignore_index=True)
    combined = combined.sort_values("timestamp").reset_index(drop=True)
    if len(combined) > TARGET_TOTAL_EVENTS:
        combined = combined.iloc[: TARGET_TOTAL_EVENTS].reset_index(drop=True)

    last_seen_per_client = (
        combined.groupby("client_id")["timestamp"].max().rename("computed_last_seen")
    )
    clients_full = clients_full.merge(
        last_seen_per_client, left_on="client_id", right_index=True, how="left"
    )
    clients_full["last_seen"] = clients_full["computed_last_seen"].combine_first(
        clients_full["last_seen"]
    )
    clients_full = clients_full.drop(columns=["computed_last_seen"])

    metrics = recompute_hourly_metrics(combined, aps)

    root = project_root()
    combined_out = combined.copy()
    combined_out["timestamp"] = combined_out["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    combined_out.to_csv(os.path.join(root, "network_events_curated.csv"), index=False)

    clients_out = clients_full.copy()
    clients_out["last_seen"] = pd.to_datetime(clients_out["last_seen"]).dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    clients_out.to_csv(os.path.join(root, "clients_curated.csv"), index=False)

    metrics_out = metrics.copy()
    metrics_out["timestamp_hour"] = metrics_out["timestamp_hour"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    metrics_out.to_csv(os.path.join(root, "ap_hourly_metrics_curated.csv"), index=False)

    print("=" * 60)
    print("EXPANSION COMPLETADA")
    print("=" * 60)
    print(f"Eventos originales:        {existing_count}")
    print(f"Sesiones generadas:        {sessions_created}")
    print(f"Eventos nuevos generados:  {len(new_events)}")
    print(f"Eventos totales finales:   {len(combined)}")
    print(f"Clientes originales:       {len(clients_orig)}")
    print(f"Clientes nuevos:           {len(new_clients_df)}")
    print(f"Clientes totales:          {len(clients_full)}")
    print(f"Filas hourly_metrics:      {len(metrics)} (originales: {len(hourly_orig)})")
    print(f"Rango temporal eventos:    {combined['timestamp'].min()}  ->  {combined['timestamp'].max()}")
    print()
    print("Top 5 AP por eventos:")
    print(combined["ap_name"].value_counts().head(5).to_string())


if __name__ == "__main__":
    main()
