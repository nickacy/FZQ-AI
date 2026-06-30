// static/js/charts.js
// V23-Final — UI Components
// Author: Nick
// Version: V23.1.0

export function renderRiskCard(data) {
    const card = document.createElement("div");
    card.className = "risk-card";

    card.innerHTML = `
        <h3>风险扫描</h3>
        <p>总体风险等级：${data.overall_risk_level || "未知"}</p>
        <ul>
            ${(data.risks || []).map(r => `<li>${r.category}: ${r.description}</li>`).join("")}
        </ul>
    `;

    return card;
}

export function renderTimeline(data) {
    const container = document.createElement("div");
    container.className = "timeline";

    container.innerHTML = `
        <h3>事件时间线</h3>
        <ul>
            ${(data.events || []).map(e => `<li>${e.timestamp} — ${e.summary}</li>`).join("")}
        </ul>
    `;

    return container;
}

export function renderQuoteCard(data) {
    const card = document.createElement("div");
    card.className = "quote-card";

    card.innerHTML = `
        <blockquote>${data.quote}</blockquote>
        <p>来源：${data.source || "未知"}</p>
        <p>时间：${data.timestamp || "未知"}</p>
    `;

    return card;
}
