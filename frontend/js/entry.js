/**
 * FZQ‑AI Unified Entry Layer (V23)
 * 负责调用后端 API，并将结果交给 V19 dashboard.js 渲染
 */

async function runEntry() {
    const text = document.getElementById("userInput").value;

    const response = await fetch("http://127.0.0.1:8000/entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            text: text,
            language: currentLang,
            session_id: "web-session-001"
        })
    });

    const data = await response.json();
    renderStatusBar(data);
    renderLayout(data.ui_layout, data.result);
}

async function runMulti() {
    const text = document.getElementById("userInput").value;

    const tasks = [
        {agent: "news_center", intent: "ANALYZE", payload: text},
        {agent: "zh_risk_scan", intent: "SUMMARIZE", payload: text},
        {agent: "zh_opinion_landscape", intent: "MERGE", payload: text}
    ];

    const response = await fetch("http://127.0.0.1:8000/multi", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({tasks})
    });

    const data = await response.json();

    document.getElementById("resultArea").innerHTML =
        `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
}

async function runAutonomy() {
    const response = await fetch("http://127.0.0.1:8000/autonomy", {
        method: "POST"
    });

    const data = await response.json();

    document.getElementById("resultArea").innerHTML =
        `<pre>${JSON.stringify(data.status, null, 2)}</pre>`;
}
