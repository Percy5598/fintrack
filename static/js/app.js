const fmt = (n) => new Intl.NumberFormat("en-US", {
  style: "currency", currency: "EUR"
}).format(n);

async function loadAll() {
  const [txs, report] = await Promise.all([
    fetch("/api/transactions").then(r => r.json()),
    fetch("/api/report").then(r => r.json()),
  ]);

  // summary
  const s = report.summary;
  document.getElementById("s-income").textContent   = fmt(s.income_net);
  document.getElementById("s-expenses").textContent = fmt(s.expenses_net);
  document.getElementById("s-profit").textContent   = fmt(s.profit_net);
  document.getElementById("s-margin").textContent   = `${s.margin_pct}%`;
  document.getElementById("s-vat").textContent      = fmt(s.vat_payable);

  // table
  const tbody = document.querySelector("#tx-table tbody");
  tbody.innerHTML = "";
  for (const t of txs) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${t.date}</td>
      <td class="type-${t.type}">${t.type}</td>
      <td>${t.category}</td>
      <td>${fmt(t.amount_net)}</td>
      <td>${fmt(t.vat_amount)}</td>
      <td>${fmt(t.amount_gross)}</td>
      <td><button data-id="${t.id}">✕</button></td>
    `;
    tbody.appendChild(tr);
  }

  tbody.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", async () => {
      await fetch(`/api/transactions/${btn.dataset.id}`, { method: "DELETE" });
      loadAll();
    });
  });
}

document.getElementById("tx-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  const payload = {
    type: f.type.value,
    category: f.category.value,
    description: f.description.value,
    amount_net: parseFloat(f.amount_net.value),
    vat_rate: parseFloat(f.vat_rate.value || "0"),
    vat_deductible: f.vat_deductible.checked,
    date: f.date.value,
  };
  const res = await fetch("/api/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    alert("Error: " + (err.error || res.status));
    return;
  }
  f.reset();
  loadAll();
});

// default date = today
document.querySelector('input[name="date"]').valueAsDate = new Date();
loadAll();