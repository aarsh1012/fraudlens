# FraudLens — Architecture & Project Structure

This document describes how FraudLens is structured, how data flows through it, and which pattern each layer follows. Keep this updated as the project evolves — it's meant to be the single reference for "how does this thing actually work."

---

## 1. High-Level Overview

FraudLens is a fraud-detection web application with two detection modes:

1. **Website/URL fraud detection** (built first, fully working)
2. **Mobile application fraud detection** (planned second phase)

Both modes are accessed through one web app, share one user account system, and store their check history in one database. Under the hood, the system is split into **three tiers**, plus a dedicated **ML microservice** that the backend calls into — similar to how a normal MERN app might call any third-party API, except this API is one we built and trained ourselves.

---

## 2. Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────┐
│  TIER 1 — FRONTEND (React + Vite)                        │
│  UI Layer → Hook Layer → State/Context Layer              │
│                     │                                      │
│                     ▼                                      │
│              API Service Layer                             │
└───────────────────────┬─────────────────────────────────┘
                         │ HTTPS (Axios)
                         ▼
┌─────────────────────────────────────────────────────────┐
│  TIER 2 — BACKEND (Node.js + Express)                     │
│  Route → Auth Middleware → Controller → Service            │
│                                   │                         │
│                                   ▼                         │
│                            Mongoose Model                  │
└──────────────┬──────────────────────────┬─────────────────┘
               │                          │
               ▼                          ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│  TIER 3a — DATABASE         │  │  TIER 3b — ML SERVICE        │
│  MongoDB Atlas               │  │  Python + FastAPI /predict   │
└───────────────────────────┘  └───────────────────────────┘
```

**Why three tiers plus a separate ML service?**
Node.js is excellent for handling web requests, authentication, and database access — but training and running machine learning models is Python's strength (that's where scikit-learn, pandas, and the whole ML ecosystem live). So instead of forcing everything into one language, the Node backend treats the Python ML service as an external API it calls into, exactly the same pattern used for calling any third-party service.

---

## 3. Tier 1 — Frontend (React + Vite): The 4-Layer Pattern

The frontend strictly follows a 4-layer separation. **Rule: a layer only talks to the layer directly below it — the UI never calls the API directly, and it never touches global state directly either.**

```
UI Layer
   │  (user clicks "Check", calls a hook function)
   ▼
Hook Layer ───────────────► API Service Layer ───────► Backend
   │                                                       │
   ▼                                                       │
State / Context Layer ◄───────────────────────────────────┘
   │ (result stored in state)
   ▼
UI Layer re-renders with the result
```

| Layer | Responsibility | Example |
|---|---|---|
| **UI Layer** | Pure presentation. Renders what's on screen, captures user input, calls hook functions on button clicks/form submits. Contains no business logic and no direct API calls. | `pages/Home.jsx`, `pages/Results.jsx`, `components/UrlInput.jsx` |
| **Hook Layer** | The "brain" connecting everything. Exposes clean functions the UI can call (e.g., `checkUrl()`, `getHistory()`). Internally calls the API layer, then updates State/Context with the result. | `hooks/useUrlCheck.js` |
| **State / Context Layer** | Holds data that needs to be shared across components — current result, loading status, check history. Built with React Context + `useState`. | `context/urlCheck.context.jsx` → `UrlCheckProvider` |
| **API Service Layer** | The only layer allowed to make HTTP requests. Pure functions wrapping Axios calls — no logic beyond "send this, return that." | `services/urlCheck.api.js` → `checkUrlRequest(url)` |
| **Routing** | React Router defines which page component renders for which URL path, and wraps protected pages (e.g., `/history`) behind an auth check. | `app.routes.jsx` |

**Example flow — user checks a URL:**
```
1. User types URL, clicks "Check"                         (UI)
2. UI calls hook function: checkUrl(url)                  (Hook)
3. Hook calls API service: checkUrlRequest(url)            (API)
4. Axios sends POST /api/check-url to backend
5. Backend responds with { prediction, confidence }
6. Hook updates Context with the result                   (State)
7. UI re-renders automatically, showing the result         (UI)
```

---

## 4. Tier 2 — Backend (Node.js + Express): Request Flow

The backend follows a standard layered flow: **Route → Middleware → Controller → Service → Model**. Each layer has exactly one job.

```
Route
   │  (matches POST /api/check-url to its controller)
   ▼
Auth Middleware
   │  (verifies JWT cookie — rejects with 401 if invalid/missing)
   ▼
Controller
   ├──► Service ──────► Python ML API (/predict)
   └──► Mongoose Model ──────► MongoDB
   │
   ▼
