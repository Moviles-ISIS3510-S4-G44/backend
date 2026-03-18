# Marketplace Andes Analytics

---

## 1. Marketplace Health

### 1.1 GMV (Gross Merchandise Value)

Definition

Total value of completed transactions **over a given period**.

Formula

```sql
GMV = SUM(transactions.price WHERE status = 'completed')
```

---

### 1.2 Conversion Rate (Listing Sale)

Definition

Percentage of listings that result in a completed sale.

Formula

```sql
Conversion Rate = (# of sold listings) / (# of total listings)
```

---

### 1.3 Average Time to Sell

Definition
Average time between listing creation and completed sale.

Formula

```sql
AVG(transactions.created_at - listings.created_at)
```

---

### 1.4 Active Listings per Day

Definition

Number of listings active on each day.

Logic

A listing is active if:

```sql
status = 'active'
OR (created_at <= day AND not sold before day)
```

---

## 2. User Behavior

### 2.1 DAU / MAU

Definition

* DAU: Daily Active Users
* MAU: Monthly Active Users

Logic
Count distinct users performing any action:

* login
* message
* listing creation
* transaction

Formula

```sql
DAU = COUNT(DISTINCT user_id WHERE activity_date = today)
MAU = COUNT(DISTINCT user_id WHERE activity_date within 30 days)
```

---

### 2.2 Listings per User

Definition

Average number of listings created per user.

Formula

```sql
AVG(listings per user)
```

---

### 2.3 Buyer vs Seller Ratio

Definition

Ratio of users who buy vs users who sell.

Formula

```sql
buyers = COUNT(DISTINCT transactions.buyer_id)
sellers = COUNT(DISTINCT listings.seller_id)

ratio = buyers / sellers
```

---

## 3. Supply vs Demand

### 3.1 Listings Created vs Sold per Category

Definition

Tracks supply (created) vs demand (sold).

Formula

```sql
created = COUNT(listings WHERE category = X)
sold = COUNT(transactions JOIN listings WHERE category = X)
```

---

### 3.2 Most Searched Categories

Definition

Top categories based on user searches.

**Note**
Requires search logging.

---

### 3.3 Price Distribution

Definition

Distribution of listing prices per category.

Metrics

* min price
* max price
* median
* percentiles (p50, p75, p90)

---

## 4. Trust & Quality

### 4.1 Average Rating per Seller

Definition

Average review score per seller.

Formula

```sql
AVG(reviews.rating GROUP BY reviewee_id)
```

---

## 4.2 Fraud Signals

### Cancel Rate

**Definition**
Percentage of transactions that are cancelled.

```sql
cancel_rate = cancelled_transactions / total_transactions
```

---

### Message-to-Sale Ratio

Definition

Number of messages required to complete a sale.

Formula

```sql
messages_per_sale = COUNT(messages) / COUNT(completed transactions)
```

## Star Schema

### Dims

```sql
CREATE TABLE dim_user (
    user_id UUID,
    university_id UUID,
    created_date DATE,
    is_verified BOOLEAN
);

CREATE TABLE dim_university (
    university_id UUID,
    name TEXT,
    country TEXT,
    city TEXT
);

CREATE TABLE dim_listing (
    listing_id UUID,
    category TEXT,
    condition TEXT,
    created_date DATE
);

CREATE TABLE dim_date (
    date DATE PRIMARY KEY,
    year INT,
    month INT,
    day INT,
    weekday INT
);
```

### Facts

```sql
CREATE TABLE fact_listings (
    listing_id UUID,
    seller_id UUID,
    created_date DATE,
    price NUMERIC,
    status TEXT
);

CREATE TABLE fact_transactions (
    transaction_id UUID,
    listing_id UUID,
    buyer_id UUID,
    seller_id UUID,
    transaction_date DATE,
    price NUMERIC,
    status TEXT
);

CREATE TABLE fact_engagement (
    id UUID,
    listing_id UUID,
    user_id UUID,
    event_type TEXT,
    event_date DATE
);
```
