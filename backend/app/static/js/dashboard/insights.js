// =========================
// GENERATE PREMIUM INSIGHTS
// =========================

function generateInsights(data) {

    const container = document.getElementById("insightsList")
    container.innerHTML = ""

    if (!data || !data.category_totals) return

    const categories = data.category_totals

    const topCategory = Object.keys(categories).reduce((a, b) =>
        categories[a] > categories[b] ? a : b
    )

    const topAmount = categories[topCategory]


    // =========================
    // INSIGHTS
    // =========================

    addInsight(
        `You spent the most on ${topCategory} (${formatINR(topAmount)})`,
        "info"
    )

    if (data.expense > data.income) {
        addInsight(
            "Your expenses exceeded your income this period",
            "danger"
        )
    } else {
        addInsight(
            "You maintained a positive balance — great job!",
            "success"
        )
    }

    if (topAmount > data.expense * 0.4) {
        addInsight(
            `${topCategory} takes a large share of your spending. Consider optimizing it.`,
            "warning"
        )
    }

    if (Object.keys(categories).length >= 5) {
        addInsight(
            "Your spending is well distributed across categories",
            "info"
        )
    }

}


// =========================
// CREATE CARD
// =========================

function addInsight(text, type) {

    const div = document.createElement("div")
    div.className = `insight-card ${type}`

    div.innerHTML = `
        <div class="insight-icon">${getIcon(type)}</div>
        <div class="insight-text">${text}</div>
    `

    document.getElementById("insightsList").appendChild(div)
}


// =========================
// ICONS
// =========================

function getIcon(type) {

    if (type === "success") return "🟢"
    if (type === "danger") return "🔴"
    if (type === "warning") return "⚠️"

    return "📊"
}