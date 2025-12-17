function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
}

document.addEventListener("DOMContentLoaded", () => {
  const savedTheme = localStorage.getItem("theme") || "light";
  applyTheme(savedTheme);
});

document.getElementById("theme-toggle")?.addEventListener("click", () => {
  const current = localStorage.getItem("theme") || "light";
  const next = current === "light" ? "dark" : "light";
  applyTheme(next);
  localStorage.setItem("theme", next);
});

function deletePost(postId) {
  if (!confirm("Точно удалить?")) return;
  fetch(`/delete-post/${postId}`, { method: "POST" })
    .then(r => r.json())
    .then(() => location.reload());
}

document.getElementById("avatar-form")?.addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const res = await fetch("/upload-avatar", { method: "POST", body: fd });
  const data = await res.json();
  if (data.url) {
    document.getElementById("avatar-preview").src = data.url;
  } else {
    alert("Ошибка: " + data.error);
  }
});
