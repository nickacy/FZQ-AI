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
    const title = document.getElementById("appTitle");
    if (title) title.innerText = t("app.title");

    const subtitle = document.getElementById("appSubtitle");
    if (subtitle) subtitle.innerText = t("app.subtitle");

    // 输入框 placeholder
    const input = document.getElementById("userInput");
    if (input) input.placeholder = t("input.placeholder");

    // 按钮
    const submitBtn = document.getElementById("submitBtn");
    if (submitBtn) submitBtn.innerText = t("button.submit");

    const zhBtn = document.getElementById("langZhBtn");
    if (zhBtn) zhBtn.innerText = t("button.zh");

    const enBtn = document.getElementById("langEnBtn");
    if (enBtn) enBtn.innerText = t("button.en");

    // 其他 UI 文本可以继续扩展
}

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
