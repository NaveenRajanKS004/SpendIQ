// =========================
// CONFIG & AUTH
// =========================

const API = "http://127.0.0.1:8000"

const token = localStorage.getItem("token")

// Redirect if not logged in
if (!token) {
    window.location.href = "/login-page"
}

const headers = {
    "Authorization": "Bearer " + token
}


// =========================
// DOM REFERENCES
// =========================

const yearSelector = document.getElementById("yearSelector")
const monthSelector = document.getElementById("monthSelector")
const csvUpload = document.getElementById("csvUpload")


// =========================
// BASIC ACTIONS
// =========================

function logout() {
    localStorage.removeItem("token")
    window.location.href = "/login-page"
}

function triggerUpload() {
    csvUpload.click()
}


// =========================
// CSV UPLOAD HANDLER
// =========================

csvUpload.addEventListener("change", async function () {

    const file = csvUpload.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch(`${API}/transactions/upload`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token
        },
        body: formData
    })

    const data = await res.json()

    alert(data.message || "Upload complete")

    // Reload dashboard after upload
    loadDashboard()
})


// =========================
// YEAR SELECTOR INIT
// =========================

function initYears() {

    const currentYear = new Date().getFullYear()

    for (let y = currentYear; y >= currentYear - 5; y--) {

        const option = document.createElement("option")

        option.value = y
        option.text = y

        yearSelector.appendChild(option)
    }
}


// =========================
// 🔥 ANIMATED VALUE (NEW)
// =========================

function animateValue(id, endValue) {

    const el = document.getElementById(id)

    if (!el) return

    let start = 0
    const duration = 800
    const stepTime = 16

    const increment = endValue / (duration / stepTime)

    const timer = setInterval(() => {
        start += increment

        if (start >= endValue) {
            el.innerText = formatINR(endValue)
            clearInterval(timer)
        } else {
            el.innerText = formatINR(Math.floor(start))
        }
    }, stepTime)
}


// =========================
// YEARLY DASHBOARD
// =========================

async function loadYearDashboard(year) {

    const res = await fetch(`${API}/analytics/yearly?year=${year}`, { headers })
    const data = await res.json()

    // Update title
    document.getElementById("dashboardTitle").innerText = `Dashboard — ${year}`

    // 🔥 Animated summary
    animateValue("income", data.income)
    animateValue("expense", data.expense)
    animateValue("balance", data.balance)

    // Charts
    drawBarChart(data)
    drawCategoryChart(data.category_totals)

    // Insights
    generateInsights(data)

    // Hide transactions table
    document.getElementById("transactionsSection").style.display = "none"

    // Load subscriptions
    loadSubscriptions()
}


// =========================
// MONTHLY DASHBOARD
// =========================

async function loadMonthDashboard(year, month) {

    const res = await fetch(
        `${API}/analytics/monthly?year=${year}&month=${month}`,
        { headers }
    )

    const data = await res.json()

    const monthNames = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    // Update title
    document.getElementById("dashboardTitle").innerText =
        `Dashboard — ${monthNames[month - 1]} ${year}`

    // 🔥 Animated summary
    animateValue("income", data.income)
    animateValue("expense", data.expense)
    animateValue("balance", data.balance)

    // Charts
    drawCategoryChart(data.category_totals)
    drawMonthBarChart(data, month)

    // Insights
    generateInsights(data)

    // Transactions
    renderTransactions(data.transactions)
    document.getElementById("transactionsSection").style.display = "block"

    // Budgets
    await loadBudgets(year, month)
}


// =========================
// MAIN DASHBOARD LOADER
// =========================

async function loadDashboard() {

    const year = yearSelector.value
    const month = monthSelector.value

    if (month === "all") {
        loadYearDashboard(year)
    } else {
        loadMonthDashboard(year, month)
    }
}


// =========================
// EVENT LISTENERS
// =========================

yearSelector.addEventListener("change", loadDashboard)
monthSelector.addEventListener("change", loadDashboard)


// =========================
// INITIAL LOAD
// =========================

initYears()
loadDashboard()