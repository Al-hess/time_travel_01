# Time Travel Database - Entity Relationship Diagram (ERD)

This diagram visualizes the complete database schema natively reflecting the current SQL setup. It displays all entities (tables), their attributes (columns) with data types, primary keys (PK), foreign keys (FK), and the cardinal relationships (one-to-many, one-to-one) between them.

```mermaid
erDiagram
    Customer ||--o{ Booking : "places (1:N)"
    Customer ||--o{ Payments : "makes (1:N)"
    Customer ||--o{ Identities : "has (1:1)"
    Customer ||--o{ Languages : "speaks (1:N)"
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

### Cardinality Legend:
*   `||--o{` : **One-to-Many**. (e.g., One `Customer` can have zero or many `Bookings`).
*   `||--o|` : **One-to-One / Zero-to-One**. (e.g., One `Booking` can optionally generate one `Identity`).
*   `PK` : Primary Key (Unique identifier for the row).
*   `FK` : Foreign Key (Reference to another table's Primary Key).
