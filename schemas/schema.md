# Time Travel Database Schema

Here is the relational database graph representing the structure of `time_travel.db`, showing how the central `Booking` table acts as the hub connecting all surrounding tables.

```mermaid
erDiagram
    Customer ||--o{ Booking : places
    Customer ||--o{ Payments : makes
    Packages ||--o{ Booking : selected_in
    Timeline ||--o{ Booking : destination_of
    MinuteMen ||--o{ Booking : monitors
    Booking ||--o| Identities : generates
    Booking ||--o{ Payments : settled_by
    Booking ||--o{ Trip_Violations : incurs
    Violations ||--o{ Trip_Violations : catalogued_in
    Booking }|--|{ Languages : uses_skills_from

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
        TEXT booking_languages "Stores comma-separated language IDs"
        INTEGER fame_level
        TIMESTAMP booking_date
    }
```

*Note: For the full attribute details of all tables, please refer to the Entity-Relationship Diagram (`erd.md`) and the project report (`report-time-travel.md`).*
