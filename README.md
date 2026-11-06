# FinTrack – Freelancer Financial Reporting

**FinTrack** is a Python-based financial reporting application designed to help freelancers and small businesses monitor income, expenses, profitability, and VAT.

The project explores how financial data processing, automated calculations, and interactive dashboards can simplify financial management.

## Features

- Financial transaction management
- Income and expense categorization
- Gross, net, and VAT calculations
- VAT deductibility tracking
- Financial performance summaries
- SQLite database integration
- Automated financial calculation tests

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | User interface |
| SQLite | Data persistence |
| Pandas | Data processing |
| Plotly | Financial visualizations |
| Pytest | Automated testing |
| Ruff | Code quality |

## Project Structure

```text
fintrack/
├── app.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── fintrack/
│       ├── __init__.py
│       ├── calculations.py
│       ├── database.py
│       ├── models.py
│       └── reporting.py
├── tests/
│   ├── test_calculations.py
│   └── test_database.py
├── assets/
└── .streamlit/
```

