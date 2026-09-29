/* Runs on every authenticated page. Populates the sidebar with the
   logged-in user's name/wallet id/balance, redirects to /login if the
   session is missing, and wires the logout button. */

async function initLayout() {
  let user;
  try {
    user = await api.get("/api/me");
  } catch (e) {
    window.location.href = "/";
    return null;
  }

  const nameEl = document.getElementById("sidebar-name");
  const walletEl = document.getElementById("sidebar-wallet");
  const balanceEl = document.getElementById("sidebar-balance");
  if (nameEl) nameEl.textContent = user.name;
  const avatarEl = document.getElementById("user-avatar");
  if (avatarEl) avatarEl.textContent = initials(user.name);
  if (walletEl) walletEl.textContent = user.wallet_id;
  if (balanceEl) balanceEl.textContent = formatMoney(user.balance);

  const path = window.location.pathname;
  document.querySelectorAll(".topnav a").forEach((a) => {
    if (a.getAttribute("href") === path) a.classList.add("active");
  });

  const logoutBtn = document.getElementById("logout-btn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      await api.post("/api/logout");
      window.location.href = "/";
    });
  }

  const menuToggle = document.getElementById("menu-toggle");
  const topnav = document.getElementById("topnav");
  if (menuToggle && topnav) {
    menuToggle.addEventListener("click", () => {
      const open = topnav.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(open));
    });
  }

  return user;
}

document.addEventListener("DOMContentLoaded", initLayout);
