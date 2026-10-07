# 🤖 Intelligent Analytics Query Engine

## What is your project actually?

Your project is an:

> **Intelligent Analytics Query Engine**

In simple words:

### It allows a person to ask questions about business data in normal English, and the system automatically understands the question, creates the required analytical query, executes it, and gives the answer.

Instead of the user needing to know SQL, they can simply ask:

> **"Total sales in India for March?"**

Your system converts that into an analytical SQL query, runs it against the sales database, and returns:

> **₹108 revenue**

---

# 🧠 Think of it like ChatGPT for business data

Imagine a company has thousands or millions of sales records.

Normally, a business analyst might need to write SQL:

```sql
SELECT SUM(quantity * unit_price * (1 - discount))
FROM sales
WHERE country = 'India'
AND order_date BETWEEN ...;
```

But a manager doesn't necessarily know SQL.

So they can simply type:

> "What were our sales in India in March?"

Your system acts as the bridge:

```text
Human
  ↓
"What were our sales in India in March?"
  ↓
Intelligent Analytics Query Engine
  ↓
Understand the question
  ↓
Create analytical logic
  ↓
Generate SQL
  ↓
Execute SQL
  ↓
Get result
  ↓
Explain result to Human
```

That's the **main idea of your project**.

---

# 🔥 Why is this a GenAI project?

The important part is **Natural Language Understanding**.

Humans don't normally ask analytical questions in SQL.

They ask things like:

> "Show me the top 3 customers in every region."

or:

> "Which region failed to reach its target?"

or:

> "How much did each category contribute to sales?"

The system has to understand what the user means.

For example:

### User:

> "Show me the top 3 customers per region."

The system needs to understand:

```text
Metric       → Revenue
Group        → Region + Customer
Ranking      → Top 3
Ranking type → Within each region
```

Which becomes a structured plan such as:

```text
metric = revenue

group_by =
    region
    customer_id

ranking =
    top 3
    within region
```

Then your SQL generator creates the SQL required to answer it.

---

# 🏗️ Your project has multiple layers

Think of your project like a factory.

```text
             USER
              │
              ▼
       Natural Language
              │
              ▼
       ┌───────────────┐
       │  GenAI / NLP  │
       └───────┬───────┘
               │
               ▼
          Query Plan
               │
               ▼
        SQL Generator
               │
               ▼
        SQL Validator
               │
               ▼
            DuckDB
               │
               ▼
          Query Result
               │
               ▼
      Explanation + Confidence
               │
               ▼
             USER
```

Let's understand each one.

---

# 1️⃣ User asks a question

For example:

> **"Top 2 cities by profit"**

The user doesn't need to know:

- SQL
- database structure
- column names
- aggregation functions
- ranking functions

They just ask normally.

---

# 2️⃣ Natural Language Understanding

This is where the **AI/GenAI part** comes in.

The system needs to understand:

> "Top 2 cities by profit"

as:

```text
Metric = profit
Aggregation = sum
Group by = city
Ranking = top 2
```

So conceptually:

```text
"Top 2 cities by profit"
             ↓
      QueryPlan
```

---

# 3️⃣ Query Plan

Your project uses a `QueryPlan`.

It's basically a structured representation of what the user wants.

For example:

```json
{
  "metric": "profit",
  "aggregation": "sum",
  "group_by": ["city"],
  "filters": {},
  "ranking": {
    "direction": "desc",
    "limit": 2
  }
}
```

This is extremely important.

Instead of directly asking AI:

> "Give me SQL."

you're creating an intermediate structured layer.

That's a good system-design decision.

---

# 4️⃣ SQL Generator

Now your system knows what the user wants.

It generates SQL.

For:

> "Top 2 cities by profit"

it can generate SQL conceptually like:

```sql
SELECT
    city,
    SUM(profit) AS sum_profit
FROM sales
GROUP BY city
ORDER BY sum_profit DESC
LIMIT 2;
```

---

# 5️⃣ SQL Validator 🔐

This is a very important security layer.

You **don't want AI-generated SQL to blindly execute**.

Imagine a malicious query somehow generates:

```sql
DROP TABLE sales;
```

That would be dangerous.

So your validator checks things like:

```text
Is this SELECT/WITH?
        ↓
Are the tables allowed?
        ↓
Are dangerous SQL commands present?
        ↓
YES → Execute
NO  → Reject
```

Your system allows analytical queries against:

```text
sales
targets
```

and blocks dangerous operations such as:

```text
DROP
DELETE
UPDATE
INSERT
ALTER
CREATE
TRUNCATE
```

This is something you can mention in an interview.

---

# 6️⃣ DuckDB executes the query

Your project uses **DuckDB** as the analytical database.

Your CSV data is loaded into DuckDB tables:

```text
sales
targets
```

So instead of directly manipulating CSV files every time, your system can execute SQL against the database.

---

# 7️⃣ Result

Suppose the database returns:

```text
city          profit
--------------------
New York      200
San Francisco 180
```

Your system converts that into JSON for the API.

---

# 8️⃣ Confidence Score

Your project also returns:

```json
"confidence_score": 0.9
```

This represents how confidently the system interpreted the query based on the information it extracted.

For example:

```text
0.95 → Very clear query
0.80 → Reasonably clear
0.60 → Some ambiguity
```

