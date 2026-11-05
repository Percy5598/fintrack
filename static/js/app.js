const transactions = [
    {
        description: "Freelance consulting",
        date: "2026-11-01",
        type: "income",
        amount: 1255.00
    },
    {
        description: "Phone bill",
        date: "2026-11-02",
        type: "expense",
        amount: 125.50
    },
    {
        description: "Software subscription",
        date: "2026-11-03",
        type: "expense",
        amount: 50.00
    },
    {
        description: "Data analysis project",
        date: "2026-10-15",
        type: "income",
        amount: 850.00
    }
];

const formatEUR = amount =>
    new Intl.NumberFormat("en-FI", {
        style: "currency",
        currency: "EUR"
    }).format(amount);

function updateDashboard() {
    const revenue = transactions
        .filter(t => t.type === "income")
        .reduce((sum, t) => sum + t.amount, 0);

    const expenses = transactions
        .filter(t => t.type === "expense")
        .reduce((sum, t) => sum + t.amount, 0);

    document.getElementById("revenue").textContent =
        formatEUR(revenue);

    document.getElementById("expenses").textContent =
        formatEUR(expenses);

    document.getElementById("profit").textContent =
        formatEUR(revenue - expenses);

    // Illustrative VAT estimate.
    // Replace with the backend's actual VAT calculation.
    document.getElementById("vat").textContent =
        formatEUR((revenue - expenses) * 0.255);

    renderTransactions();
    renderChart();
}

function renderTransactions() {
    const container = document.getElementById("transactionList");

    const recent = [...transactions]
        .sort((a, b) => b.date.localeCompare(a.date))
        .slice(0, 5);

    container.innerHTML = recent.map(transaction => `
        <div class="transaction-item">
            <div>
                <div class="transaction-description">
                    ${transaction.description}
                </div>
                <div class="transaction-date">
                    ${transaction.date}
                </div>
            </div>
            <div class="transaction-amount ${transaction.type}">
                ${transaction.type === "income" ? "+" : "-"}
                ${formatEUR(transaction.amount)}
            </div>
        </div>
    `).join("");
}

let financeChart;

function renderChart() {
    const monthly = {};

    transactions.forEach(transaction => {
        const month = transaction.date.slice(0, 7);

        if (!monthly[month]) {
            monthly[month] = {
                income: 0,
                expense: 0
            };
        }

        monthly[month][transaction.type] += transaction.amount;
    });

    const labels = Object.keys(monthly).sort();

    const data = {
        labels,
        datasets: [
            {
                label: "Revenue",
                data: labels.map(month => monthly[month].income),
                backgroundColor: "#2563eb",
                borderRadius: 5
            },
            {
                label: "Expenses",
                data: labels.map(month => monthly[month].expense),
                backgroundColor: "#cbd5e1",
                borderRadius: 5
            }
        ]
    };

    if (financeChart) {
        financeChart.destroy();
    }

    financeChart = new Chart(
        document.getElementById("financeChart"),
        {
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
                        beginAtZero: true,
                        grid: {
                            color: "#eef2f7"
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        }
    );
}

document.getElementById("addTransactionBtn")
    .addEventListener("click", () => {
        alert(
            "Transaction entry will be connected to the backend in the next step."
        );
    });

updateDashboard();