const API_BASE = "/api";

let financeChart = null;
let transactions = [];

const formatEUR = cents =>
    new Intl.NumberFormat("en-FI", {
        style: "currency",
        currency: "EUR"
    }).format(cents / 100);

async function fetchDashboard() {
    try {
        const response = await fetch(`${API_BASE}/dashboard`);

        if (!response.ok) {
            throw new Error("Could not load dashboard data.");
        }

        const data = await response.json();

        transactions = data.transactions;

        updateSummary(data.summary);
        renderTransactions();
        renderChart();

    } catch (error) {
        console.error("Dashboard error:", error);

        const container = document.getElementById("transactionList");

        if (container) {
            container.textContent = "Unable to load transactions.";
        }
    }
}

function updateSummary(summary) {
    document.getElementById("revenue").textContent =
        formatEUR(summary.revenue_cents);

    document.getElementById("expenses").textContent =
        formatEUR(summary.expenses_cents);

    document.getElementById("profit").textContent =
        formatEUR(summary.profit_cents);

    document.getElementById("vat").textContent =
        formatEUR(summary.vat_payable_cents);
}

function renderTransactions() {
    const container = document.getElementById("transactionList");

    if (!container) return;

    container.replaceChildren();

    const recent = [...transactions]
        .sort((a, b) =>
            b.transaction_date.localeCompare(a.transaction_date)
        )
        .slice(0, 5);

    if (recent.length === 0) {
        container.textContent = "No transactions recorded yet.";
        return;
    }

    recent.forEach(transaction => {
        const item = document.createElement("div");
        item.className = "transaction-item";

        const details = document.createElement("div");

        const description = document.createElement("div");
        description.className = "transaction-description";
        description.textContent = transaction.description;

        const transactionDate = document.createElement("div");
        transactionDate.className = "transaction-date";
        transactionDate.textContent = transaction.transaction_date;

        details.append(description, transactionDate);

        const amount = document.createElement("div");
        amount.className =
            `transaction-amount ${transaction.transaction_type}`;

        const sign =
            transaction.transaction_type === "income" ? "+" : "-";

        amount.textContent =
            `${sign} ${formatEUR(transaction.gross_cents)}`;

        item.append(details, amount);
        container.appendChild(item);
    });
}

function renderChart() {
    const canvas = document.getElementById("financeChart");

    if (!canvas || typeof Chart === "undefined") return;

    const monthly = {};

    transactions.forEach(transaction => {
        const month = transaction.transaction_date.slice(0, 7);

        if (!monthly[month]) {
            monthly[month] = {
                income: 0,
                expense: 0
            };
        }

        // Chart displays gross transaction amounts.
        monthly[month][transaction.transaction_type] +=
            transaction.gross_cents / 100;
    });

    const labels = Object.keys(monthly).sort();

    const data = {
        labels,
        datasets: [
            {
                label: "Income (gross)",
                data: labels.map(month => monthly[month].income),
                backgroundColor: "#2563eb",
                borderRadius: 5
            },
            {
                label: "Expenses (gross)",
                data: labels.map(month => monthly[month].expense),
                backgroundColor: "#cbd5e1",
                borderRadius: 5
            }
        ]
    };

    if (financeChart) {
        financeChart.destroy();
    }

    financeChart = new Chart(canvas, {
        type: "bar",
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Load real data from Flask.
document.addEventListener("DOMContentLoaded", fetchDashboard);