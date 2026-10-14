# PostgreSQL Setup & Administration Guide (`psql.md`)

This guide explains how to connect to, configure, and administer the **PostgreSQL database** for the `aibin-backend` service and TrafficVision AI ecosystem on Windows.

---

## 📑 Table of Contents

1. [Master Database Configuration & Credentials](#1-master-database-configuration--credentials)
2. [Connecting via `psql` Interactive Terminal](#2-connecting-via-psql-interactive-terminal)
3. [Running SQL Schema Files](#3-running-sql-schema-files)
4. [Essential Inspection Commands](#4-essential-inspection-commands)
5. [Useful SQL Management Queries](#5-useful-sql-management-queries)
6. [Troubleshooting Connection Issues](#6-troubleshooting-connection-issues)

---

## 🔑 1. Master Database Configuration & Credentials

The entire TrafficVision AI project is configured with the following credentials in `.env`:

| Parameter | Value | Notes |
|---|---|---|
| **Host** | `127.0.0.1` (or `localhost`) | Local loopback address |
| **Port** | `5432` | Standard PostgreSQL port |
| **Database** | `postgres` | Primary project database |
| **User** | `postgres` | Superuser administrative account |
| **Password** | **`A`** | Configured across all project `.env` files |
| **Connection URL** | `postgresql://postgres:A@127.0.0.1:5432/postgres` | Used by SQLAlchemy ORM |

---

## 💻 2. Connecting via `psql` Interactive Terminal

### Step 1: Open PowerShell
Open Windows PowerShell and ensure PostgreSQL `bin` directory is accessible:

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin;C:\Program Files\PostgreSQL\16\bin"
```

### Step 2: Launch `psql`
```powershell
psql -U postgres -d postgres -h 127.0.0.1 -p 5432
```
When prompted for **Password for user postgres:**, enter:
👉 **`A`**

---

## 📜 3. Running SQL Schema Files

### Run Authentication & RBAC Schema (Intern 1):
```powershell
cd "c:\Users\AIBIN SHIBU\OneDrive\Documents\trafficvision"
psql -U postgres -d postgres -h 127.0.0.1 -p 5432 -f "aibin-backend\database\schema.sql"
```

### Run Traffic Monitoring Schema (Intern 2):
```powershell
psql -U postgres -d postgres -h 127.0.0.1 -p 5432 -f "anmol-data\Database\schema.sql"
```

### Run Inside an Active `psql` Session:
```sql
\i 'C:/Users/AIBIN SHIBU/OneDrive/Documents/trafficvision/aibin-backend/database/schema.sql'
```

---

## 🔍 4. Essential Inspection Commands

Once connected inside the `psql` prompt:

| Command | Action |
|---|---|
| `\dt` | List all tables in the current database |
| `\dt public.*` | List all tables in the public schema |
| `\d users` | Inspect structure, data types, and indexes of `users` table |
| `\d roles` | Inspect structure of `roles` table |
| `\d user_sessions` | Inspect structure of `user_sessions` table |
| `\d+ users` | Show detailed table information including foreign keys |
| `\du` | List all PostgreSQL users and roles |
| `\l` | List all databases on this PostgreSQL server |
| `\conninfo` | Display current connection details |
| `\q` | Exit `psql` and return to PowerShell |

---

## 📊 5. Useful SQL Management Queries

### View All Registered Users:
```sql
SELECT id, name, email, role, created_at FROM users;
```

### View All Roles:
```sql
SELECT * FROM roles;
```

### View Active User Sessions / Refresh Tokens:
```sql
SELECT * FROM user_sessions;
```

### Find a Specific User:
```sql
SELECT * FROM users WHERE email = 'admin@trafficvision.ai';
```

### Count Total Registered Users:
```sql
SELECT COUNT(*) FROM users;
```

### Promote a User to Admin:
```sql
UPDATE users SET role = 'admin' WHERE email = 'user@example.com';
```

### View Unread Alerts:
```sql
SELECT id, type, severity, road_id, message FROM alerts WHERE read = FALSE;
```

---

## 🛠️ 6. Troubleshooting Connection Issues

### 1. `psql : The term 'psql' is not recognized`
Add PostgreSQL to your PowerShell PATH:
```powershell
$env:Path += ";C:\Program Files\PostgreSQL\17\bin;C:\Program Files\PostgreSQL\16\bin"
```

### 2. `Connection refused (0x0000274D / 10061)`
PostgreSQL service is stopped. Start it with:
```powershell
Start-Service postgresql*
```

### 3. `FATAL: password authentication failed for user "postgres"`
Ensure you typed password **`A`** (case-sensitive). If PostgreSQL was installed with a different password, reset it in `psql` or reinstall via winget with `--superpassword A`.
