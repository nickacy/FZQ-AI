/**
 * FZQ-AI Dashboard Frontend (V24 — Fixed)
 * Aligned with V24 /entry contract: sends {input}, reads {data, ui_schema, timeline}
 */

let currentLang = "zh";

/* ============================================================
 * 1. 发送请求 — 对齐 V24 API 契约
 * ============================================================ */

async function sendQuery() {
    const text = document.getElementById("userInput").value;

    const response = await fetch("http://127.0.0.1:8000/entry", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            input: text,
            languages: [currentLang],
        })
    });

    let data;
    try {
        data = await response.json();
    } catch (e) {
        document.getElementById("resultArea").innerHTML =
            "<b>" + (t("error.non_json") || "Backend returned non-JSON response.") + "</b>";
        return;
    }

    // 显示原始 JSON（调试用）
    document.getElementById("resultArea").innerHTML =
        "<pre>" + JSON.stringify(data, null, 2) + "</pre>";

    // 渲染状态栏
    renderStatusBar(data);

    clearCharts();
    clearPolicyCard();
    clearDynamicComponents();

    // V24 契约: ui_schema 包含 layout; data.data 包含实际结果
    const layout = data.ui_schema || data.ui_layout;
    const result = data.data || {};

    if (layout && layout.blocks) {
        renderLayout(layout, result);
    } else {
        console.warn("No ui_schema.blocks returned");
    }
}


/* ============================================================
 * 2. 状态栏
 * ============================================================ */

function renderStatusBar(data) {
    const m = document.getElementById("statusModel");
    const p = document.getElementById("statusPipeline");
    const t = document.getElementById("statusTrace");
    if (m) m.innerText = (t("status.model") || "Model") + ": N/A";
    if (p) p.innerText = (t("status.pipeline") || "Pipeline") + ": N/A";
    if (t) t.innerText = (t("status.trace_id") || "Trace") + ": " + (data.trace_id || "N/A");
}


/* ============================================================
 * 3. 根据 ui_schema 渲染组件
 * ============================================================ */

function renderLayout(layout, result) {
    const blocks = layout.blocks || [];
    blocks.forEach(function(block) {
        switch (block.type) {
            case "card":
                renderCard(block, result);
                break;
            case "timeline":
                renderTimeline(block, result);
                break;
            case "state_machine":
                renderStateMachine(block, result);
                break;
            default:
                console.warn("Unknown block type:", block.type);
        }
    });
}


/* ============================================================
 * 4. 辅助清理函数
 * ============================================================ */

function clearCharts() {
    var ids = ["radarChart", "trendChart"];
    ids.forEach(function(id) {
        var el = document.getElementById(id);
        if (el) {
            var ctx = el.getContext("2d");
            if (ctx) ctx.clearRect(0, 0, el.width, el.height);
        }
    });
}

function clearPolicyCard() {
    var el = document.getElementById("policyCardArea");
    if (el) el.innerHTML = "";
}

function clearDynamicComponents() {
    ["timelineArea", "sourceListArea", "mergeSummaryArea", "graphArea"].forEach(function(id) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = "";
    });
}


/* ============================================================
 * 5. Card 组件
 * ============================================================ */

function renderCard(block, result) {
    var area = document.getElementById("policyCardArea");
    if (!area) return;
    area.innerHTML = "<div class=\"policy-card\"><h3>" + (block.title || "") + "</h3><pre>" +
        JSON.stringify(block.items || result, null, 2) + "</pre></div>";
}


/* ============================================================
 * 6. Timeline 组件
 * ============================================================ */

function renderTimeline(block, result) {
    var area = document.getElementById("timelineArea");
    if (!area) return;
    var items = block.items || result.timeline || [];
    area.innerHTML = "<h3>" + (t("timeline.title") || "Timeline") + "</h3><ul>" +
        items.map(function(i) { return "<li>" + JSON.stringify(i) + "</li>"; }).join("") +
        "</ul>";
}


/* ============================================================
 * 7. State Machine 组件
 * ============================================================ */

function renderStateMachine(block, result) {
    var area = document.getElementById("resultArea");
    if (!area) return;
    area.innerHTML += "<div class=\"policy-card\"><h3>" + (block.title || "State Machine") +
        "</h3><pre>" + JSON.stringify(block.states || result, null, 2) + "</pre></div>";
}


/* ============================================================
 * 8. i18n bridge (redirects to i18n.js t())
 * ============================================================ */

function t(key) {
    if (typeof window._t === "function") return window._t(key);
    return key;
}
