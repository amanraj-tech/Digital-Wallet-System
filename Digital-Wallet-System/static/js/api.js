/* Small fetch wrapper shared by every page. Every API route returns
   { ok: true, data: ... } or { ok: false, error: "..." }. */

async function apiRequest(method, url, body) {
  const options = {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  };
  if (body !== undefined) {
    options.body = JSON.stringify(body);
  }
  const res = await fetch(url, options);
  let json;
  try {
    json = await res.json();
  } catch (e) {
    throw new Error("Unexpected server response.");
  }
  if (!json.ok) {
    throw new Error(json.error || "Something went wrong.");
  }
  return json.data;
}

const api = {
  get: (url) => apiRequest("GET", url),
  post: (url, body) => apiRequest("POST", url, body),
};

function formatMoney(amount) {
  const n = Number(amount);
  const sign = n < 0 ? "-" : "";
  return `${sign}₹${Math.abs(n).toFixed(2)}`;
}

function formatDateTime(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function badgeClass(status) {
  switch (status) {
    case "Success": return "success";
    case "Failed": return "failed";
    case "Pending": return "pending";
    case "Reversed": return "reversed";
    default: return "success";
  }
}

function initials(name) {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}
