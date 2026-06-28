async function sendQuery() {
    const text = document.getElementById("userInput").value;

    // 使用绝对路径，避免 /static/entry 404 问题
    const response = await fetch("http://127.0.0.1:8000/entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ text: text })
    });

    let data;
    try {
        data = await response.json();
    } catch (e) {
        document.getElementById("resultArea").innerHTML =
            "<b>后端返回了非 JSON 响应，请检查服务器日志。</b>";
        return;
    }

    const result = data.result;

    // 显示 JSON 结果
    document.getElementById("resultArea").innerHTML =
        `<pre>${JSON.stringify(result, null, 2)}</pre>`;

    // 清空旧图表和卡片
    clearCharts();
    clearPolicyCard();

    // ⭐ 处理澄清请求
    if (result.type === "clarification_required") {
        document.getElementById("resultArea").innerHTML =
            `<b>系统需要更多信息：</b><br>${result.message}`;
        return;
    }

    // ⭐ 根据任务类型渲染对应图表或卡片
    if (result.type === "zh_risk_scan") {
        renderRadarChart(result.data);
    }

    if (result.type === "zh_opinion_landscape") {
        renderTrendChart(result.data);
    }

    if (result.type === "zh_multisource_merge") {
        renderGraph(result.data);
    }

    if (result.type === "zh_policy_brief") {
        renderPolicyCard(result.data);
    }
}


// 清空旧图表（避免叠加）
function clearCharts() {
    const radar = document.getElementById("radarChart");
    const trend = document.getElementById("trendChart");
    const graph = document.getElementById("graphArea");

    if (radar) radar.getContext("2d").clearRect(0, 0, radar.width, radar.height);
    if (trend) trend.getContext("2d").clearRect(0, 0, trend.width, trend.height);
    if (graph) graph.innerHTML = "";
}


// 清空政策卡片
function clearPolicyCard() {
    const cardArea = document.getElementById("policyCardArea");
    if (cardArea) cardArea.innerHTML = "";
}
