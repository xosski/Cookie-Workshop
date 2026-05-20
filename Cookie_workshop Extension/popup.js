const SAME_SITE_VALUES = new Set(["lax", "strict", "no_restriction"]);

function byId(id) {
    return document.getElementById(id);
}

function showMessage(text, status = "success") {
    const message = byId("message");
    message.textContent = text;
    message.className = `message ${status}`;
}

function clearMessage() {
    byId("message").className = "message hidden";
    byId("message").textContent = "";
}

async function getCurrentTab() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.url) {
        throw new Error("No active tab URL found.");
    }
    return tab;
}

async function getActiveHttpUrl() {
    const tab = await getCurrentTab();
    const url = new URL(tab.url);
    if (!["http:", "https:"].includes(url.protocol)) {
        throw new Error("Open an http:// or https:// page before using Cookie Workshop.");
    }
    return url;
}

function normalizePath(path) {
    const trimmed = (path || "/").trim() || "/";
    return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

function optionalDomain(domain) {
    return (domain || "").trim() || undefined;
}

function displayDomain(domain) {
    return domain?.startsWith(".") ? domain.slice(1) : domain;
}

function buildCookieUrl(activeUrl, { domain, path = "/", secure = false } = {}) {
    const host = displayDomain(domain) || activeUrl.hostname;
    const protocol = secure || activeUrl.protocol === "https:" ? "https:" : activeUrl.protocol;
    return `${protocol}//${host}${normalizePath(path)}`;
}

function validateCookieOptions({ name, sameSite, secure }) {
    if (!name?.trim()) {
        throw new Error("Cookie name cannot be blank.");
    }
    if (!SAME_SITE_VALUES.has(sameSite)) {
        throw new Error("SameSite must be Lax, Strict, or None.");
    }
    if (sameSite === "no_restriction" && !secure) {
        throw new Error("Modern browsers require Secure when SameSite=None.");
    }
}

function expirationDateFromFields(prefix = "") {
    const mode = byId(`${prefix}expiresMode`)?.value || "days";
    if (mode === "session") {
        return undefined;
    }
    if (mode === "max_age") {
        const maxAge = Number(byId(`${prefix}maxAge`).value || 0);
        if (maxAge < 0) {
            throw new Error("Max-Age cannot be negative.");
        }
        return Math.floor(Date.now() / 1000) + maxAge;
    }
    if (mode === "expires_at") {
        const rawExpiresAt = byId(`${prefix}expiresAt`).value;
        if (!rawExpiresAt) {
            throw new Error("Absolute expiration requires a UTC datetime.");
        }
        return Math.floor(new Date(`${rawExpiresAt}Z`).getTime() / 1000);
    }

    const days = Number(byId(`${prefix}days`).value || 7);
    if (days < 1) {
        throw new Error("Days must be at least 1.");
    }
    return Math.floor(Date.now() / 1000) + days * 24 * 60 * 60;
}

function parseCookieHeader(header) {
    const pairs = [];
    for (const part of header.split(";")) {
        const trimmed = part.trim();
        if (!trimmed) {
            continue;
        }
        if (!trimmed.includes("=")) {
            throw new Error(`Invalid cookie pair: ${trimmed}`);
        }
        const [name, ...valueParts] = trimmed.split("=");
        const cookieName = name.trim();
        if (!cookieName) {
            throw new Error("Cookie names cannot be blank.");
        }
        pairs.push([cookieName, valueParts.join("=").trim()]);
    }
    if (!pairs.length) {
        throw new Error("Cookie header did not contain any name=value pairs.");
    }
    return pairs;
}

async function getVisibleCookies() {
    const activeUrl = await getActiveHttpUrl();
    const url = buildCookieUrl(activeUrl, { path: activeUrl.pathname || "/" });
    const cookies = await chrome.cookies.getAll({ url });
    cookies.sort((a, b) => a.name.localeCompare(b.name) || a.path.localeCompare(b.path));
    return { activeUrl, url, cookies };
}

function appendCookieRow(container, activeUrl, cookie) {
    const row = document.createElement("div");
    row.className = "cookie";

    const title = document.createElement("b");
    title.textContent = cookie.name;

    const value = document.createElement("code");
    value.textContent = cookie.value;

    const meta = document.createElement("small");
    const expires = cookie.session ? "session" : new Date(cookie.expirationDate * 1000).toISOString();
    meta.textContent = `Domain: ${cookie.domain} | Path: ${cookie.path} | SameSite: ${cookie.sameSite || "unspecified"} | Secure: ${cookie.secure} | HttpOnly: ${cookie.httpOnly} | Expires: ${expires}`;

    const edit = document.createElement("button");
    edit.textContent = "Load into editor";
    edit.addEventListener("click", () => loadCookieIntoEditor(cookie));

    const del = document.createElement("button");
    del.textContent = "Delete";
    del.addEventListener("click", () => withErrors(async () => {
        await chrome.cookies.remove({
            url: buildCookieUrl(activeUrl, cookie),
            name: cookie.name,
            storeId: cookie.storeId,
        });
        showMessage(`Deleted cookie '${cookie.name}'.`);
        await loadCookies();
    }));

    row.append(title, document.createElement("br"), value, document.createElement("br"), meta, edit, del);
    container.appendChild(row);
}

function loadCookieIntoEditor(cookie) {
    byId("name").value = cookie.name;
    byId("value").value = cookie.value;
    byId("path").value = cookie.path || "/";
    byId("domain").value = cookie.hostOnly ? "" : cookie.domain;
    byId("sameSite").value = SAME_SITE_VALUES.has(cookie.sameSite) ? cookie.sameSite : "lax";
    byId("secure").checked = cookie.secure;
    byId("httpOnly").checked = cookie.httpOnly;
    byId("expiresMode").value = cookie.session ? "session" : "expires_at";
    byId("expiresAt").value = cookie.session ? "" : new Date(cookie.expirationDate * 1000).toISOString().slice(0, 16);
    showMessage(`Loaded '${cookie.name}' into the editor.`);
}

async function loadCookies() {
    const { activeUrl, url, cookies } = await getVisibleCookies();
    byId("site").textContent = `Current site: ${url}`;

    const rawHeader = cookies.map((cookie) => `${cookie.name}=${cookie.value}`).join("; ");
    byId("rawCookie").value = rawHeader;

    const container = byId("cookies");
    container.textContent = "";
    if (!cookies.length) {
        container.textContent = "No cookies found.";
        return;
    }

    for (const cookie of cookies) {
        appendCookieRow(container, activeUrl, cookie);
    }
}

async function setCookie() {
    const activeUrl = await getActiveHttpUrl();
    const name = byId("name").value.trim();
    const value = byId("value").value;
    const path = normalizePath(byId("path").value);
    const domain = optionalDomain(byId("domain").value);
    const sameSite = byId("sameSite").value;
    const secure = byId("secure").checked;
    const httpOnly = byId("httpOnly").checked;
    validateCookieOptions({ name, sameSite, secure });

    const details = {
        url: buildCookieUrl(activeUrl, { domain, path, secure }),
        name,
        value,
        path,
        sameSite,
        secure,
        httpOnly,
    };
    if (domain) {
        details.domain = domain;
    }
    const expirationDate = expirationDateFromFields();
    if (expirationDate !== undefined) {
        details.expirationDate = expirationDate;
    }

    await chrome.cookies.set(details);
    showMessage(`Saved cookie '${name}'.`);
    await loadCookies();
}

async function bulkSetCookies() {
    const activeUrl = await getActiveHttpUrl();
    const pairs = parseCookieHeader(byId("bulkHeader").value);
    const path = normalizePath(byId("bulkPath").value);
    const domain = optionalDomain(byId("bulkDomain").value);
    const sameSite = byId("bulkSameSite").value;
    const secure = byId("bulkSecure").checked;
    const httpOnly = byId("bulkHttpOnly").checked;
    const days = Number(byId("bulkDays").value || 7);
    if (days < 1) {
        throw new Error("Days must be at least 1.");
    }

    const expirationDate = Math.floor(Date.now() / 1000) + days * 24 * 60 * 60;
    for (const [name, value] of pairs) {
        validateCookieOptions({ name, sameSite, secure });
        const details = {
            url: buildCookieUrl(activeUrl, { domain, path, secure }),
            name,
            value,
            path,
            sameSite,
            secure,
            httpOnly,
            expirationDate,
        };
        if (domain) {
            details.domain = domain;
        }
        await chrome.cookies.set(details);
    }

    showMessage(`Saved ${pairs.length} cookies from header.`);
    await loadCookies();
}

async function deleteCookie() {
    const activeUrl = await getActiveHttpUrl();
    const name = byId("deleteName").value.trim();
    if (!name) {
        throw new Error("Cookie name cannot be blank.");
    }

    const path = normalizePath(byId("deletePath").value);
    const domain = optionalDomain(byId("deleteDomain").value);
    await chrome.cookies.remove({
        url: buildCookieUrl(activeUrl, { domain, path }),
        name,
    });
    showMessage(`Deleted cookie '${name}'.`);
    await loadCookies();
}

async function clearVisibleCookies() {
    const { activeUrl, cookies } = await getVisibleCookies();
    for (const cookie of cookies) {
        await chrome.cookies.remove({
            url: buildCookieUrl(activeUrl, cookie),
            name: cookie.name,
            storeId: cookie.storeId,
        });
    }
    showMessage(`Cleared ${cookies.length} visible cookies.`);
    await loadCookies();
}

async function withErrors(action) {
    try {
        clearMessage();
        await action();
    } catch (error) {
        showMessage(error.message || String(error), "error");
    }
}

byId("load").addEventListener("click", () => withErrors(loadCookies));
byId("set").addEventListener("click", () => withErrors(setCookie));
byId("bulkSet").addEventListener("click", () => withErrors(bulkSetCookies));
byId("deleteCookie").addEventListener("click", () => withErrors(deleteCookie));
byId("clearAll").addEventListener("click", () => withErrors(clearVisibleCookies));

withErrors(loadCookies);