Response sent back to frontend
```

| Layer | Responsibility | Example |
|---|---|---|
| **Routes** | Defines the URL path and which controller handles it. No logic here. | `routes/urlCheck.routes.js` → `POST /api/check-url` |
| **Middleware** | Runs before the controller — checks if the user is logged in (verifies JWT cookie). Rejects the request early if not authenticated. | `middlewares/auth.middleware.js` |
| **Controller** | Receives the request, pulls out the needed data, calls the appropriate service(s), and sends back the HTTP response. Contains orchestration, not deep logic. | `controllers/urlCheck.controller.js` |
| **Service** | The actual business logic. For URL checks, this is what calls the Python ML API and formats the result. Kept separate from the controller so logic is reusable and testable. | `services/mlService.js` → `getFraudPrediction(url)` |
| **Model** | Mongoose schema defining how data is structured and stored in MongoDB. | `models/user.model.js`, `models/urlCheck.model.js` |

**Example flow — checking a URL, full request lifecycle:**
```
1. POST /api/check-url arrives
2. Route matches it to the controller
3. Auth Middleware verifies the JWT cookie (401 if invalid)
4. Controller receives the request
5. Controller calls mlService.getFraudPrediction(url)
6.    → Axios sends the URL to the Python FastAPI service
7.    ← Receives { prediction, confidence }
8. Controller saves the result via the UrlCheck model
9.    → Mongoose writes the record to MongoDB
10. Controller sends the JSON response back to the frontend
```

---

## 5. Tier 3b — ML Service (Python + FastAPI): Three-Layer Detection Flow

This is the machine learning core, exposed as its own small web service — completely independent of the Node backend, communicating only over HTTP. Prediction happens in **three layers**, checked in priority order, so the most expensive step (the ML model) only runs when the cheaper/faster checks haven't already reached a confident verdict.

```
POST /predict { url }
   │
   ▼
LAYER 1 — Trusted Domain Whitelist
   │  Is this domain (or a subdomain of it) globally trusted?
   │
   ├── YES ──► Return { LEGITIMATE, 99% confidence }  [STOP]
   │
   └── NO
        ▼
     LAYER 2 — Google Safe Browsing (live check)
        │  Has Google already confirmed this exact URL is malicious?
        │
        ├── YES ──► Return { PHISHING, 99% confidence }  [STOP]
        │
        └── NO
             ▼
          LAYER 3 — Trained ML Model
             │
             ▼
          extract_all_features(url)
             │
             ├──► String-based features        (feature_extractor.py)
             │
             └──► Network-based features, run IN PARALLEL via ThreadPoolExecutor:
                     ├── Domain age (WHOIS)
                     ├── SSL certificate validity
                     ├── Redirect count
                     ├── Response time
                     └── DNS features (nameservers, MX, SPF, TTL, resolved IPs)
             │
             ▼
          Combine into one feature row
             │
             ▼
          Load trained model (fraud_model_v2.pkl)
             │
             ▼
          Predict + confidence score
             │
             ▼
          Return JSON result to caller
```

**Why this order matters:**
- The whitelist check is instant (no network calls) — costs nothing to check first.
- Safe Browsing is a single fast API call (~100–300ms) — much cheaper than the full feature-extraction pipeline, and catches URLs already confirmed malicious by Google's constantly-updated threat database, including scams newer than our training data.
- Only URLs that pass both checks reach the ML model, which is the most expensive step (several live network lookups).
- Running the network-based feature checks (WHOIS, SSL, redirects, response time, DNS) **in parallel** via `ThreadPoolExecutor` instead of one after another reduced total prediction time by roughly 30% (measured: 4.49s → 3.17s for a full ML-layer check).

| Component | Responsibility | File |
|---|---|---|
| **API layer** | Exposes the `/predict` endpoint, validates the incoming request shape. | `main.py` |
| **Layer 1 — Whitelist** | Short-circuits well-known trusted domains (and their subdomains). | `predict.py` → `TRUSTED_DOMAINS` |
| **Layer 2 — Safe Browsing** | Calls Google's Safe Browsing API to check if the exact URL is already known-malicious. | `network_features.py` → `check_safe_browsing()` |
| **Layer 3 — Feature extraction (string-based)** | Calculates URL/domain/directory/file/query-string lexical features purely from the text of the URL. | `feature_extractor.py` |
| **Layer 3 — Feature extraction (network-based)** | Live lookups run in parallel: domain age (WHOIS), SSL validity, redirect count, response time, DNS records (nameservers, MX, SPF, TTL, resolved IPs), plus lexical heuristics (IP-literal domain, TLD count, vowel ratio, shortener detection). | `network_features.py` |
| **Model** | A Random Forest classifier trained on real-time-computable features, achieving 95.7% test accuracy. Loaded from disk at prediction time. | `fraud_model_v2.pkl`, `selected_features.pkl` |
| **Training pipeline** | Separate from the live prediction path — used only when retraining the model, not called during normal operation. | `train_model_v2.py` |

---

## 6. Planned Module — Mobile App Fraud Detection (Phase 2)

Not yet implemented, but designed to slot into the same architecture:

```
Frontend (same input UI, extended)
   │  app name / identifier
   ▼
