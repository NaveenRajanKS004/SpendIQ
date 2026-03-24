// =========================
// CONFIG & AUTH
// =========================

const API = "http://127.0.0.1:8000"

const token = localStorage.getItem("token")

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
// CSV UPLOAD
// =========================

csvUpload.addEventListener("change", async function () {

    const file = csvUpload.files[0]
    if (!file) return

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch(`${API}/transactions/upload`, {
        method: "POST",
        headers: { "Authorization": "Bearer " + token },
        body: formData
    })

    const data = await res.json()

    alert(data.message || "Upload complete")
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
// 🔥 SMOOTH ANIMATION (UPGRADED)
// =========================

function animateValue(id, endValue) {

    const el = document.getElementById(id)
    if (!el) return

    const duration = 800
    let startTimestamp = null

    const startValue = 0

    function easeOutQuad(t) {
        return t * (2 - t)
    }

    function step(timestamp) {

        if (!startTimestamp) startTimestamp = timestamp

        const progress = Math.min((timestamp - startTimestamp) / duration, 1)
        const eased = easeOutQuad(progress)

        const value = Math.floor(eased * endValue)

        el.innerText = formatINR(value)

        if (progress < 1) {
            requestAnimationFrame(step)
        } else {
            el.innerText = formatINR(endValue)
        }
    }

    requestAnimationFrame(step)
}


// =========================
// 🔥 CARD ENTRY ANIMATION
// =========================

function animateCards() {

    const cards = document.querySelectorAll(".card")

    cards.forEach((card, index) => {
        card.style.opacity = "0"
        card.style.transform = "translateY(20px)"

        setTimeout(() => {
            card.style.transition = "all 0.4s ease"
            card.style.opacity = "1"
            card.style.transform = "translateY(0)"
        }, index * 120)
    })
}


// =========================
// YEARLY DASHBOARD
// =========================

async function loadYearDashboard(year) {

    const res = await fetch(`${API}/analytics/yearly?year=${year}`, { headers })
    const data = await res.json()

    document.getElementById("dashboardTitle").innerText = `Dashboard — ${year}`

    animateValue("income", data.income)
    animateValue("expense", data.expense)
    animateValue("balance", data.balance)

    drawBarChart(data)
    drawCategoryChart(data.category_totals)

    generateInsights(data, year, 1)

    document.getElementById("transactionsSection").style.display = "none"

    loadSubscriptions()

    // 🔥 trigger animation
    animateCards()
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
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    document.getElementById("dashboardTitle").innerText =
        `Dashboard — ${monthNames[month - 1]} ${year}`

    animateValue("income", data.income)
    animateValue("expense", data.expense)
    animateValue("balance", data.balance)

    drawCategoryChart(data.category_totals)
    drawMonthBarChart(data, month)

    generateInsights(data, year, parseInt(month))

    renderTransactions(data.transactions)
    document.getElementById("transactionsSection").style.display = "block"

    await loadBudgets(year, month)

    // 🔥 trigger animation
    animateCards()
}


// =========================
// MAIN LOADER
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
// EVENTS
// =========================

yearSelector.addEventListener("change", loadDashboard)
monthSelector.addEventListener("change", loadDashboard)


// =========================
// INITIAL LOAD
// =========================

initYears()
loadDashboard()