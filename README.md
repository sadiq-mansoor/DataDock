# 🗄️ DataDock — Offline Data-Retrieval System

<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/role--based%20access-control-2563EB?style=flat-square" />
  <img src="https://img.shields.io/badge/100%25-offline-16A34A?style=flat-square" />
</p>

**A secure, fully offline system for retrieving all records about a person across scattered
databases and files — with role-based access and a complete audit trail.**

---

## The problem it solves

Organizations often need to pull together everything they hold about an individual — but that data
is spread across PostgreSQL, MySQL, and loose CSV/JSON/XML files, with no unified, auditable way to
search it. Doing this by hand is slow, error-prone, and leaves no compliance record.

**DataDock** is a self-contained application that searches every connected source at once, groups
results by person, masks sensitive fields automatically, and logs every action — all without any
internet connectivity.

---

## Screenshots

<!--
  TODO: add 2–3 screenshots to make this instantly credible. Suggested:
  docs/screenshots/login.png · docs/screenshots/global-search.png · docs/screenshots/audit-log.png
  Then reference them here, e.g.:
  <p align="center"><img src="docs/screenshots/global-search.png" width="80%" alt="Global search" /></p>
-->
*Screenshots coming soon — run locally (below) to see the dashboard, global search, and audit log.*

---

## ✨ Features

**Search & retrieval**
- 🔍 **Global search** across all connected data sources simultaneously
- 👤 **Person-based retrieval** — find every record tied to one individual
- 🧭 **Schema auto-detection** and management per source
- 🕵️ **Sensitive-field masking** — configurable (SSN, credit card, salary, medical, …)

**Security & access control**
- 🔐 **Role-based access:** Super Admin · Admin · User
- 📴 **Fully offline** — no external connectivity required
- 📝 **Immutable audit logging** of every user action, stored locally
- 🔑 **bcrypt** password hashing

**Export & reporting**
- 📤 CSV & PDF export with **provenance tracking** (data lineage per source)
- 🧾 Search-session history

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py          # opens http://localhost:8501
```
> Windows users can just run `run.bat` (or `run.ps1`).

**Demo login:** `admin` / `admin123`

> ⚠️ **Security note:** the default `admin/admin123` credentials exist **only for local demo**.
> Change them before any real deployment — and never enter real sensitive data into a demo instance.

---

## 🧩 Data Sources Supported

| Type | Connect with |
|------|--------------|
| PostgreSQL | host / port / db / user / password |
| MySQL | host / port / db / user / password |
| CSV / JSON / XML | absolute file path |

Add sources from the **Data Sources** page (Admin+); test the connection before saving.

---

## 🏗️ Architecture

```
Frontend (Streamlit)      → login · dashboard · global search · schema mgmt · audit logs · user mgmt
Backend Services          → auth · data-source · search · export · audit
Data Connectors           → SQL (PostgreSQL/MySQL) · File (CSV/JSON/XML) · base connector interface
Database Layer            → SQLite (app metadata) + external data sources
```

```
app.py                 # entry point
config.py              # settings + SENSITIVE_FIELDS
database/              # connection + models (SQLite metadata)
data_connectors/       # base · factory · sql_connector · file_connector
services/              # data_source · search · export
utils/                 # auth · audit
pages/                 # login · dashboard
test_installation.py   # environment self-check
```

---

## 🔒 Security model

| Role | Capabilities |
|------|--------------|
| **Super Admin** | Full access — user & data-source management |
| **Admin** | Data-source management, audit-log access |
| **User** | Search & export only |

All actions are written to an immutable local audit log with timestamps and user identity; sensitive
fields are filtered before results are ever displayed or exported.

---

## 🧪 Verify your setup

```bash
python test_installation.py   # checks dependencies + directory structure
```

## 📦 Requirements

Python 3.10+ · 4 GB RAM (8 GB recommended) · Windows 10/11 (SQLite bundled; no server needed for app metadata).
