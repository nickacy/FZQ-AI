function renderPolicyCard(data) {
    const cardArea = document.getElementById("policyCardArea");

    const html = `
        <div class="policy-card">
            <h2 class="policy-title">${data.title}</h2>

            <p class="policy-summary">${data.summary}</p>

            <h3>影响领域 / Impact Areas</h3>
            <ul>
                ${data.impact_areas.map(item => `<li>${item}</li>`).join("")}
            </ul>

            <h3>风险等级 / Risk Level</h3>
            <p class="policy-risk">${data.risk_level}</p>

            <h3>建议行动 / Suggested Actions</h3>
            <ul>
                ${data.actions.map(item => `<li>${item}</li>`).join("")}
            </ul>

            <div class="policy-meta">
                <small>Trace ID: ${data.trace_id}</small><br>
                <small>Duration: ${data.duration_ms.toFixed(2)} ms</small>
            </div>
        </div>
    `;

    cardArea.innerHTML = html;
}
