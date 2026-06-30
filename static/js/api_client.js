// static/js/api_client.js
// V23-Final — Unified API Client
// Author: Nick
// Version: V23.1.0

export async function callEntry(task, ctx = {}, options = {}) {
    const payload = { task, ctx, options };

    const res = await fetch("/entry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    return await res.json();
}

export async function callMulti(ctx = {}, options = {}) {
    const payload = { task: "multi_agent", ctx, options };

    const res = await fetch("/multi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    return await res.json();
}

export async function callAutonomy(options = {}) {
    const payload = { task: "autonomy_v23", ctx: {}, options };

    const res = await fetch("/autonomy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    return await res.json();
}
