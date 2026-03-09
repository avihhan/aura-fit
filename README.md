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

- `server/.env.example`
- `mobile/.env.example`
- `web-portal/.env.example`
