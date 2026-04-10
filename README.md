# Aura Fit

Aura Fit is now fully web-based. Both client surfaces run in the browser:

- `mobile/` - React + Vite mobile web interface
- `web-portal/` - React + Vite admin web portal
- `server/` - Flask API
- Supabase - Auth + PostgreSQL

## Quick Start

### 1) Start API

```bash
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

### 2) Start mobile web app

```bash
cd mobile
npm install
copy .env.example .env
npm run dev
```

### 3) Start web portal

```bash
cd web-portal
npm install
copy .env.example .env
npm run dev
```

## Environment Variables

- `server/.env.example` — includes `CORS_ORIGINS` for extra origins (LAN IPs, Cloud Run HTTPS frontends, production domains). Defaults include localhost and Android emulator (`10.0.2.2`) for ports 3000/3001.
- `mobile/.env.example` — `VITE_API_URL` for local Flask vs **Google Cloud Run** API; emulator/device notes inside the file.
- `web-portal/.env.example`

## Mobile shell (React Native WebView)

The native app lives in a **separate repo**: `aura-fit-native` (sibling folder). It wraps the Vite mobile web app in a WebView.

- **WebView URL:** `EXPO_PUBLIC_WEB_APP_URL` in `aura-fit-native` (where the SPA is hosted).
- **API URL:** `VITE_API_URL` here in `mobile/` (baked at build time for production).

See `aura-fit-native/README.md` and `aura-fit-native/PLATFORM_NOTES.md` next to this monorepo.
