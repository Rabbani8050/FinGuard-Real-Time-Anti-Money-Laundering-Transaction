"use strict";
document.addEventListener("DOMContentLoaded", () => {
  const graph = new TransactionGraph(document.getElementById("graph-canvas"));
  const txStream = document.getElementById("tx-stream");
  const tpsEl    = document.getElementById("tps-counter");
  let txCount = 0, lastSec = Date.now();

  connectWS((data) => {
    // Update TPS
    txCount++;
    const now = Date.now();
    if (now - lastSec >= 1000) {
      if (tpsEl) tpsEl.textContent = txCount.toLocaleString();
      txCount = 0; lastSec = now;
    }
    // Update graph
    if (data.from_account && data.to_account) {
      graph.addTransaction(data.from_account, data.to_account, data.risk_level || "clean");
    }
    // Transaction stream row
    if (txStream) {
      const row = document.createElement("div");
      row.className = `tx-row ${data.flagged ? "risk" : "ok"}`;
      row.innerHTML = `<span>${(data.from_account||"").slice(0,10)}</span>
                       <span>$${(data.amount||0).toLocaleString()}</span>
                       <span>${data.risk_level||""}</span>`;
      txStream.insertBefore(row, txStream.firstChild);
      if (txStream.children.length > 15) txStream.lastChild.remove();
    }
  });

  // Fetch alert stats every 10s
  async function refreshAlerts() {
    try {
      const r = await fetch("/api/alerts?limit=20");
      const data = await r.json();
      const list = document.getElementById("alert-list");
      if (list && data.alerts) {
        list.innerHTML = data.alerts.slice(0, 8).map(a => `
          <div class="alert-item">
            <span class="alert-id">${a.alert_id || "AML-????"}</span>
            <span class="alert-score">${a.risk_score}</span>
            <span class="alert-level">${a.risk_level}</span>
          </div>`).join("");
      }
    } catch (_) {}
  }
  refreshAlerts();
  setInterval(refreshAlerts, 10000);
});
