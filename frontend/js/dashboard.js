async function sendQuery() {
    const text = document.getElementById("userInput").value;

    const response = await fetch("/entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({text: text})
    });

    const data = await response.json();
    const result = data.result;

    document.getElementById("resultArea").innerHTML =
        `<pre>${JSON.stringify(result, null, 2)}</pre>`;

    // 根据任务类型渲染图表
    if (result.type === "zh_risk_scan") {
        renderRadarChart(result.data);
    }

    if (result.type === "zh_opinion_landscape") {
        renderTrendChart(result.data);
    }

    if (result.type === "zh_multisource_merge") {
        renderGraph(result.data);
    }
}
