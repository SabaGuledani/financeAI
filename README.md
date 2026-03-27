# FinanceAI — Personal Finance Dashboard Powered by AI

> Upload your bank statement. Get instant AI-powered insights about where your money actually goes.

---

## What Is This?

**FinanceAI** is a full-stack web application that turns a raw bank export file into a rich, interactive spending dashboard — in seconds.

You export your transaction history from **Bank of Georgia** as an Excel file, drop it into the app, and within moments you're looking at:

- A **breakdown of your spending by category** (groceries, restaurants, transport, subscriptions, etc.)
- **Month-by-month trends** showing how your habits have changed over time
- Your **top merchants** ranked by total spend
- **Anomaly detection** that flags unusually large transactions
- **Spending pace warnings** — are you on track to overspend this month compared to your average?
- A **predicted end-of-month total** based on your current pace
- Average spending per day of the week, filterable by category

The AI part: merchant names in Georgian bank exports are raw, messy strings. FinanceAI sends them to **Google Gemini** (a large language model by Google) which reads the merchant text and assigns a human-readable category like "Restaurants" or "Utilities". Once a merchant is categorized, the result is saved to a database so the same merchant is never sent to the AI twice — keeping the app fast and cost-efficient.

---

## Who Is This For?

This project was built for anyone who has ever exported their bank statement and stared at a wall of numbers with no idea what story they tell. It's especially relevant for **Bank of Georgia** account holders, but the architecture is generic enough to adapt to any bank.

---

## Tech Stack

This project is intentionally built without heavy frameworks or boilerplate generators. Everything was written from scratch.

| Layer | Technology | Why |
|---|---|---|
| **Backend API** | Python + FastAPI | Fast, modern, auto-generates API docs |
| **Data processing** | pandas + openpyxl | Industry-standard for tabular data in Python |
| **AI / Categorization** | Google Gemini (via `google-genai`) | LLM that understands messy merchant text |
| **Database** | PostgreSQL + SQLAlchemy | Persists merchant categories to avoid redundant AI calls |
| **Frontend** | Vanilla HTML, CSS, JavaScript | No build tools, no framework overhead — loads instantly |
| **Charts** | Chartist.js | Lightweight, clean SVG charts |
| **Deployment** | Render (backend) | Free-tier cloud hosting for the API |
| **Notebooks** | Jupyter | Used for exploration and prototyping before production code |

---

## How It Works — The Full Flow

```
User uploads Excel file
        │
        ▼
Backend parses the file
(reads the "Transactions" sheet, filters only payment rows)
        │
        ▼
Merchant names are extracted from the description field
(using regex patterns specific to the Bank of Georgia format)
        │
        ▼
Unknown merchants → sent to Google Gemini in batch
Known merchants   → pulled from PostgreSQL cache instantly
        │
        ▼
Categories merged back into the dataset
        │
        ▼
~20 API endpoints serve aggregated stats to the frontend
        │
        ▼
Frontend renders charts, tables, cards, and warnings
```

### Smart Caching

Every merchant that gets categorized by Gemini is stored in the database with a **confidence level** (`high`, `medium`, `low`). Next time anyone uploads a file with the same merchant, the database is checked first. This means:

- The app gets **faster** the more it's used
- **API costs stay low** (Gemini isn't called for already-known merchants)
- Categories remain **consistent** across different users' uploads

---

## Project Structure

```
financeAI/
│
├── backend/
│   └── app/
│       ├── api/           # FastAPI route handlers (~20 endpoints)
│       ├── models/        # SQLAlchemy database models
│       ├── schemas/       # Pydantic data validation schemas
│       ├── services/      # Business logic (parsing, AI, analytics)
│       └── utils/         # DB init, in-memory store, AI prompts
│
├── frontend/
│   ├── index.html         # Single-page dashboard
│   ├── main.js            # All chart rendering and API calls (~800 lines)
│   └── styles.css         # Custom styling
│
└── ml/
    └── experiments/       # Jupyter notebooks used during development
```

---

## API Endpoints (Selected)

The backend exposes a clean REST API. Here are some highlights:

| Endpoint | What it returns |
|---|---|
| `POST /upload` | Parses the Excel file, returns session IDs |
| `GET /main-insights/spending-by-category` | Totals per category |
| `GET /main-insights/spending-by-month` | Monthly aggregates |
| `GET /main-insights/spent-so-far-warning` | Are you overspending this month? |
| `GET /main-insights/monthly-spending-prediction` | Projected end-of-month total |
| `GET /behaviour/spending-by-merchant` | Top merchants by total spend |
| `GET /behaviour/avg-spending-by-weekday` | Spending habits by day, filterable by category |
| `GET /other-insights/anomaly-transactions` | Transactions that are statistical outliers |

All endpoints accept a `dataset_id` query parameter — a UUID generated at upload time — so multiple users can use the app simultaneously without their data mixing.

---

## Anomaly Detection

Outlier transactions are detected using a **mean + 2× standard deviation** rule — a classical statistical method. Any transaction where the amount exceeds `mean + 2σ` for that currency is flagged and shown in the anomaly table. This is intentionally simple and transparent: no black-box model, just math anyone can verify.

---

## Multi-Currency Support

Bank of Georgia accounts can hold GEL, USD, EUR, and GBP. FinanceAI handles all four currencies — amounts are kept in their original currency and grouped accordingly across all charts and totals. Currency filters are available on relevant endpoints.

---

## Running Locally

**Prerequisites:** Python 3.10+, PostgreSQL, a Google AI API key.

```bash
# 1. Clone the repo
git clone https://github.com/your-username/financeAI.git
cd financeAI

# 2. Set up the backend
cd backend
pip install -r requirements.txt

# 3. Create a .env file from the example template
cp .env.example .env
# Then fill in your actual credentials in .env

# 4. Start the API server
uvicorn app.api.main:app --reload

# 5. Open frontend/index.html in your browser
#    (or use a simple local server like VS Code Live Server)
```

---

## What I Learned Building This

- How to **parse real-world Excel files** with inconsistent formatting (Georgian text, mixed currencies, unnamed columns)
- How to use **LLMs as a data enrichment tool** rather than a chat interface — sending structured batches and getting structured responses back
- The value of a **database-backed cache** for AI calls: cuts cost and latency significantly after the first run
- How to design a **stateless REST API** where the server holds session data in memory (using UUIDs as keys) rather than maintaining user sessions
- Building a dashboard entirely in **vanilla JavaScript** — reinforcing that you don't always need a framework

---

## Status

The backend is deployed and live on **Render**. The frontend calls the live API directly from the browser (no server needed for the frontend). The app is functional end-to-end.

Possible next steps:
- Support for other Georgian banks (TBC, Credo, etc.)
- User accounts and persistent history
- More sophisticated anomaly detection (e.g., category-aware thresholds)
- Budget-setting and goal tracking

---

## Author

Built by **Saba** — a developer interested in applied AI, data products, and tools that make real information accessible to real people.
