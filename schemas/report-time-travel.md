# LevarT — Time Travel Booking Platform
### Project Technical Report
**Course:** MSC2 — Technologies and Architecture  
**Date:** March 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Application Structure — Streamlit Front-End](#4-application-structure--streamlit-front-end)
   - 4.1 [Booking Flow](#41-booking-flow)
   - 4.2 [Pricing Engine](#42-pricing-engine)
   - 4.3 [Database Write Sequence](#43-database-write-sequence)
   - 4.4 [Analytics Dashboard](#44-analytics-dashboard)
5. [Database Design — ERD & UML](#5-database-design--erd--uml)
   - 5.1 [Entity-Relationship Diagram (ERD)](#51-entity-relationship-diagram-erd)
   - 5.2 [Relationship Summary (UML Perspective)](#52-relationship-summary-uml-perspective)
6. [Entity Descriptions](#6-entity-descriptions)
   - 6.1 [Booking — Central Transaction Hub](#61-booking--central-transaction-hub)
   - 6.2 [Customer — Traveler Identity](#62-customer--traveler-identity)
   - 6.3 [Packages — Service Tiers](#63-packages--service-tiers)
   - 6.4 [Timeline — Temporal Destinations](#64-timeline--temporal-destinations)
   - 6.5 [MinuteMen — Oversight Agents](#65-minutemen--oversight-agents)
   - 6.6 [Identities — Timeline Aliases](#66-identities--timeline-aliases)
   - 6.7 [Payments — Financial Transactions](#67-payments--financial-transactions)
   - 6.8 [Languages — Historical Language Catalog](#68-languages--historical-language-catalog)
   - 6.9 [Violations & Trip_Violations — Compliance Rulebook](#69-violations--trip_violations--compliance-rulebook)
7. [Key Design Decisions](#7-key-design-decisions)
8. [Deployment & Configuration](#8-deployment--configuration)

---

## 1. Project Overview

**LevarT** (a reverse of *Travel*) is a fictional time-travel tourism platform built as a university project for the MSC2 — Technologies and Architecture course. The premise is that a company named **TimeCorp** offers customers the ability to travel to historical eras through a technology that creates a controlled, pruned copy of the target timeline. The platform manages the entire commercial lifecycle: customer registration, trip configuration, pricing, legal compliance, payment processing, and operational analytics.

The project demonstrates the integration of a relational database backend with a full Python web application, covering concepts such as database normalisation, foreign key relationships, dual-database portability (SQLite/PostgreSQL), and live data visualisation.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Front-End / UI** | Python · Streamlit | Interactive web application, booking form, analytics dashboard |
| **Data Manipulation** | Pandas | SQL query results → DataFrames for display and charts |
| **Visualisation** | Plotly Express | Interactive charts (line, bar) inside the analytics tab |
| **Identity Generation** | Faker | Generates random realistic alias names for traveler identities |
| **Local Database** | SQLite (`time_travel.db`) | Development and offline mode |
| **Cloud Database** | PostgreSQL via Supabase | Production hosting with persistent cloud storage |
| **DB Connector (Cloud)** | psycopg2 | Python adapter for PostgreSQL |
| **Environment Config** | python-dotenv | Loads `SUPABASE_DB_URL` from `.env` at runtime |
| **Schema Migration** | SQL (`supabase_migration.sql`) | Creates all tables and seeds reference data on Supabase |

**Dependencies** (`requirements.txt`):
```
streamlit
pandas
plotly
faker
psycopg2-binary
python-dotenv
sqlalchemy
```

---

## 3. System Architecture

The application follows a **hub-and-spoke architecture** centred on a single transaction table (`Booking`) that links all surrounding reference tables. The connection layer is abstracted by a single `get_connection()` function that checks for a `SUPABASE_DB_URL` environment variable and routes accordingly:

```
┌──────────────────────────────────────────────────────┐
│               Streamlit Web Application               │
│         (streamlit_app.py — 959 lines)                │
└───────────────────────┬──────────────────────────────┘
                        │
           get_connection() — chooses backend
                        │
        ┌───────────────┴───────────────┐
        │                               │
   SQLite (local)              PostgreSQL / Supabase
   time_travel.db              (via psycopg2 + SUPABASE_DB_URL)
```

Placeholder tokens (`PL`, `T_VAL`, `F_VAL`) are set at startup and adapt all SQL queries automatically to the connected database's syntax (`?` vs `%s`, `1/0` vs `TRUE/FALSE`). This means the same Python codebase runs on both databases with no changes.

---

## 4. Application Structure — Streamlit Front-End

The application is divided into two main tabs: **Book a Trip** and **Analytics**. The sidebar displays a short description of the currently selected package.

### 4.1 Booking Flow

The booking form is structured as a top-to-bottom guided wizard composed of the following sections:

| Section | UI Element | Description |
|---|---|---|
| **Traveler Identity** | Text inputs, date picker, selectbox | Collects real name, birthdate, email, sex, country, phone |
| **Package Selection** | Selectbox (3 options) | Peasant Package, Quantum Query, Monarch Mode |
| **Identity & Status** | Selectbox (1–5) | Fame level (only shown for non-Peasant packages) |
| **Duration** | Slider + number input (synced) | Trip duration in minutes (1–2880) |
| **Timeline** | Selectbox (25 eras + custom) | Historical destination; custom year entry if "Personalized" |
| **Spawn Country** | Selectbox (all world nations) | Country of temporal materialisation |
| **Languages** | Multiselect + custom text input | 104 predefined languages; custom entries accepted |
| **Add-ons** | Two checkboxes | Insurance Protection (+$200), Memory Reset (+$100) |
| **Payment Details** | Two selectboxes | Currency (9 options including BTC and ChronoCredits); Payment method |
| **Invoice** | Computed display | Real-time cost breakdown before confirmation |
| **Confirm Booking** | Button | Triggers full database write sequence |

### 4.2 Pricing Engine

The total price is computed in USD using the following formula, then converted to the chosen currency:

```
base_price      = minutes × package_rate_per_minute
fame_extra      = base_price × (fame_level × 0.20)
language_cost   = $50 × number_of_languages  (Quantum Query only; free for Monarch Mode)
insurance_cost  = $200  (if selected)
memory_cost     = $100  (if selected)
─────────────────────────────────────────────────────
total_price (USD) = base_price + fame_extra + language_cost + insurance_cost + memory_cost
converted_price   = total_price × CURRENCY_RATE[selected_currency]
```

Nine currency conversion rates are applied (USD, EUR, GBP, JPY, CNY, CHF, BTC, ETH, ChronoCredits).

### 4.3 Database Write Sequence

When the user clicks **Confirm Booking**, the application executes these steps in a single database transaction:

1. **Check for returning customer** — looks up the email in `Customer`; reuses the existing `customer_id` if found, otherwise inserts a new row.
2. **Insert Timeline** — creates a new `Timeline` row with the selected era label and spawn country.
3. **Resolve Package** — queries `Packages` by description to retrieve the `package_id`.
4. **Assign MinuteMen** — fetches all agents from `MinuteMen` and picks one at random.
5. **Process Languages** — for each selected language, inserts it into `Languages` if it does not already exist, then collects all `language_id` values into a comma-separated string.
6. **Insert Booking** — inserts the central `Booking` row with all foreign keys and trip attributes.
7. **Generate Identity** (non-Peasant only) — uses Faker to generate a sex-matched alias (`first_name`, `last_name`) and inserts it into `Identities` linked to the new `booking_id`.
8. **Insert Payment** — records the converted amount, currency, and payment method into `Payments`.
9. **Commit** — saves all changes atomically; displays a success banner with the alias name and assigned agent.

### 4.4 Analytics Dashboard

The second tab displays a live, read-only view of the booking database through seven visualisations:

| # | Chart | Query Source |
|---|---|---|
| KPIs | Total Bookings, Total Revenue, Unique Travelers, Avg Trip (min) | `Booking`, `Customer` |
| 1 | Chronological Timeline of Trips (log-scale line chart) | `Booking` JOIN `Timeline` |
| 2 | Revenue by Package (bar chart) | `Booking` JOIN `Packages` |
| 3 | Traveler Gender Split (bar chart) | `Customer` |
| 4 | MinuteMen Deployments (bar chart) | `Booking` JOIN `MinuteMen` |
| 5 | Add-ons Combinations (bar chart) | `Booking` (boolean flags) |
| 6 | Fame Level Distribution (bar chart) | `Booking` (fame_level > 0) |
| 7 | Crimes & Violations (bar chart) | `Trip_Violations` JOIN `Violations` |

The timeline chart uses a logarithmic x-axis reversed so that the Dinosaurs Era (−65,000,000) appears correctly alongside modern eras without distortion.

---

## 5. Database Design — ERD & UML

### 5.1 Entity-Relationship Diagram (ERD)

The following diagram uses standard crow's foot notation to represent all entities, their attributes with data types, primary keys (PK), foreign keys (FK), and cardinalities.

```mermaid
erDiagram
    Customer ||--o{ Booking : "places (1:N)"
    Customer ||--o{ Payments : "makes (1:N)"
    Packages ||--o{ Booking : "selected_in (1:N)"
    Timeline ||--o{ Booking : "destination_of (1:N)"
    MinuteMen ||--o{ Booking : "monitors (1:N)"
    Booking ||--o| Identities : "generates (1:1)"
    Booking ||--o{ Payments : "settled_by (1:N)"
    Booking ||--o{ Trip_Violations : "incurs (1:N)"
    Violations ||--o{ Trip_Violations : "catalogued_in (1:N)"

    Customer {
        INTEGER customer_id PK
        TEXT first_name
        TEXT last_name
        TEXT phone_num
        TEXT address
        TEXT birthdate
        TEXT email
        TEXT sex
    }

    Packages {
        INTEGER package_id PK
        TEXT description
        REAL package_rate
    }

    Timeline {
        INTEGER timeline_id PK
        TEXT timeline_year
        TEXT map
    }

    MinuteMen {
        INTEGER agent_id PK
        TEXT badge_number
        TEXT agent_name
    }

    Booking {
        INTEGER booking_id PK
        INTEGER customer_id FK
        INTEGER package_id FK
        INTEGER timeline_id FK
        INTEGER agent_id FK
        TEXT spawn_country
        INTEGER minutes
        BOOLEAN insurance
        BOOLEAN memory_reset
        REAL total_price
        TEXT booking_languages
        INTEGER fame_level
        TIMESTAMP booking_date
    }

    Identities {
        INTEGER identity_id PK
        INTEGER booking_id FK
        TEXT first_name
        TEXT last_name
        TEXT sex
        INTEGER fame_level
    }

    Payments {
        INTEGER payment_id PK
        INTEGER customer_id FK
        INTEGER booking_id FK
        REAL amount
        TEXT currency
        TEXT method
    }

    Languages {
        INTEGER language_id PK
        TEXT language_name
    }

    Violations {
        INTEGER violation_id PK
        TEXT crime
        TEXT penalty_description
        REAL fine_amount
    }

    Trip_Violations {
        INTEGER trip_violation_id PK
        INTEGER booking_id FK
        INTEGER violation_id FK
        TIMESTAMP occurrence_date
    }
```

#### Cardinality Legend

| Notation | Meaning |
|---|---|
| `\|\|--o{` | **One-to-Many**: one parent row can relate to zero or many child rows |
| `\|\|--o\|` | **One-to-One (optional)**: one parent row can relate to zero or one child row |
| `PK` | Primary Key — unique identifier for the row |
| `FK` | Foreign Key — reference to another table's Primary Key |

### 5.2 Relationship Summary (UML Perspective)

From a UML class diagram perspective, each table is a class with typed attributes. The associations and their multiplicities are:

| Association | Multiplicity | Description |
|---|---|---|
| `Customer` → `Booking` | 1 to 0..* | A customer can book zero or many trips |
| `Customer` → `Payments` | 1 to 0..* | A customer can make zero or many payments |
| `Packages` → `Booking` | 1 to 0..* | A package can appear in zero or many bookings |
| `Timeline` → `Booking` | 1 to 0..* | A timeline era can be used for zero or many bookings |
| `MinuteMen` → `Booking` | 1 to 0..* | An agent can be assigned to zero or many bookings |
| `Booking` → `Identities` | 1 to 0..1 | A booking generates at most one alias identity |
| `Booking` → `Payments` | 1 to 1 | Each booking has exactly one associated payment |
| `Booking` ↔ `Violations` | M to N (via `Trip_Violations`) | A trip can have multiple violations; a violation type can appear on many trips |

---

## 6. Entity Descriptions

### 6.1 Booking — Central Transaction Hub

The `Booking` table is the analytical core of the database. Every time a customer purchases a trip, a single row is inserted here, recording the full context of that transaction. Rather than storing names, descriptions, and labels directly, the table stores foreign key integers that point to dedicated reference tables, eliminating redundancy. Its own columns store attributes that are unique to each individual trip: `minutes` (the duration of the stay), `spawn_country` (the country of temporal arrival), `fame_level` (a social-influence tier from 1 to 5 purchased for that specific trip), `booking_languages` (a comma-separated list of language IDs chosen by the traveler), two boolean flags (`insurance` and `memory_reset`) representing purchasable add-ons, and a `total_price` computed at the time of booking. The `booking_date` timestamp is automatically populated on insert, providing an immutable audit record.

### 6.2 Customer — Traveler Identity

The `Customer` table stores the real-world legal and biological identity of every registered traveler. Each row identifies a unique individual through their `first_name`, `last_name`, `email`, `phone_num`, `address`, `birthdate`, and `sex`. The `customer_id` primary key is referenced by both the `Booking` and `Payments` tables, making the customer the root entity from which all financial and transactional activity originates. Email is used as the deduplication key: if a returning customer books a second trip, the application reuses their existing `customer_id` rather than creating a duplicate row. The deliberate separation of this table from the `Identities` table is a security design choice — the real identity of the traveler is never stored alongside their timeline alias.

### 6.3 Packages — Service Tiers

The `Packages` table is a reference catalog that defines the three commercial tiers of time travel available to customers: *Peasant Package* (basic observation mode, $10/min), *Quantum Query* (interaction mode with purchased language abilities, $20/min), and *Monarch Mode* (full immersion with return item privilege and all languages included, $50/min). Each row contains a `description` field (enforced as unique) and a `package_rate` expressed in USD per minute. Storing these tiers in a dedicated table means that a price adjustment requires only a single row update, and all historical booking records remain untouched while the current rate is instantly corrected across the system.

### 6.4 Timeline — Temporal Destinations

The `Timeline` table stores the available historical eras to which customers can travel. Each record holds a human-readable `timeline_year` label (e.g., *Roman Empire (100)*, *World War II (1940)*) alongside a `map` field containing the spawn country or numeric year representation as a string. The application offers 24 predefined historical destinations — from the Dinosaurs Era (−65,000,000) to the Fall of the Berlin Wall (1989) — plus a custom option where the traveler can enter any year. Each booking creates its own `Timeline` row (with the chosen era label and spawn country), allowing the analytics dashboard to group and count trips per destination accurately.

### 6.5 MinuteMen — Oversight Agents

The `MinuteMen` table contains the roster of TimeCorp's 10 authorised temporal oversight agents (e.g., *Agent K*, badge `MM-001`; *Agent Weaver*, badge `MM-009`). Each agent is identified by a unique `badge_number` and an `agent_name`. When a booking is created, one agent is randomly selected by the application from this table and linked via the `agent_id` foreign key in `Booking`. Isolating agents in their own table ensures that any update to an agent's name or badge is applied in one place and automatically reflected across every associated booking record — a direct benefit of relational normalisation. The analytics dashboard charts agent deployment frequency, showing how evenly trips are distributed across the team.

### 6.6 Identities — Timeline Aliases

The `Identities` table stores the historically blending aliases generated for travelers who purchase the *Quantum Query* or *Monarch Mode* packages. Each record contains a fictional `first_name`, `last_name`, and `sex`, along with the `fame_level` that was active during that booking. The alias is generated at booking time by the Python *Faker* library, which produces a realistic, sex-matched name. The table is linked directly to a specific `Booking` record (via `booking_id` FK) rather than to the `Customer`, because a single customer taking multiple trips requires a completely different alias for each journey. This one-to-one optional relationship means a record only exists when the business logic requires it — *Peasant Package* travelers, who travel in ghost mode, receive no alias and generate no row here.

### 6.7 Payments — Financial Transactions

The `Payments` table records the financial transaction associated with each booking. Each row stores the `amount` paid (in the customer's chosen currency after conversion), the `currency` code (e.g., `USD`, `BTC`, `CC` for ChronoCredits), and the payment `method` (e.g., Visa, MasterCard, Cash). It is linked to the `Customer` table via `customer_id` and to the `Booking` table via `booking_id`, providing a complete audit trail that connects a specific monetary event back to both the payer and the trip it settled. Nine currencies are supported, including two cryptocurrencies and a fictional currency (ChronoCredits).

### 6.8 Languages — Historical Language Catalog

The `Languages` table is a standalone reference catalog of 104 historical and modern languages, spanning from *Sumerian* and *Akkadian* (the oldest recorded written languages) to *Classical Chinese*, *Modern English*, and *Chuvash*. It is queried exclusively by the application's front-end to populate a multi-select dropdown during the booking process. Travellers purchasing *Quantum Query* pay $50 per language; *Monarch Mode* travellers receive all languages at no extra cost. The selected combination is serialised as a comma-separated string of `language_id` integers and stored in the `booking_languages` field of `Booking`. Custom languages typed by the customer are inserted into this table automatically (using `INSERT OR IGNORE` / `ON CONFLICT DO NOTHING`) before being linked to the booking.

### 6.9 Violations & Trip_Violations — Compliance Rulebook

The `Violations` table acts as a read-only legal rulebook defining prohibited acts in the timeline, each with a `crime` label (unique), a `penalty_description`, and a `fine_amount` in USD. Currently it defines four offences: Murder ($5,000), Genocide ($50,000), Enslavement ($15,000), and Rape/Sexual Misconduct ($10,000). The table is a reference catalog; it does not actively participate in any transaction until an infraction is detected by a MinuteMen agent.

The `Trip_Violations` table resolves the many-to-many relationship between bookings and violations. When a traveler commits a prohibited act, a record is inserted into `Trip_Violations` referencing both the `booking_id` and the `violation_id`, with an automatic `occurrence_date` timestamp. This design allows a single trip to accumulate multiple violations and a single violation type to be applied across many different bookings without any data duplication. The analytics dashboard renders a bar chart of violation frequency to monitor timeline integrity.

---

## 7. Key Design Decisions

**Normalisation over convenience.** The decision to split data across 10 separate tables (rather than one large flat table) was intentional. It enforces the Third Normal Form (3NF): every non-key attribute depends only on the primary key of its own table. This prevents update anomalies — for example, changing a package price or an agent name requires updating exactly one row in one table.

**Hub-and-spoke around `Booking`.** The `Booking` table acts as the single transaction record; all contextual data (who, what package, which era, which agent) is stored by reference, not by value. This keeps the `Booking` table lean and all reference tables authoritative.

**Dual-database portability.** The application runs identically on SQLite (local development) and PostgreSQL (Supabase cloud). The `get_connection()` function, combined with adaptive placeholder tokens (`PL`, `T_VAL`, `F_VAL`), abstracts away syntax differences. This was designed to allow fast local development with zero cloud cost, and a clean migration path to production.

**Customer deduplication by email.** Rather than always inserting a new customer row, the app checks for an existing email first. This prevents duplicate customer records across multiple bookings and preserves correct revenue attribution in the analytics.

**Languages as a serialised string.** The `booking_languages` column stores a comma-separated list of `language_id` integers rather than a separate junction table. This is a deliberate trade-off: it simplifies the booking insertion transaction and reduces join complexity in the analytics queries, at the cost of not being able to query "all bookings that included Latin" with a single SQL clause. A full junction table (`Booking_Languages`) would be the fully normalised alternative.

**`Trip_Violations` as a proper junction table.** Unlike languages, violations are handled with a proper many-to-many junction table (`Trip_Violations`) because the compliance use-case requires querying and aggregating violation counts by type — a functionality directly surfaced in the analytics dashboard.

---

## 8. Deployment & Configuration

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application (SQLite mode — no configuration needed)
streamlit run streamlit_app.py
```

### Cloud Deployment (Supabase)

1. Create a project on [Supabase](https://supabase.com).
2. Copy the connection string from **Project Settings → Database → Connection String (URI)**.
3. Create a `.env` file (from `.env.example`) and set:
   ```
   SUPABASE_DB_URL=postgresql://postgres.xxxxxx:password@aws-0-eu-central-1.pooler.supabase.com:5432/postgres
   ```
4. Run the migration script in the Supabase SQL Editor:
   ```
   sql/supabase_migration.sql
   ```
   This drops and recreates all tables and seeds all reference data (Packages, Languages, MinuteMen, Violations).
5. Start the application — it will automatically detect `SUPABASE_DB_URL` and connect to PostgreSQL.

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUPABASE_DB_URL` | Cloud only | Full PostgreSQL connection URI from Supabase |

If `SUPABASE_DB_URL` is not set, the application falls back silently to the local `time_travel.db` SQLite file.

---

*End of Report*
