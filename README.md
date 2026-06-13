

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/Market%20Analysis%20Cockpit-%2300C853?style=for-the-badge&logo=chartjs&logoColor=white">
    <img src="https://img.shields.io/badge/Market%20Analysis%20Cockpit-%2300C853?style=for-the-badge&logo=chartjs&logoColor=white" alt="Market Analysis Cockpit">
  </picture>
</p>

<p align="center">
  <strong>Dashboard de trading intelligent</strong> — Analyse technique temps réel, indicateurs, niveaux clés, et scoring multi-actifs.
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-docker-deployment">Docker</a> •
  <a href="#%EF%B8%8F-api-configuration">API Config</a> •
  <a href="#-api-endpoints">API</a> •
  <a href="#-project-structure">Structure</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-%233776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-%23009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-15-%23000000?logo=next.js&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/yfinance-live-%23darkgreen" alt="yfinance">
  <img src="https://img.shields.io/badge/DuckDB-cache-%23FFF000" alt="DuckDB">
  <img src="https://img.shields.io/badge/License-MIT-%23yellow" alt="License">
</p>

---

## 📋 Table des matières

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [🚀 Quick Start](#-quick-start)
  - [Local (dev)](#local-dev)
  - [Docker (prod)](#docker-prod)
- [🐳 Docker Deployment](#-docker-deployment)
- [⚙️ API Configuration](#️-api-configuration)
- [📡 API Endpoints](#-api-endpoints)
- [📁 Project Structure](#-project-structure)
- [🌍 Assets disponibles](#-assets-disponibles)
- [🔧 Personnalisation](#-personnalisation)
- [📄 License](#-license)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📊 Analyse temps réel
- Données **yfinance** live (pas de mock)
- Cache **DuckDB** pour les performances
- Fallback automatique vers données simulées
- 5 actifs majeurs pré-configurés (Forex, Crypto, Indices, Commodités)

</td>
<td width="50%">

### 📈 Indicateurs techniques
- **RSI** — Force relative, zones de sur-achat/vente
- **ADX** — Force de la tendance
- **ATR** — Volatilité
- **MACD** — Croisements de momentum
- **EMA 20/50/200** — Tendances court/moyen/long terme

</td>
</tr>
<tr>
<td width="50%">

### 🎯 Analyse de structure
- **Tendance** identifiée (haussière/baissière/neutre)
- **Momentum** directionnel
- **Volatilité** relative (haute/normale/basse)
- **Consolidation / Breakout / Sweep** patterns

</td>
<td width="50%">

### 🧱 Niveaux clés
- **Supports et résistances** automatiques
- Importance basée sur le nombre de touches
- Proximité des prix en temps réel
- Badges de fiabilité

</td>
</tr>
<tr>
<td width="50%">

### 🔮 Scénarios
- Scénario **bullish** avec cible et invalidation
- Scénario **bearish** avec cible et invalidation
- Direction basée sur tendance + momentum

</td>
<td width="50%">

### ⭐ Scoring intelligent
- Score composite sur 100
- Pondération: tendance > momentum > RSI > MACD > volatilité
- Vue rapide de la qualité du setup

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                        │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │   Dashboard   │  │  Asset Detail   │  │ CandlestickChart │   │
│  │ (Asset Cards) │  │  (Full Analysis)│  │  (lightweight)  │   │
│  └──────┬───────┘  └───────┬────────┘  └────────┬────────┘   │
│         │                  │                     │            │
│         └──────────────────┼─────────────────────┘            │
│                            │ HTTP (fetch)                     │
└────────────────────────────┼─────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────┐
│                     Backend (FastAPI)                         │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Routes  │→ │ Analysis │→ │  Market   │  │    Cache     │  │
│  │         │  │ Modules  │  │  Data     │  │   (DuckDB)   │  │
│  │ /assets │  │          │  │           │  │              │  │
│  │ /candles│  │indicators│  │ yfinance  │  │ candles      │  │
│  │ /levels │  │ levels   │  │ mock_data │  │ analysis     │  │
│  │ /brief  │  │scenarios │  │           │  │              │  │
│  │ /health │  │ scoring  │  │           │  │              │  │
│  └─────────┘  └──────────┘  └───────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Couche | Technologie | Rôle |
|--------|------------|------|
| **Backend** | **Python 3.12 + FastAPI** | API REST asynchrone |
| **Data** | **yfinance** | Données marché temps réel (gratuit, pas de clé API) |
| **Analyse** | **pandas + pandas-ta** | Calculs d'indicateurs techniques |
| **Cache** | **DuckDB** | Base de données colonnes embarquée |
| **Frontend** | **Next.js 15 + React 19** | Interface utilisateur |
| **Charts** | **Lightweight Charts** | Graphiques bougies (TradingView-like) |
| **UI** | **shadcn/ui + Tailwind CSS** | Composants et style |
| **Déploiement** | **Docker + docker-compose** | Conteneurisation |

---

## 🚀 Quick Start

### Local (dev)

**Prérequis :** Python 3.12+, Node.js 20+, `uv` (ou `pip`)

```bash
# 1. Cloner
git clone https://github.com/TMSSS05/cockpit-analyse.git
cd cockpit-analyse

# 2. Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API → http://localhost:8000

# 3. Frontend (nouveau terminal)
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### Docker (prod)

```bash
# Build & lancement
docker compose up --build

# Frontend → http://localhost:3000
# API     → http://localhost:8000
# Docs    → http://localhost:8000/docs
```

<details>
<summary><strong>⚡ Avec Make (optionnel, mais pratique)</strong></summary>

```bash
make install    # Installe backend + frontend
make dev        # Lance backend + frontend en dev
make docker     # Lance avec Docker
make test       # Lance les tests backend
```
</details>

---

## 🐳 Docker Deployment

Le projet inclut une configuration Docker prête à l'emploi pour un déploiement en production.

### Architecture Docker

```
┌───────────────┐       ┌───────────────┐
│  Frontend     │──────▶│  Backend      │
│  Next.js      │ HTTP  │  FastAPI      │
│  port 3000    │       │  port 8000    │
└───────────────┘       └───────┬───────┘
                                │
                        ┌───────▼───────┐
                        │  Données      │
                        │  yfinance     │
                        │  (externe)    │
                        └───────────────┘
```

### Fichiers

- **`backend/Dockerfile`** — Image Python 3.12 slim, installe les dépendances, expose le port 8000
- **`frontend/Dockerfile`** — Build multi-stage Next.js (standalone output), expose le port 3000
- **`docker-compose.yml`** — Orchestre les deux services avec réseau partagé

### Commandes utiles

```bash
# Construire et lancer
docker compose up --build

# Lancer en arrière-plan
docker compose up -d

# Voir les logs
docker compose logs -f

# Arrêter
docker compose down

# Reconstruire un seul service
docker compose build backend
docker compose up -d
```

### Volumes

- Les caches DuckDB sont stockés dans le conteneur backend (volume anonyme)
- Les données ne persistent **pas** entre les redémarrages par défaut
- Pour persister le cache : décommentez la section `volumes` dans `docker-compose.yml`

---

## ⚙️ API Configuration

Ce projet utilise **yfinance** pour récupérer les données de marché — **aucune clé API n'est requise**. Toutes les données proviennent de sources publiques et gratuites.

### Configuration disponible

| Variable | Défaut | Description |
|----------|--------|-------------|
| `MAC_USE_MOCK_DATA` | `false` | `true` → utilise des données simulées |
| `MAC_YFINANCE_ENABLED` | `true` | `false` → désactive yfinance |
| `MAC_CCXT_ENABLED` | `true` | `false` → désactive ccxt (crypto via exchange) |
| `MAC_HOST` | `0.0.0.0` | Adresse d'écoute du serveur |
| `MAC_PORT` | `8000` | Port d'écoute |
| `MAC_CORS_ORIGINS` | `http://localhost:3000` | Origines CORS autorisées |
| `MAC_DATA_DIR` | `./data` | Répertoire des données |
| `MAC_DUCKDB_PATH` | `./data/market_data.duckdb` | Chemin du cache DuckDB |
| `MAC_CACHE_EXPIRE_HOURS` | `1` | Durée de vie du cache |

### Fichier `.env.example`

```env
# ─── Mode données ──────────────────────────────────
MAC_USE_MOCK_DATA=false
MAC_YFINANCE_ENABLED=true

# ─── Serveur ───────────────────────────────────────
MAC_HOST=0.0.0.0
MAC_PORT=8000
MAC_CORS_ORIGINS=http://localhost:3000

# ─── Cache ─────────────────────────────────────────
MAC_DUCKDB_PATH=./data/market_data.duckdb
MAC_CACHE_EXPIRE_HOURS=1
```

Copiez simplement ce fichier :

```bash
cp .env.example .env
```

> **💡 Conseil :** En production, si vous hébergez le backend sur un VPS, mettez à jour `MAC_CORS_ORIGINS` avec l'URL de votre frontend déployé (ex: `https://mon-dashboard.com`).

---

## 📡 API Endpoints

### `GET /api/health`
Santé du service.

```json
{
  "status": "ok",
  "timestamp": "2026-06-12T22:00:00Z",
  "mock_mode": false,
  "uptime_hours": 2.5
}
```

### `GET /api/assets`
Liste des actifs disponibles.

```json
{
  "assets": [
    { "symbol": "XAUUSD", "name": "Gold", "type": "commodity", "price": 2334.50, "change_24h": 0.45 },
    { "symbol": "BTC", "name": "Bitcoin", "type": "crypto", "price": 67890.00, "change_24h": -1.23 }
  ]
}
```

### `GET /api/candles/{symbol}?timeframe=1h&count=200`
Bougies OHLCV.

| Paramètre | Valeurs | Défaut |
|-----------|---------|--------|
| `timeframe` | `5m`, `15m`, `1h`, `4h`, `1d` | `1h` |
| `count` | 1–500 | `200` |

### `GET /api/analysis/{symbol}?timeframe=1h`
Analyse technique complète.

```json
{
  "indicators": {
    "rsi": { "value": 58.2, "signal": "neutral" },
    "adx": { "value": 28.5, "signal": "trending" },
    "atr": { "value": 15.3 },
    "macd": { "value": 12.4, "signal": "bullish_cross", "histogram": 3.1 },
    "ema_20": 4210.5, "ema_50": 4180.2, "ema_200": 4050.0
  },
  "structure": {
    "trend": "bullish",
    "momentum": "positive",
    "volatility": "normal",
    "consolidation": false,
    "breakout": true,
    "sweep": false
  },
  "scenarios": [
    {
      "direction": "bullish",
      "target": 4280.0,
      "invalidation": 4180.0,
      "confidence": 72,
      "rationale": "Prix au-dessus des EMAs + RSI haussier"
    }
  ],
  "levels": [
    { "price": 4200.0, "type": "support", "strength": "strong", "touches": 4 },
    { "price": 4250.0, "type": "resistance", "strength": "moderate", "touches": 2 }
  ],
  "score": 72
}
```

### `GET /api/levels/{symbol}?timeframe=1h`
Niveaux supports/résistances uniquement.

### `GET /api/brief?symbols=XAUUSD,BTC`
Résumé rapide multi-actifs (utilisé par le dashboard).

---

## 📁 Project Structure

```
cockpit-analyse/
├── backend/
│   ├── app/
│   │   ├── analysis/
│   │   │   ├── indicators.py      # RSI, ADX, ATR, MACD, EMAs
│   │   │   ├── levels.py          # Supports/résistances
│   │   │   ├── market_structure.py # Tendance, momentum, patterns
│   │   │   ├── scenarios.py       # Scénarios bullish/bearish
│   │   │   └── scoring.py         # Score composite sur 100
│   │   ├── data/
│   │   │   ├── market_data.py     # yfinance + interface données
│   │   │   ├── cache.py           # DuckDB cache layer
│   │   │   └── mock_data.py       # Données simulées
│   │   ├── routes/
│   │   │   ├── assets.py          # GET /api/assets
│   │   │   ├── candles.py         # GET /api/candles/{symbol}
│   │   │   ├── analysis.py        # GET /api/analysis/{symbol}
│   │   │   ├── levels.py          # GET /api/levels/{symbol}
│   │   │   ├── brief.py           # GET /api/brief
│   │   │   └── health.py          # GET /api/health
│   │   ├── config.py              # Pydantic Settings
│   │   └── main.py                # App FastAPI + lifespan
│   ├── tests/
│   │   ├── test_indicators.py     # 41 tests ✅
│   │   ├── test_levels.py
│   │   ├── test_market_structure.py
│   │   └── test_routes.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                    # Dashboard
│   │   │   └── assets/[symbol]/page.tsx    # Détail actif
│   │   ├── components/
│   │   │   ├── chart/CandlestickChart.tsx  # Graphique bougies
│   │   │   ├── dashboard/AssetCard.tsx     # Carte actif
│   │   │   └── ui/                         # shadcn/ui components
│   │   └── lib/
│   │       ├── api.ts                      # Client API typé
│   │       └── utils.ts
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🌍 Assets disponibles

| Symbole | Nom | Type | Source yfinance |
|---------|-----|------|----------------|
| **XAUUSD** | Gold | 🪙 Commodité | `GC=F` |
| **BTC** | Bitcoin | ₿ Crypto | `BTC-USD` |
| **NASDAQ** | Nasdaq | 📊 Index | `^IXIC` |
| **OIL** | Crude Oil | 🛢️ Commodité | `CL=F` |
| **EURUSD** | EUR/USD | 💶 Forex | `EURUSD=X` |

### Timeframes supportés

`5m` · `15m` · `1h` · `4h` · `1d`

---

## 🔧 Personnalisation

### Ajouter un actif

Modifiez `backend/app/config.py` :

```python
ASSETS = {
    "AAPL": {"name": "Apple Inc.", "yfinance": "AAPL", "ccxt": None, "type": "stock"},
    # ...
}
```

### Modifier les seuils d'analyse

```python
STRONG_TREND_ADX = 25.0        # ADX minimum pour "tendance forte"
RSI_EXTREME_HIGH = 70.0        # Seuil sur-achat RSI
PROXIMITY_ATR_MULTIPLIER = 0.5 # Proximité des niveaux (en ATR)
```

---

## 📄 License

MIT © 2026 [TMSSS05](https://github.com/TMSSS05)

---

<p align="center">
  <sub>Construit avec 🐍 FastAPI · ⚛️ Next.js · 📊 yfinance</sub>
</p>
