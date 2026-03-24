// =========================
// GENERATE PREMIUM INSIGHTS
// =========================

async function generateInsights(data, year, month) {

    const container = document.getElementById("insightsList")
    container.innerHTML = ""

    if (!data || !data.category_totals) return

    const categories = data.category_totals
    const entries = Object.entries(categories)

    if (entries.length === 0) return

    const sorted = entries.sort((a, b) => b[1] - a[1])
    const [topCategory, topAmount] = sorted[0]

    const totalExpense = data.expense || 1
    const topPercent = ((topAmount / totalExpense) * 100).toFixed(1)


    // =========================
    // CURRENT INSIGHTS
    // =========================

    addInsight(
        `${topCategory} dominates your spending at ${topPercent}% (${formatINR(topAmount)})`,
        "info"
    )

    if (data.expense > data.income) {
        addInsight(
            `You are overspending by ${formatINR(data.expense - data.income)}`,
            "danger"
        )
    } else {
        addInsight(
            `You saved ${formatINR(data.income - data.expense)} this period`,
            "success"
        )
    }

    if (topPercent > 40) {
        addInsight(
            `High concentration in ${topCategory}. Consider reducing it`,
            "warning"
        )
    }

    if (entries.length >= 5) {
        addInsight(
            `Spending is diversified across ${entries.length} categories`,
            "info"
        )
    }

    if (sorted.length > 1) {
        const [secondCategory, secondAmount] = sorted[1]
        const secondPercent = ((secondAmount / totalExpense) * 100).toFixed(1)

        addInsight(
            `${secondCategory} is your second highest expense (${secondPercent}%)`,
            "info"
        )
    }


    // =========================
    // 🔥 MONTH COMPARISON
    // =========================

    try {

        let prevYear = year
        let prevMonth = month - 1

        if (prevMonth === 0) {
            prevMonth = 12
            prevYear -= 1
        }

        const res = await fetch(
            `${API}/analytics/monthly?year=${prevYear}&month=${prevMonth}`,
            {
                headers: {
                    "Authorization": "Bearer " + localStorage.getItem("token")
                }
            }
        )

        if (!res.ok) return

        const prevData = await res.json()

        if (!prevData || !prevData.expense) return

        const diff = data.expense - prevData.expense
        const percentChange = ((diff / prevData.expense) * 100).toFixed(1)


        // =========================
        // EXPENSE TREND
        // =========================

        if (diff > 0) {
            addInsight(
                `Your spending increased by ${percentChange}% compared to last month`,
                "danger"
            )
        } else {
            addInsight(
                `Your spending decreased by ${Math.abs(percentChange)}% — great improvement`,
                "success"
            )
        }


        // =========================
        // CATEGORY SHIFT
        // =========================

        if (prevData.category_totals) {

            const prevCategories = prevData.category_totals

            if (prevCategories[topCategory]) {

                const prevAmount = prevCategories[topCategory]
                const change = topAmount - prevAmount
                const changePercent = ((change / prevAmount) * 100).toFixed(1)

                if (change > 0) {
                    addInsight(
                        `${topCategory} spending increased by ${changePercent}%`,
                        "warning"
                    )
                } else {
                    addInsight(
                        `${topCategory} spending decreased by ${Math.abs(changePercent)}%`,
                        "success"
                    )
                }
            }
        }

    } catch (err) {
        console.log("Comparison skipped:", err)
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