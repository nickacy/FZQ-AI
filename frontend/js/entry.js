/**
 * FZQ-AI Unified Entry Layer (V24)
 * Aligned with /entry, /multi, /autonomy V24 contracts
 */

async function runEntry() {
    var text = document.getElementById("userInput").value;

    var response = await fetch("http://127.0.0.1:8000/entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            input: text,
            languages: [currentLang || "zh"]
        })
    });

    var data = await response.json();
    renderStatusBar(data);
    if (data.ui_schema) {
        renderLayout(data.ui_schema, data.data);
    }
}

async function runMulti() {
    var text = document.getElementById("userInput").value;

    var response = await fetch("http://127.0.0.1:8000/multi", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            input: text,
            languages: [currentLang || "zh"]
        })
    });

    var data = await response.json();
    document.getElementById("resultArea").innerHTML =
        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
}

async function runAutonomy() {
    var text = document.getElementById("userInput").value;

    var response = await fetch("http://127.0.0.1:8000/autonomy", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            input: text,
            languages: [currentLang || "zh"]
        })
    });

    var data = await response.json();
    document.getElementById("resultArea").innerHTML =
        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";
}
