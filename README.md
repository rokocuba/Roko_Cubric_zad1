# TicketHub - Support Ticket Management API

**Autor:** Roko Čubrić  
**Email:** roko.cubric@fer.hr  
**Institucija:** Fakultet elektrotehnike i računarstva (FER), Zagreb  
**Projekt:** AI Akademija 2025 - Python Developer Test  

## Pregled projekta

TicketHub je REST API middleware servis koji prikuplja i izlaže support tickete iz vanjskih izvora. Razvijen je kao dio AI Akademije 2025 Python Developer testa.

**Status: ✅ ZAVRŠENO I FUNKCIONALNO**

### Cilj
Middleware REST servis koji:
- Prikuplja tickete iz DummyJSON API-ja
- Transformira podatke u vlastiti format
- Izlaže tickete kroz REST endpointove
- Omogućava filtriranje, pretragu i paginaciju
- Rješava async deadlock probleme s vanjskim API pozivima

## Tehnološki stack

### Obavezne tehnologije
- **Python 3.11** - s typing i async/await
- **FastAPI 0.111** - web framework s automatskim OpenAPI opisom
- **httpx 0.27** - za HTTP pozive prema vanjskim servisima
- **pydantic 2.7** - validacija i serializacija podataka
- **pytest** - unit i integration testovi

### Nice to have (planirano)
- SQLAlchemy + SQLite/PostgreSQL
- Redis (caching)
- Docker Compose

## Vanjski izvori podataka

- **Ticketi**: https://dummyjson.com/todos
- **Korisnici**: https://dummyjson.com/users

### Transformacija podataka
DummyJSON todo objekti se transformiraju u Ticket model:
```python
class Ticket:
    id: int                    # iz originalnog id
    title: str                 # iz todo polja
    status: str               # "closed" ako completed==true, inače "open"
    priority: str             # izračun: id % 3 → low/medium/high
    assignee: str             # korisničko ime dohvaćeno preko userId
```

## API Endpointovi

### Obavezni
1. `GET /tickets` - paginirana lista ticketa (id, title, status, priority, opis ≤100 znakova)
2. `GET /tickets/{id}` - detalji ticketa + puni JSON iz izvora
3. `GET /tickets?status=<>&priority=<>` - filtriranje po statusu i prioritetu
4. `GET /tickets/search?q=...` - pretraga po nazivu

### Nice to have (bonus)
- `GET /stats` - agregirane statistike
- `POST /auth/login` - autentifikacija (JWT) pomoću DummyJSON
- Health-check endpoint za k8s/Compose

## Struktura projekta

```
tickethub/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI aplikacija
│   ├── models/              # Pydantic modeli
│   ├── services/            # Business logika
│   ├── api/                 # API endpointovi
│   └── config.py            # Konfiguracija
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── ci/
├── .github/workflows/       # GitHub Actions
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Postavljanje okruženja

### Preduvjeti
- Python 3.11+
- pip ili poetry
- Docker (opcionalno)

### Instalacija
```bash
# Kloniraj repozitorij
git clone <repo-url>
cd tickethub

# Stvori virtualno okruženje
python -m venv venv

# Aktiviraj virtualno okruženje
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instaliraj ovisnosti
pip install -r requirements.txt

# Pokreni aplikaciju
uvicorn src.main:app --reload
```

### Konfiguracija varijabli

Stvori `.env` file:
```env
# API konfiguracija
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Vanjski servisi
DUMMYJSON_BASE_URL=https://dummyjson.com

# Cache (opcionalno)
REDIS_URL=redis://localhost:6379

# Logiranje
LOG_LEVEL=INFO
```

## Make/Task komande

```bash
# Pokretanje
make run                # Pokreni aplikaciju
make dev                # Pokreni u development modu

# Testiranje
make test               # Pokreni sve testove
make test-unit          # Samo unit testovi
make test-integration   # Samo integration testovi

# Code quality
make lint               # Linting (flake8, black)
make format             # Format koda (black, isort)

# Docker
make docker-build       # Build Docker image
make docker-run         # Pokreni s Dockerom
make docker-compose     # Pokreni s docker-compose
```

## Razvoj i testiranje

### Pokretanje testova
```bash
pytest tests/
pytest tests/unit/
pytest tests/integration/
pytest --cov=src tests/  # s coverage reportom
```

### Linting i formatiranje
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

## Docker

### Build i pokretanje
```bash
docker build -t tickethub .
docker run -p 8000:8000 tickethub

