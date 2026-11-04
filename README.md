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

## Installation

Clone the repository:

```bash
git clone https://github.com/Percy5598/fintrack-financial-reporting.git
cd fintrack-financial-reporting
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Run the application:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest -v
```

Check code quality:

```bash
ruff check .
```

## Financial Calculation Methodology

FinTrack stores monetary values as integer cents to avoid common floating-point precision errors.

The application derives net amounts and VAT from gross transaction amounts and distinguishes between deductible and non-deductible purchase VAT.

## Project Status

**Development version – v0.1.0**

Planned improvements:

- Interactive financial dashboard
- Monthly financial reporting
- Transaction editing and deletion
- CSV import and export
- Advanced financial analytics
- Improved data validation
- Deployment

## Disclaimer

FinTrack is an educational and portfolio software project. Its calculations are not a substitute for professional accounting, tax advice, or official Finnish tax reporting. VAT deductibility and tax treatment depend on individual circumstances and applicable regulations.

## License

MIT License.