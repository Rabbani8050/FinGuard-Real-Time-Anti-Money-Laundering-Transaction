"use strict";

class TransactionGraph {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext("2d");
    this.nodes  = new Map();
    this.edges  = [];
    this.phase  = 0;
    this._resize();
    window.addEventListener("resize", () => this._resize());
    this._loop();
  }

  _resize() {
    this.canvas.width  = this.canvas.offsetWidth;
    this.canvas.height = this.canvas.offsetHeight;
  }

  addTransaction(src, dst, riskLevel) {
    const W = this.canvas.width, H = this.canvas.height;
    const cx = W / 2, cy = H / 2;
    if (!this.nodes.has(src)) {
      this.nodes.set(src, { x: cx + (Math.random() - 0.5) * W * 0.7,
                             y: cy + (Math.random() - 0.5) * H * 0.7,
                             id: src, risk: riskLevel });
    }
    if (!this.nodes.has(dst)) {
      this.nodes.set(dst, { x: cx + (Math.random() - 0.5) * W * 0.7,
                             y: cy + (Math.random() - 0.5) * H * 0.7,
                             id: dst, risk: "clean" });
    }
    this.edges.push({ s: src, t: dst, risk: riskLevel, ts: Date.now() });
    if (this.edges.length > 200) this.edges.shift();
    // Update node risk
    const n = this.nodes.get(src);
    if (riskLevel === "CRITICAL" || riskLevel === "HIGH") n.risk = riskLevel;
  }

  _nodeColor(risk) {
    if (risk === "CRITICAL" || risk === "HIGH") return "#FF2D55";
    if (risk === "MEDIUM") return "#F5C842";
    return "#00C896";
  }

  _draw() {
    const { ctx, canvas } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    this.phase += 0.015;

    // Edges
    for (const e of this.edges) {
      const s = this.nodes.get(e.s), t = this.nodes.get(e.t);
      if (!s || !t) continue;
      const col = this._nodeColor(e.risk);
      ctx.beginPath(); ctx.moveTo(s.x, s.y); ctx.lineTo(t.x, t.y);
      ctx.strokeStyle = col; ctx.globalAlpha = e.risk === "CRITICAL" ? 0.5 : 0.18;
      ctx.lineWidth = e.risk === "CRITICAL" ? 1.8 : 0.9; ctx.stroke();
      ctx.globalAlpha = 1;
      // Particle
      if (e.risk === "HIGH" || e.risk === "CRITICAL") {
        const tp = ((this.phase * 0.6) + e.ts * 0.0001) % 1;
        ctx.beginPath(); ctx.arc(s.x + (t.x - s.x) * tp, s.y + (t.y - s.y) * tp, 3, 0, Math.PI * 2);
        ctx.fillStyle = col; ctx.globalAlpha = 0.9; ctx.fill(); ctx.globalAlpha = 1;
      }
    }
    // Nodes
    for (const [, n] of this.nodes) {
      const col = this._nodeColor(n.risk);
      ctx.beginPath(); ctx.arc(n.x, n.y, 10, 0, Math.PI * 2);
      ctx.fillStyle = col; ctx.globalAlpha = 0.25; ctx.fill();
      ctx.strokeStyle = col; ctx.globalAlpha = 0.85; ctx.lineWidth = 1.5; ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.font = "9px 'JetBrains Mono',monospace";
      ctx.fillStyle = "#6A85A8"; ctx.textAlign = "center";
      ctx.fillText(n.id.slice(0, 8), n.x, n.y + 20);
    }
  }

  _loop() { this._draw(); requestAnimationFrame(() => this._loop()); }
}