Your current implementation calculates this based on how much information the QueryPlan contains.

---

# 9️⃣ Explanation

Your system doesn't just give the number.

It also explains what it understood.

For example:

> "The system interpreted the requested metric as revenue. The query applies the filter country = India. The query is restricted to 2024-03."

This is useful because the user can understand **how the system interpreted their question**.

---

# 📊 What kind of questions can it answer?

Your project is designed for business analytics.

For example:

### Simple aggregation

> "Total sales in India for March"

```text
Revenue = 108
```

---

### Ranking

> "Top 2 cities by profit"

```text
New York       200
San Francisco  180
```

---

### Grouping

> "Average order value by region"

```text
APAC
EMEA
NA
```

with the corresponding AOV.

---

### Target comparison

> "Which region missed its target in February?"

The system compares:

```text
Actual Revenue
       vs
Target Revenue
```

---

### Contribution analysis

> "Sales contribution percentage by category"

It calculates something like:

```text
Technology        88.06%
Furniture          9.44%
Office Supplies    2.50%
```

---

### Ranking within groups

> "Top product in each region"

Instead of finding the overall top product, it finds:

```text
APAC → best product
EMEA → best product
NA   → best product
```

---

### Customer ranking

> "Revenue of top 3 customers per region"

It performs:

```text
APAC
 ├── Customer 1
 ├── Customer 2
 └── Customer 3

EMEA
 ├── Customer 1
 ├── Customer 2
 └── Customer 3

NA
 ├── Customer 1
 ├── Customer 2
 └── Customer 3
```

---

### Year-over-year analysis

> "YoY growth in revenue"

The system compares:

```text
2024 revenue
      vs
2023 revenue
```

and calculates:

```text
Growth %
```

Your current dataset only has one year, so there's no previous year available, which is why that particular query returns an empty result.

---

# 📁 What is each file doing?

Your project is roughly:

```text
intelligent-analytics-query-engine/
│
├── data/
│   ├── sales_data.csv
│   ├── targets.csv
│   ├── data_dictionary.json
│   └── nl_queries.json
│
├── app/
│   ├── main.py
│   ├── data_loader.py
│   ├── database.py
│   ├── query_executor.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── core/
│   │   └── sql_validator.py
│   │
│   ├── models/
│   │   └── query_plan.py
│   │
│   └── services/
│       ├── genai_service.py
│       ├── query_engine.py
│       ├── query_service.py
│       └── sql_generator.py
│
├── tests/
│
├── requirements.txt
└── README.md
```

The important files are:

### `data_loader.py`

Reads the CSV files.

```text
CSV
 ↓
Pandas DataFrame
```

---

### `database.py`

Creates the DuckDB database.

```text
sales_data.csv
      ↓
   DuckDB
      ↓
sales table
```

---

### `genai_service.py`

Responsible for understanding the natural-language query and converting it into a QueryPlan.

This is where we'll eventually connect the **real local GenAI model**.

---

### `query_plan.py`

Defines the structure of the interpreted query.

---

### `sql_generator.py`

Converts:

```text
QueryPlan
```

into:

```text
SQL
```

---

### `sql_validator.py`

Makes sure the generated SQL is safe.

---

### `query_executor.py`

Actually executes the SQL against DuckDB.

---

### `query_engine.py`

This is basically the **orchestrator**.

It connects everything:

```text
User Query
   ↓
GenAI
   ↓
QueryPlan
   ↓
SQL
   ↓
Validation
   ↓
Execution
   ↓
Result
   ↓
Confidence + Explanation
```

---

### `routes.py`

Provides the API.

For example:

```text
POST /api/query
```

The frontend/client can send:

```json
{
  "query": "Top 2 cities by profit"
}
```

and receive the answer.

---

# 🎯 So what problem are you solving?

The actual business problem is:

> **Business data is often stored in databases, but non-technical users don't know SQL. Your system lets them ask analytical questions in natural language and automatically converts those questions into safe, executable analytical queries.**

That's the one-line explanation.

---

# 🗣️ How to explain it in an interview

If the interviewer asks:

### "Tell me about your project."

You can say:

> **"My project is an Intelligent Analytics Query Engine that allows users to query business sales data using natural language instead of SQL. The system interprets the user's query and converts it into a structured query plan containing the metric, dimensions, filters, ranking, and comparison requirements. It then generates analytical SQL, validates the SQL for security, executes it using DuckDB, and returns the result along with a confidence score and an explanation. It supports operations such as aggregation, grouping, filtering, top-N ranking, ranking within groups, contribution percentage, target comparison, and year-over-year analysis. The GenAI component is intended to make the natural-language understanding flexible rather than relying only on predefined queries."**

That's a **strong 1-minute explanation**.

---

# ⭐ The easiest way to remember the whole project

Just remember these **7 words**:

> **Ask → Understand → Plan → Generate → Validate → Execute → Explain**

```text
ASK
 ↓
"Top 3 customers per region"

UNDERSTAND
 ↓
Revenue + Customer + Region + Top 3

PLAN
 ↓
QueryPlan

GENERATE
 ↓
SQL

VALIDATE
 ↓
Safe SQL?

EXECUTE
 ↓
DuckDB

EXPLAIN
 ↓
Result + Confidence + Explanation
```

**That's your entire project.**
