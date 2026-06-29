/**
 * FZQ‑AI Dashboard Frontend (V19 · Status Bar Enhanced)
 * 使用 ui_layout 自动渲染组件 + 状态栏渲染 + 国际化
 */

async function sendQuery() {
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

    let data;
    try {
        data = await response.json();
    } catch (e) {
        document.getElementById("resultArea").innerHTML =
            `<b>${t("error.non_json")}</b>`;
        return;
    }

    // 显示原始 JSON（调试用）
    document.getElementById("resultArea").innerHTML =
        `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;

    // ⭐ 渲染状态栏
    renderStatusBar(data);

    clearCharts();
    clearPolicyCard();
    clearDynamicComponents();

    const layout = data.ui_layout;
    const result = data.result;

    if (!layout || !layout.layout_type) {
        console.warn("后端未返回 ui_layout");
        return;
    }

    renderLayout(layout, result);
}


/* ============================================================
 * 1. 状态栏渲染（模型 / 管线 / trace_id）
 * ============================================================ */

function renderStatusBar(data) {
    const modelSpan = document.getElementById("statusModel");
    const pipelineSpan = document.getElementById("statusPipeline");
    const traceSpan = document.getElementById("statusTrace");

    // 从后端 result.route 中读取 pipeline
    const route = data.result.route || {};
    const modelName = route.model_name || "N/A";
    const pipelineName = route.pipeline || "N/A";

    // trace_id
    const traceId = data.trace_id || "N/A";

    modelSpan.innerText = `${t("status.model")}: ${modelName}`;
    pipelineSpan.innerText = `${t("status.pipeline")}: ${pipelineName}`;
    traceSpan.innerText = `${t("status.trace_id")}: ${traceId}`;
}


/* ============================================================
 * 2. 根据 ui_layout 渲染组件（国际化）
 * ============================================================ */

function renderLayout(layout, result) {
    const components = layout.components || [];

    components.forEach(component => {
        switch (component.type) {

            case "risk_block":
                renderRiskBlock(result.data);
                break;

            case "risk_radar":
                renderRadarChart(result.data);
                break;

            case "sentiment_trend":
                renderTrendChart(result.data);
                break;

            case "narrative_graph":
                renderGraph(result.data);
                break;

            case "policy_brief_card":
                renderPolicyCard(result.data);
                break;

            case "timeline":
                renderTimeline(result.data);
                break;

            case "source_list":
                renderSourceList(result.data);
                break;

            case "merge_summary":
                renderMergeSummary(result.data);
                break;

            default:
                console.warn("未知组件类型：", component.type);
        }
    });
}


/* ============================================================
 * 3. 清理动态组件区域
 * ============================================================ */

function clearDynamicComponents() {
    const areas = [
        "riskBlockArea",
        "timelineArea",
        "sourceListArea",
        "mergeSummaryArea"
    ];

    areas.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = "";
    });
}


/* ============================================================
 * 4. 风险扫描组件（国际化）
 * ============================================================ */

function renderRiskBlock(data) {
    const area = document.getElementById("policyCardArea");
    if (!area) return;

    const html = `
        <div class="risk-block">
            <h3>${t("risk.title")}</h3>
            <p><b>${t("risk.overall")}：</b> ${data.overall_risk}</p>
            <p><b>${t("risk.key_points")}：</b></p>
            <ul>
                ${data.key_risks.map(r => `<li>${r}</li>`).join("")}
            </ul>
        </div>
    `;

    area.innerHTML = html;
}


/* ============================================================
 * 5. 舆情趋势图（国际化）
 * ============================================================ */

function renderTrendChart(data) {
    const ctx = document.getElementById("trendChart").getContext("2d");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.timeline,
            datasets: [{
                label: t("sentiment.title"),
                data: data.values,
                borderColor: "#4CAF50",
                fill: false
            }]
        }
    });
}


/* ============================================================
 * 6. 风险雷达图（国际化）
 * ============================================================ */

function renderRadarChart(data) {
    const ctx = document.getElementById("radarChart").getContext("2d");

    new Chart(ctx, {
        type: "radar",
        data: {
            labels: data.dimensions,
            datasets: [{
                label: t("risk.title"),
                data: data.scores,
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                borderColor: "rgba(255, 99, 132, 1)"
            }]
        }
    });
}


/* ============================================================
 * 7. 叙事图谱（D3.js）
 * ============================================================ */

function renderGraph(data) {
    const area = document.getElementById("graphArea");
    area.innerHTML = "";

    const width = 600, height = 400;

    const svg = d3.select("#graphArea")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const simulation = d3.forceSimulation(data.nodes)
        .force("link", d3.forceLink(data.links).distance(80))
        .force("charge", d3.forceManyBody().strength(-120))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .selectAll("line")
        .data(data.links)
        .enter().append("line")
        .attr("stroke", "#aaa");

    const node = svg.append("g")
        .selectAll("circle")
        .data(data.nodes)
        .enter().append("circle")
        .attr("r", 8)
        .attr("fill", "#4CAF50");

    simulation.on("tick", () => {
        link.attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node.attr("cx", d => d.x)
            .attr("cy", d => d.y);
    });
}


/* ============================================================
 * 8. 政策简报卡片（国际化）
 * ============================================================ */

function renderPolicyCard(data) {
    const area = document.getElementById("policyCardArea");
    if (!area) return;

    const html = `
        <div class="policy-card">
            <h3>${t("policy.title")}</h3>
            <p><b>${t("policy.summary")}：</b> ${data.summary}</p>
            <p><b>${t("policy.key_points")}：</b></p>
            <ul>
                ${data.key_points.map(p => `<li>${p}</li>`).join("")}
            </ul>
        </div>
    `;

    area.innerHTML = html;
}


/* ============================================================
 * 9. 时间线组件（国际化）
 * ============================================================ */

function renderTimeline(data) {
    const area = document.getElementById("timelineArea");
    if (!area) return;

    const html = `
        <h3>${t("timeline.title")}</h3>
        <ul>
            ${data.timeline.map(t => `<li>${t.date} — ${t.event}</li>`).join("")}
        </ul>
    `;

    area.innerHTML = html;
}


/* ============================================================
 * 10. 多源合并组件（国际化）
 * ============================================================ */

function renderSourceList(data) {
    const area = document.getElementById("sourceListArea");
    if (!area) return;

    const html = `
        <h3>${t("merge.sources")}</h3>
        <ul>
            ${data.sources.map(s => `<li>${s}</li>`).join("")}
        </ul>
    `;

    area.innerHTML = html;
}

function renderMergeSummary(data) {
    const area = document.getElementById("mergeSummaryArea");
    if (!area) return;

    const html = `
        <h3>${t("merge.summary")}</h3>
        <p>${data.summary}</p>
    `;

    area.innerHTML = html;
}


/* ============================================================
 * 11. 清理函数
 * ============================================================ */

function clearCharts() {
    const radar = document.getElementById("radarChart");
    const trend = document.getElementById("trendChart");
    const graph = document.getElementById("graphArea");

    if (radar) radar.getContext("2d").clearRect(0, 0, radar.width, radar.height);
    if (trend) trend.getContext("2d").clearRect(0, 0, trend.width, trend.height);
    if (graph) graph.innerHTML = "";
}

function clearPolicyCard() {
    const cardArea = document.getElementById("policyCardArea");
    if (cardArea) cardArea.innerHTML = "";
}
