// 各頁面共用：API 呼叫、導覽列、上傳/操作回饋提示

async function api(path, options = {}) {
  const res = await fetch(path, { credentials: "include", ...options });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail || detail;
    } catch (e) { /* 回應不是 JSON */ }
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

function renderNav(user, activePage) {
  const links = [
    { href: "/static/index.html", label: "業務總覽", page: "index", icon: "folder" },
    { href: "/static/my_uploads.html", label: "我的上傳", page: "my-uploads", icon: "upload" },
  ];
  if (user.is_admin) {
    links.push({ href: "/static/admin_users.html", label: "帳號管理", page: "users", icon: "users" });
    links.push({ href: "/static/admin_handover.html", label: "人員異動", page: "handover", icon: "handover" });
    links.push({ href: "/static/admin_changelog.html", label: "結構異動歷程", page: "changelog", icon: "history" });
  }

  const linksHtml = links
    .map(
      (l) =>
        `<a href="${l.href}" class="${l.page === activePage ? "active" : ""}">${icon(l.icon)}${l.label}</a>`
    )
    .join("");

  return `
    <nav>
      ${linksHtml}
      <span class="whoami">${icon("user")}${user.display_name}${user.is_admin ? "（管理者）" : ""}</span>
      <button onclick="logout()" class="link-btn">${icon("logout")}登出</button>
    </nav>`;
}

async function logout() {
  await api("/api/auth/logout", { method: "POST" });
  location.href = "/static/index.html";
}

// feedback: 操作進行中/成功/失敗的提示，statusElId 指向頁面上一個 <div>
function showFeedback(elId, message, type = "info") {
  const el = document.getElementById(elId);
  if (!el) return;
  el.textContent = message;
  el.className = `feedback ${type}`;
  el.style.display = "block";
  if (type === "success") {
    setTimeout(() => {
      if (el.textContent === message) el.style.display = "none";
    }, 3000);
  }
}

function hideFeedback(elId) {
  const el = document.getElementById(elId);
  if (el) el.style.display = "none";
}

// 呼叫 async 動作時包一層：先顯示「處理中」、按鈕停用，結束後顯示成功/失敗訊息。
// 如果按鈕裡有 .btn-label（放圖示的按鈕都會有），只換文字部分，不會把圖示一起洗掉。
function _buttonLabelTarget(button) {
  return button ? button.querySelector(".btn-label") || button : null;
}

async function withFeedback(elId, button, busyMessage, successMessage, action) {
  const labelEl = _buttonLabelTarget(button);
  const originalText = labelEl ? labelEl.textContent : null;
  if (button) button.disabled = true;
  if (labelEl) labelEl.textContent = busyMessage;
  showFeedback(elId, busyMessage, "info");
  try {
    const result = await action();
    showFeedback(elId, successMessage, "success");
    return result;
  } catch (e) {
    showFeedback(elId, `失敗：${e.message}`, "error");
    throw e;
  } finally {
    if (button) button.disabled = false;
    if (labelEl) labelEl.textContent = originalText;
  }
}
