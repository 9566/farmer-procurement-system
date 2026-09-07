# Smart Farmer Procurement & Queue Management System

A full-stack prototype: FastAPI + MySQL backend, plain HTML/CSS/JS frontend,
with farmer registration, slot booking, live queue (WebSocket), procurement
tracking, payment tracking, notifications and an admin dashboard.

## 1. Prerequisites
- Python 3.10+
- MySQL Server (and MySQL Workbench, optional but helpful)
- A code editor (VS Code recommended)

## 2. Set up the database
1. Open MySQL Workbench (or the `mysql` CLI).
2. Run the script `backend/schema.sql`. This creates the `farmer_procurement`
   database, all tables, and a couple of sample centres/crops.

## 3. Configure the backend
1. Open **`backend/database.py`** and edit these lines to match your MySQL setup:
   ```python
   DB_USER = "root"
   DB_PASSWORD = "YOUR_MYSQL_PASSWORD"   # <-- change this
   DB_HOST = "localhost"
   DB_PORT = "3306"
   ```
2. Open **`backend/auth.py`** and replace the placeholder secret key:
   ```python
   SECRET_KEY = "REPLACE_WITH_YOUR_OWN_RANDOM_SECRET_KEY"
   ```
   Generate one with:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. (Optional, later) Open **`backend/services/notification.py`** and paste your
   SMS provider API key inside `send_sms()` once you're ready to send real SMS.
4. (Optional, later) Open **`backend/routers/payment.py`** if you want to wire
   up a real payment gateway (Razorpay/Stripe) — the spot is marked in the file.

## 4. Install & run the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
uvicorn main:app --reload
```
- API will run at: http://127.0.0.1:8000
- Interactive API docs: http://127.0.0.1:8000/docs

## 5. Create your first admin login
The schema doesn't insert an admin account automatically (for security).
Create one by calling the register-staff endpoint once, from the Swagger docs
(`/docs` → find `POST /admin/staff`) — but note this endpoint itself requires
an admin token, so for the *very first* admin, temporarily insert one directly
into MySQL:
```sql
-- Run this AFTER hashing a password with Python (see below), then paste the hash:
INSERT INTO staff_users (name, mobile, password, role)
VALUES ('Admin User', '9999999999', '<PASTE_BCRYPT_HASH_HERE>', 'admin');
```
To generate the bcrypt hash, run this once in a Python shell inside your venv:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
print(pwd_context.hash("your_chosen_password"))
```
Once you have one admin account, log in via `admin-dashboard.html` and use
`POST /admin/staff` to create operator accounts for each procurement centre.

## 6. Run the frontend
The frontend is plain HTML/CSS/JS — no build step needed.
- Easiest: open `frontend/index.html` directly in your browser, **or**
- Recommended: serve it so relative paths behave consistently:
  ```bash
  cd frontend
  python -m http.server 5500
  ```
  Then visit http://127.0.0.1:5500

If your backend runs on a different host/port, edit `frontend/config.js`:
```js
const API_BASE_URL = "http://127.0.0.1:8000";
const WS_BASE_URL = "ws://127.0.0.1:8000";
```

## 7. Try the full flow
1. Register a farmer on `register.html`, then log in.
2. Book a slot on `booking.html` — note the token number you get back.
3. Open `queue.html`, pick the same centre, and watch the live queue.
4. Log in as an operator on `procurement.html` (create that account per
   Step 5), click **Call Next Farmer**, then update procurement status for
   that booking.
5. Update the payment for that booking via the `/docs` Swagger UI
   (`POST /payments?booking_id=...`) or extend `payment.html` with an
   operator form (currently `payment.html` is read-only, for farmers to
   check status).
6. Log in as admin on `admin-dashboard.html` to see stats and the crop chart.

## 8. Folder structure
```
farmer-procurement-system/
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── farmer-dashboard.html
│   ├── booking.html
│   ├── queue.html
│   ├── procurement.html
│   ├── payment.html
│   ├── admin-dashboard.html
│   ├── config.js
│   └── css/style.css
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── schema.sql
│   ├── requirements.txt
│   ├── routers/
│   │   ├── farmer.py
│   │   ├── booking.py
│   │   ├── queue.py
│   │   ├── procurement.py
│   │   ├── payment.py
│   │   └── admin.py
│   └── services/
│       ├── notification.py
│       └── queue_manager.py
└── README.md
```

## 9. Where you'll need to paste things / make changes (quick checklist)
| File | What to change |
|---|---|
| `backend/database.py` | Your MySQL username, password, host |
| `backend/auth.py` | Your own random `SECRET_KEY` |
| `backend/services/notification.py` | SMS provider API key (optional) |
| `backend/routers/payment.py` | Real payment gateway integration (optional) |
| `backend/main.py` | Restrict `allow_origins` before deploying (optional) |
| `frontend/config.js` | Backend URL if not running on `127.0.0.1:8000` |

## 10. Deployment (later)
- Backend → Render or Railway (set the same env vars / edit `database.py` to
  point at your cloud MySQL instance).
- Database → any managed MySQL (PlanetScale, Railway MySQL, AWS RDS, etc.).
- Frontend → Vercel or Netlify (just update `config.js` to your deployed
  backend URL first).
