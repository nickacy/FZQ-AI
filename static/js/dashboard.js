// static/js/dashboard.js
// V23-Final — Schema-Driven Dashboard Renderer
// Author: Nick
// Version: V23.1.0

import { renderRiskCard } from "./charts.js";
import { renderTimeline } from "./charts.js";
import { renderQuoteCard } from "./charts.js";

export function renderLayout(uiLayout) {
    const container = document.getElementById("dashboard");
    container.innerHTML = "";

    uiLayout.forEach(component => {
        const { type, data } = component;

        let element = null;

        switch (type) {
            case "RiskCard":
                element = renderRiskCard(data);
                break;

            case "Timeline":
                element = renderTimeline(data);
                break;

            case "QuoteCard":
                element = renderQuoteCard(data);
                break;

            default:
                element = document.createElement("div");
                element.innerText = `Unknown component: ${type}`;
        }

        container.appendChild(element);
    });
}

export function renderResult(result) {
    const { status, data, ui_layout } = result;

    const statusEl = document.getElementById("status");
    statusEl.innerText = `Status: ${status}`;

    if (ui_layout && Array.isArray(ui_layout)) {
        renderLayout(ui_layout);
    } else {
        const container = document.getElementById("dashboard");
        container.innerHTML = "<p>No UI layout provided.</p>";
    }
}
