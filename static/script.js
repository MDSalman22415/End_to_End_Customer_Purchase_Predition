// ============================================================
// Checkout Signal — frontend logic
// ============================================================

const API_BASE = "http://127.0.0.1:8001";

const form = document.getElementById("predictForm");
const submitBtn = document.getElementById("submitBtn");
const resetBtn = document.getElementById("resetBtn");
const formNote = document.getElementById("formNote");
const toast = document.getElementById("toast");

const receiptIdle = document.getElementById("receiptIdle");
const receiptPrint = document.getElementById("receiptPrint");
const receiptTimestamp = document.getElementById("receiptTimestamp");
const receiptVerdict = document.getElementById("receiptVerdict");
const verdictIcon = document.getElementById("verdictIcon");
const verdictText = document.getElementById("verdictText");
const verdictExplain = document.getElementById("verdictExplain");
const receiptTable = document.getElementById("receiptTable");

const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

// ------------------------------------------------------------
// Validation rules — mirrors the FastAPI/Pydantic schema
// ------------------------------------------------------------
const RULES = {
  age:                 { min: 18,  max: 100,  label: "Age" },
  income:              { min: 100, max: 20000, label: "Income" },
  browsing_time:       { min: 1,   max: 200,  label: "Browsing time" },
  pages_viewed:        { min: 2,   max: 30,   label: "Pages viewed" },
  previous_purchases:  { min: 2,   max: 80,   label: "Previous purchases" },
};

function clearErrors() {
  Object.keys(RULES).forEach((name) => {
    const el = document.getElementById(`err-${name}`);
    if (el) el.textContent = "";
    document.getElementById(name).closest(".field").classList.remove("has-error");
  });
  formNote.textContent = "";
}

function validate(values) {
  let firstInvalid = null;

  for (const [name, rule] of Object.entries(RULES)) {
    const raw = values[name];
    const num = Number(raw);
    const errEl = document.getElementById(`err-${name}`);
    const fieldEl = document.getElementById(name).closest(".field");
    let message = "";

    if (raw === "" || raw === null || Number.isNaN(num)) {
      message = "Required";
    } else if (num < rule.min || num > rule.max) {
      message = `${rule.label} must be between ${rule.min} and ${rule.max}`;
    }

    if (message) {
      errEl.textContent = message;
      fieldEl.classList.add("has-error");
      if (!firstInvalid) firstInvalid = document.getElementById(name);
    }
  }

  // required selects
  ["gender", "product_category", "discount_used"].forEach((name) => {
    if (!values[name]) {
      const fieldEl = document.getElementById(name).closest(".field");
      fieldEl.classList.add("has-error");
      if (!firstInvalid) firstInvalid = document.getElementById(name);
    }
  });

  return firstInvalid;
}

// ------------------------------------------------------------
// Toast
// ------------------------------------------------------------
let toastTimer;
function showToast(message, isError = false) {
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.toggle("is-error", isError);
  toast.classList.add("is-visible");
  toastTimer = setTimeout(() => toast.classList.remove("is-visible"), 3800);
}

// ------------------------------------------------------------
// API health check
// ------------------------------------------------------------
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/`, { method: "GET" });
    if (res.ok) {
      statusDot.className = "status__dot is-online";
      statusText.textContent = "API Connected";
    } else {
      throw new Error("not ok");
    }
  } catch {
    statusDot.className = "status__dot is-offline";
    statusText.textContent = "API Unavailable";
  }
}

// ------------------------------------------------------------
// Submit handler
// ------------------------------------------------------------
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearErrors();

  const fd = new FormData(form);
  const values = Object.fromEntries(fd.entries());

  const firstInvalid = validate(values);
  if (firstInvalid) {
    formNote.textContent = "Check the highlighted fields before ringing this in.";
    firstInvalid.focus();
    return;
  }

  const payload = {
    age: Number(values.age),
    gender: values.gender,
    income: Number(values.income),
    product_category: values.product_category,
    browsing_time: Number(values.browsing_time),
    pages_viewed: Number(values.pages_viewed),
    previous_purchases: Number(values.previous_purchases),
    discount_used: values.discount_used,
  };

  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (res.status === 422) {
      const detail = await res.json().catch(() => null);
      throw new Error(
        detail?.detail?.[0]?.msg
          ? `Validation error: ${detail.detail[0].msg}`
          : "The API rejected the ticket — check the values and try again."
      );
    }

    if (!res.ok) {
      throw new Error(`Server responded with ${res.status}.`);
    }

    const data = await res.json();
    if (!data || !data.prediction) {
      throw new Error("Unexpected response shape from the API.");
    }

    printReceipt(payload, data.prediction);
  } catch (err) {
    const message =
      err instanceof TypeError
        ? "Can't reach the API — is the FastAPI server running on port 8000?"
        : err.message || "Something went wrong reading that prediction.";
    showToast(message, true);
    statusDot.className = "status__dot is-offline";
    statusText.textContent = "API Unavailable";
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle("is-loading", isLoading);
}

// ------------------------------------------------------------
// Reset
// ------------------------------------------------------------
resetBtn.addEventListener("click", () => {
  form.reset();
  clearErrors();
  receiptPrint.hidden = true;
  receiptIdle.hidden = false;
});

// ------------------------------------------------------------
// Render the "printed" receipt
// ------------------------------------------------------------
const CATEGORY_LABEL = {
  Fashion: "Fashion", Grocery: "Grocery", Home: "Home",
  Beauty: "Beauty", Electronics: "Electronics", Sports: "Sports",
};

function printReceipt(payload, prediction) {
  const isGo = prediction === "PURCHASED";

  receiptIdle.hidden = true;
  receiptPrint.hidden = false;
  // restart animation
  receiptPrint.style.animation = "none";
  void receiptPrint.offsetWidth;
  receiptPrint.style.animation = "";

  receiptTimestamp.textContent = new Date().toLocaleString(undefined, {
    dateStyle: "medium", timeStyle: "short",
  });

  receiptVerdict.className = `receipt__verdict ${isGo ? "is-go" : "is-stop"}`;
  verdictText.textContent = isGo ? "LIKELY TO PURCHASE" : "UNLIKELY TO PURCHASE";
  verdictIcon.innerHTML = isGo
    ? `<svg viewBox="0 0 24 24" fill="none"><path d="M4 12l5 5L20 6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>`
    : `<svg viewBox="0 0 24 24" fill="none"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>`;

  verdictExplain.textContent = isGo
    ? `${payload.previous_purchases} past purchases and ${payload.pages_viewed} pages viewed this session point toward checkout.`
    : `Signals from this session — ${payload.browsing_time}min browsing, ${payload.pages_viewed} pages — don't add up to a checkout yet.`;

  const rows = [
    ["Age", payload.age],
    ["Gender", payload.gender],
    ["Category", CATEGORY_LABEL[payload.product_category] || payload.product_category],
    ["Income", `$${Number(payload.income).toLocaleString()}`],
    ["Browsing time", `${payload.browsing_time} min`],
    ["Pages viewed", payload.pages_viewed],
    ["Prev. purchases", payload.previous_purchases],
    ["Discount used", payload.discount_used],
  ];

  receiptTable.innerHTML = rows
    .map(([label, value]) => `<tr><td>${label}</td><td>${value}</td></tr>`)
    .join("");

  receiptPrint.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ------------------------------------------------------------
// Init
// ------------------------------------------------------------
checkHealth();
setInterval(checkHealth, 30000);
