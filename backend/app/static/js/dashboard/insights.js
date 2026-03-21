// =========================
// GENERATE INSIGHTS
// =========================

function generateInsights(data) {

    const list = document.getElementById("insightsList")

    // Clear previous insights
    list.innerHTML = ""

    // No category data → nothing to show
    if (!data.category_totals) return

    const categories = data.category_totals

    // Find category with highest spending
    const topCategory = Object.keys(categories).reduce((a, b) =>
        categories[a] > categories[b] ? a : b
    )

    // Create insight item
    const li = document.createElement("li")

    li.innerText = `${getCategoryIcon(topCategory)} Highest spending category: ${topCategory} (${formatINR(categories[topCategory])})`

    list.appendChild(li)
}