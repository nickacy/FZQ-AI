/**
 * FZQ‑AI i18n Engine (V18)
 * 国际化引擎：加载语言 JSON，提供 t(key) 翻译函数
 */

let currentLang = "zh";
let translations = {};

/* ============================================================
 * 1. 加载语言文件
 * ============================================================ */

async function loadLanguage(lang) {
    currentLang = lang;

    try {
        const response = await fetch(`/static/locales/${lang}.json`);
        translations = await response.json();
    } catch (e) {
        console.error("无法加载语言文件：", lang, e);
        translations = {};
    }

    applyTranslations();
}

/* ============================================================
 * 2. 翻译函数 t(key)
 * ============================================================ */

function t(key) {
    return translations[key] || key;
}

/* ============================================================
 * 3. 自动更新页面文本
 * ============================================================ */

function applyTranslations() {
    // 页面标题
    var title = document.getElementById("appTitle");
    if (title) title.innerText = t("app.title");

    var subtitle = document.getElementById("appSubtitle");
    if (subtitle) subtitle.innerText = t("app.subtitle");

    // 输入框 placeholder
    var input = document.getElementById("userInput");
    if (input) input.placeholder = t("input.placeholder");

    // 按钮
    var submitBtn = document.getElementById("submitBtn");
    if (submitBtn) submitBtn.innerText = t("button.submit");

    var zhBtn = document.getElementById("langZhBtn");
    if (zhBtn) zhBtn.innerText = t("button.zh");

    var enBtn = document.getElementById("langEnBtn");
    if (enBtn) enBtn.innerText = t("button.en");

    // 导航按钮
    var navHome = document.getElementById("navHomeText");
    if (navHome) navHome.innerText = t("nav.home");

    var navDash = document.getElementById("navDashboardText");
    if (navDash) navDash.innerText = t("nav.dashboard");

    var navSettings = document.getElementById("navSettingsText");
    if (navSettings) navSettings.innerText = t("nav.settings");
}

// 导出到全局 _t 以便 dashboard.js 使用
window._t = t;

/* ============================================================
 * 4. 设置语言（供按钮调用）
 * ============================================================ */

function setLanguage(lang) {
    loadLanguage(lang);
}

/* ============================================================
 * 5. 初始化默认语言
 * ============================================================ */

document.addEventListener("DOMContentLoaded", () => {
    loadLanguage(currentLang);
});
