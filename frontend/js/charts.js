function renderRadarChart(data) {
    const ctx = document.getElementById("radarChart");

    new Chart(ctx, {
        type: "radar",
        data: {
            labels: ["政治", "经济", "社会", "科技", "国际"],
            datasets: [{
                label: "风险等级",
                data: data.risks || [0,0,0,0,0],
                backgroundColor: "rgba(255,99,132,0.2)",
                borderColor: "rgba(255,99,132,1)"
            }]
        }
    });
}

function renderTrendChart(data) {
    const ctx = document.getElementById("trendChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.timeline || [],
            datasets: [{
                label: "舆情热度",
                data: data.values || [],
                borderColor: "rgba(54,162,235,1)"
            }]
        }
    });
}