Backend: POST /api/check-app
   │
   ▼
appCheckService.js
   │
   ├──► Play Store metadata scraper (rating, permissions, developer age)
   └──► RBI Digital Lending App directory / banned-apps list cross-check
   │
   ▼
Combined fraud-risk score
   │
   ▼
Saved to same history collection (type: "app")
```

| Layer | Planned responsibility |
|---|---|
| Frontend | Same input UI, extended to accept an app name/identifier alongside a URL |
| Backend | New route `POST /api/check-app`, new service `appCheckService.js` |
| Data sources | Play Store metadata scraping (rating, permissions, developer age) + cross-reference against RBI's Digital Lending App directory / banned-apps list |
| Output | Same result shape as URL checks (prediction + confidence + reasoning), stored in the same history collection with a `type: "app"` field to distinguish it from `type: "url"` checks |

---

## 7. Full Project Folder Structure

```
FraudLens/
│
├── Frontend/                        (React + Vite)
│   ├── src/
│   │   ├── pages/                   ← UI Layer
│   │   ├── components/              ← UI Layer (reusable pieces)
│   │   ├── hooks/                   ← Hook Layer
│   │   ├── context/                 ← State/Context Layer
│   │   ├── services/                ← API Service Layer
│   │   ├── app.routes.jsx           ← Routing
│   │   └── App.jsx
│   └── .env                         (VITE_API_URL)
│
├── Backend/                         (Node.js + Express)
│   ├── src/
│   │   ├── routes/
│   │   ├── middlewares/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── models/
│   │   └── config/                  (database.js)
│   ├── server.js
│   └── .env                         (MONGO_URI, JWT_SECRET, ML_SERVICE_URL, FRONTEND_URL)
│
├── ML-Services/                     (Python + FastAPI)
│   ├── main.py                      ← API layer
│   ├── predict.py                   ← Whitelist + Safe Browsing + ML orchestration
│   ├── feature_extractor.py         ← String-based features
│   ├── network_features.py          ← Network/DNS features + Safe Browsing check
│   ├── train_model_v2.py            ← Training pipeline
│   ├── fraud_model_v2.pkl           ← Trained model
│   ├── selected_features.pkl        ← Expected feature order
│   ├── dataset_small.csv            ← Training data
│   ├── dataset_full.csv             ← Validation data
│   ├── requirements.txt             ← Python dependencies
│   ├── .env                         (GOOGLE_SAFE_BROWSING_API_KEY)
│   └── tests/                       ← Exploration/debug/benchmark scripts
│
└── ARCHITECTURE.md                  ← This file
```

---

## 8. Tech Stack Summary

| Layer | Technology | Why |
|---|---|---|
| Frontend | React, Vite | Fast dev experience, component-based UI |
| Frontend state | React Context + Hooks | Lightweight, no extra library needed for this scale |
| Backend | Node.js, Express | Familiar, fast to build REST APIs with |
| Auth | JWT + httpOnly cookies | Secure, stateless authentication |
| Database | MongoDB Atlas + Mongoose | Flexible schema, easy cloud hosting |
| ML | Python, scikit-learn, pandas, joblib | Industry-standard ML tooling |
| ML API | FastAPI + Uvicorn | Lightweight, auto-generates interactive API docs |
| DNS lookups | dnspython | Free nameserver/MX/SPF/TTL queries |
| Live threat intel | Google Safe Browsing API | Free, constantly-updated database of known-malicious URLs |
| Concurrency | Python `ThreadPoolExecutor` | Runs independent network checks in parallel instead of sequentially |
| Inter-service communication | Axios (Node → Python) | Simple HTTP calls between services |
| Deployment (planned) | Vercel (frontend), Render (backend + ML service) | Free tier, straightforward deploys |

---

## 9. Design Principles Followed

1. **Every layer has one job.** UI doesn't fetch data. Controllers don't contain business logic. Services don't touch HTTP requests/responses directly.
2. **Every ML feature used in production must be honestly reproducible in real time** — no feature is used in training that can't also be computed for a brand-new, live input.
3. **Cheaper, faster checks run before expensive ones.** The whitelist and Safe Browsing checks are tried first, in increasing order of cost, so the ML model — the most expensive step — only runs when genuinely needed.
4. **List-based and live-lookup safety nets complement the learned model, not replace it** — no ML model, trained on a static historical dataset, should be expected to correctly judge every case alone, especially against threats newer than its training data.
5. **Independent operations run in parallel, not sequentially**, wherever they don't depend on each other's results — applied to the network-based feature checks to reduce total response time.
6. **Both detection modes (URL and app) share the same infrastructure** — one auth system, one database, one frontend shell — so adding the app-detection module later means adding a new service and route, not rebuilding the app.