# Marketplace Andes App Database Model

This document proposes the transactional database model for the marketplace application, using the current backend in `src/marketplace_andes_backend` as the starting point.

## Context

- The current backend already defines a minimal `User` model with `id`, `name`, `email`, and `rating`.
- The current app wiring only exposes `users` routes; marketplace domains such as listings and transactions are still missing.
- This model extends the current structure into a university-focused marketplace for students selling physical items and digital materials such as notes.

## Core assumptions

- Each listing has one seller.
- Buyers purchase listings directly; no auction model is included.
- Listings may represent physical goods or digital goods.
- Listing condition is limited to `new`, `used`, and `refurbished`.
- Analytics requirements imply operational tables for messages, searches, reviews, listing lifecycle, and user activity.

## Proposed transactional ER model

```mermaid
erDiagram
    UNIVERSITY {
        int id PK
        string name
        string country
        string city
        datetime created_at
    }

    PROGRAM {
        int id PK
        int university_id FK
        string name
        string faculty
        datetime created_at
    }

    USER {
        int id PK
        int university_id FK
        int program_id FK
        string name
        string email UK
        int rating
        boolean is_verified
        string student_code
        datetime created_at
        datetime last_login_at
    }

    CATEGORY {
        int id PK
        int parent_category_id FK
        string name
        string slug UK
        boolean is_active
        datetime created_at
    }

    LISTING {
        int id PK
        int seller_id FK
        int category_id FK
        string title
        string description
        string product_type
        string condition
        decimal price
        string currency
        string status
        boolean is_negotiable
        boolean is_digital
        int quantity_available
        string campus_pickup_point
        datetime created_at
        datetime published_at
        datetime sold_at
        datetime archived_at
    }

    LISTING_MEDIA {
        int id PK
        int listing_id FK
        string asset_url
        string media_type
        int sort_order
        datetime created_at
    }

    LISTING_STATUS_HISTORY {
        int id PK
        int listing_id FK
        int changed_by_user_id FK
        string from_status
        string to_status
        datetime changed_at
    }

    TRANSACTION {
        int id PK
        int listing_id FK
        int buyer_id FK
        int seller_id FK
        decimal listed_price
        decimal agreed_price
        string currency
        string status
        datetime created_at
        datetime completed_at
        datetime cancelled_at
    }

    MESSAGE_THREAD {
        int id PK
        int listing_id FK
        int buyer_id FK
        int seller_id FK
        datetime created_at
        datetime last_message_at
    }

    MESSAGE {
        int id PK
        int thread_id FK
        int sender_id FK
        string body
        boolean is_read
        datetime created_at
    }

    REVIEW {
        int id PK
        int transaction_id FK
        int reviewer_id FK
        int reviewee_id FK
        int rating
        string comment
        datetime created_at
    }

    SEARCH_EVENT {
        int id PK
        int user_id FK
        int category_id FK
        string query_text
        string sort_mode
        int results_count
        datetime created_at
    }

    USER_ACTIVITY_EVENT {
        int id PK
        int user_id FK
        int listing_id FK
        int transaction_id FK
        string event_type
        datetime created_at
    }

    UNIVERSITY ||--o{ PROGRAM : offers
    UNIVERSITY ||--o{ USER : enrolls
    PROGRAM ||--o{ USER : groups

    CATEGORY ||--o{ CATEGORY : parent_of
    CATEGORY ||--o{ LISTING : classifies
    CATEGORY ||--o{ SEARCH_EVENT : filters

    USER ||--o{ LISTING : sells
    USER ||--o{ TRANSACTION : buys
    USER ||--o{ TRANSACTION : fulfills
    USER ||--o{ MESSAGE_THREAD : starts
    USER ||--o{ MESSAGE : sends
    USER ||--o{ REVIEW : writes
    USER ||--o{ REVIEW : receives
    USER ||--o{ SEARCH_EVENT : searches
    USER ||--o{ USER_ACTIVITY_EVENT : performs
    USER ||--o{ LISTING_STATUS_HISTORY : updates

    LISTING ||--o{ LISTING_MEDIA : has
    LISTING ||--o{ LISTING_STATUS_HISTORY : changes
    LISTING ||--o| TRANSACTION : converts_to
    LISTING ||--o{ MESSAGE_THREAD : discussed_in
    LISTING ||--o{ USER_ACTIVITY_EVENT : triggers

    MESSAGE_THREAD ||--o{ MESSAGE : contains
    TRANSACTION ||--o{ REVIEW : receives
    TRANSACTION ||--o{ USER_ACTIVITY_EVENT : generates
```

## Entity responsibilities

- `USER`
  - Reuses the current backend user concept.
  - Adds university context and verification fields needed for trust and analytics.
- `UNIVERSITY` and `PROGRAM`
  - Support a student-centered marketplace and enable analytical cuts by campus or program.
- `CATEGORY`
  - Supports supply/demand and search analytics, with optional hierarchy.
- `LISTING`
  - Central sellable entity for items, notes, and other student offerings.
  - Stores listing condition, lifecycle timestamps, and commercial attributes.
- `LISTING_MEDIA`
  - Supports multiple photos or digital asset previews per listing.
- `LISTING_STATUS_HISTORY`
  - Preserves lifecycle events required for active listing calculations and operational auditing.
- `TRANSACTION`
  - Represents the conversion of a listing into an order or sale, including cancellation/completion timestamps.
- `MESSAGE_THREAD` and `MESSAGE`
  - Support buyer-seller conversations and the message-to-sale metric.
- `REVIEW`
  - Supports seller trust and quality analytics.
- `SEARCH_EVENT`
  - Required for most searched categories.
- `USER_ACTIVITY_EVENT`
  - Required for DAU/MAU and broader engagement analytics.

## Notes for implementation in the current backend

- The current codebase only implements `users`, so all marketplace tables except `USER` are proposed additions.
- `TRANSACTION` is named as a business entity here; if it conflicts with framework or database conventions, use a concrete table name such as `marketplace_transaction` or `orders` in implementation.
- `LISTING.sold_at` should be derived from the completed sale event or updated transaction status.
- `USER_ACTIVITY_EVENT.event_type` should at minimum cover `login`, `message`, `listing_created`, and `transaction` to satisfy `docs/ANALYTICS.md`.