# Ili s docker-compose
docker-compose up
```

## CI/CD

GitHub Actions workflow automatski:
- Pokreće testove
- Provjerava code quality
- Gradi Docker image
- Deploya (opcionalno)

## Dokumentacija

- **OpenAPI**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## AI Asistenti korišteni

### GitHub Copilot
- **Gdje korišten**: 
  - Generiranje početne strukture projekta i direktorija
  - Standardni boilerplate kod za FastAPI aplikaciju (main.py)
  - Konfiguracija aplikacije (config.py)
  - Docker i docker-compose setup
  - GitHub Actions CI/CD workflow
  - Makefile s automatiziranim komandama
  
- **Zašto korišten**: 
  - Ubrzavanje razvoja i izbjegavanje repetitivnog koda
  - Osiguravanje industry best practices
  - Standardni patterns za FastAPI projekte
  - Smanjivanje mogućnosti grešaka u konfiguraciji

- **Konkretni prompt primjeri**:
  - "Kreiraj FastAPI main.py s health check endpointom, CORS middleware i osnovnom strukturom"
  - "Standardni pattern za konfiguraciju FastAPI aplikacija s pydantic settings"
  - "Docker multi-stage build za Python FastAPI aplikaciju s security best practices"

### Claude (GitHub Copilot Chat)
- **Gdje korišten**:
  - Analiza zadatka i kreiranje projektne strukture
  - Planiranje arhitekture i tehnološkog stacka
  - Kreiranje detaljnog README.md dokumenta
  - Procjena vremena za implementaciju
  - Objašnjavanje FastAPI koncepta za početnike

- **Zašto korišten**:
  - Razumijevanje kompleksnih zahtjeva zadatka
  - Strategijsko planiranje implementacije
  - Mentoriranje i objašnjavanje novih tehnologija
  - Kreiranje kvalitetne dokumentacije

- **Konkretni prompt primjeri**:
  - "Pročitaj upute, opiši mi što točno moram napraviti. Procjeni koliko vremena će mi trebati da ovo napravim."
  - "Postavi početnu strukturu. Održavaj ReadMe (promptovi i ostalo, kako je zadano u zahtjevu projekta)."
  - "Objasni što je FastAPI i kako implementirati REST API s vanjskim pozivima"

## Status razvoja

✅ **PROJEKT ZAVRŠEN I FUNKCIONALAN** ✅

### Implementirano i testirano:
- [x] Početna struktura projekta ✅
- [x] Osnovni FastAPI setup ✅  
- [x] Pydantic modeli ✅
- [x] Vanjski API pozivi (httpx s persistent client) ✅
- [x] **SVI OBAVEZNI ENDPOINTOVI** ✅:
  - `GET /tickets` - paginirana lista s filtriranjem
  - `GET /tickets/{id}` - detalji ticketa  
  - `GET /tickets/search?q=...` - pretraga po nazivu
  - `GET /tickets/stats/summary` - agregirane statistike (bonus)
- [x] **ASYNC DEADLOCK PROBLEM RIJEŠEN** ✅
- [x] Proper lifecycle management (startup/shutdown) ✅
- [x] Error handling i timeout konfiguracija ✅
- [x] Test i mock endpointovi ✅
- [x] Health check endpoint ✅

### Tehnički problemi riješeni:
- ✅ **Async deadlock s httpx** - zamijenjeni context manageri s persistent AsyncClient
- ✅ **Server hanging** - dodano proper lifecycle management s FastAPI lifespan events  
- ✅ **Route ordering** - specifične rute prije generičkih
- ✅ **Timeout optimizacija** - smanjeno s 30s na 10s za brže failover
- ✅ **Connection pooling** - ograničene konekcije (max 10, keepalive 5)

### Ključno tehničko rješenje:
**Problem:** Aplikacija je imala deadlock prilikom poziva na DummyJSON API - endpointovi bi "visili" beskonačno i server se nije mogao zaustaviti.

**Uzrok:** Korištenje `async with httpx.AsyncClient()` context managera za svaki request stvaralo je nové HTTP klijente koji nisu bili pravilno zatvoreni u async kontekstu.

**Rješenje:** 
1. **Persistent AsyncClient** - jedan klijent koji se dijeli kroz lifecycle aplikacije
2. **FastAPI lifespan events** - proper startup/shutdown management  
3. **Explicit client closure** - `await client.aclose()` u shutdown handleru

**Rezultat:** Svi endpointovi sada rade brzo i pouzdano, server se može normalno zaustaviti.

### Testiranje:
- ✅ Svi endpointovi rade u browseru
- ✅ DummyJSON API integracija funkcionalna
- ✅ Server ostaje responzivan
- ✅ Graceful shutdown s Ctrl+C

### Kako pokrenuti projekt (FINALNA VERZIJA)

#### 1. Postavljanje okruženja
```bash
# Navigiraj u projekt direktorij
cd tickethub

# Stvori virtualno okruženje
python -m venv venv

# Aktiviraj ga (Windows)
venv\Scripts\activate

# Instaliraj dependencies (ako nije već)
pip install fastapi uvicorn httpx pydantic pydantic-settings
```

#### 2. Pokretanje servera
```bash
# Jednostavno pokretanje
python -m uvicorn src.main:app --reload

# Server će biti dostupan na http://127.0.0.1:8000
```

#### 3. Testiranje endpointova
```bash
# Health check
curl http://127.0.0.1:8000/health

# Svi ticketi (DummyJSON API)
curl http://127.0.0.1:8000/tickets/

# Specifičan ticket
curl http://127.0.0.1:8000/tickets/1

# Pretraživanje
curl "http://127.0.0.1:8000/tickets/search?q=lorem"

# Statistike
curl http://127.0.0.1:8000/tickets/stats/summary

# Test endpointovi (bez vanjskih poziva)
curl http://127.0.0.1:8000/tickets/test
curl http://127.0.0.1:8000/tickets/mock
```

#### 4. Swagger dokumentacija
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

**API će raditi i vraćati odgovarajuće podatke iz DummyJSON servisa!** ✅

## Kontakt

**Autor:** Roko Čubrić  
**Email:** roko.cubric@fer.hr  
**Institucija:** Fakultet elektrotehnike i računarstva (FER), Zagreb  
**GitHub:** [GitHub profil]  

---

**Projekt završen:** 5. srpnja 2025.  
**AI Akademija 2025 - Python Developer Test** ✅
