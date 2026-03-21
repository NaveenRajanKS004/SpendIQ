// =========================
// HELPER: PROGRESS COLOR
// =========================

function getBudgetColor(percent) {

    if (percent < 70) return "green"
    if (percent < 90) return "yellow"

    return "red"
}


// =========================
// LOAD BUDGETS
// =========================

async function loadBudgets(year, month) {

    const container = document.getElementById("budgetContainer")

    // If "All Months" selected → clear budgets
    if (month === "all") {
        container.innerHTML = ""
        return
    }

    const monthFormatted = month.toString().padStart(2, "0")

    // Fetch budget summary
    const res = await fetch(
        `${API}/budgets/summary?month=${year}-${monthFormatted}`,
        { headers }
    )

    const data = await res.json()

    container.innerHTML = ""

    // Render each category budget
    Object.keys(data).forEach(category => {

        const budget = data[category]

        // Calculate percentage spent (capped at 100%)
        const percent = Math.min((budget.spent / budget.budget) * 100, 100)

        const color = getBudgetColor(percent)

        const div = document.createElement("div")
        div.className = "budget-item"

        div.innerHTML = `
            <div class="budget-header">
                <span>${getCategoryIcon(category)} ${category}</span>
                <span>${formatINR(budget.spent)} / ${formatINR(budget.budget)}</span>
            </div>

            <div class="budget-bar">
                <div class="budget-progress ${color}" style="width:${percent}%"></div>
            </div>
        `

        container.appendChild(div)
    })
}


// =========================
// SET BUDGET
// =========================

async function setBudget() {

    const category = document.getElementById("budgetCategory").value
    const amount = Number(document.getElementById("budgetAmount").value)

    const year = yearSelector.value
    const month = monthSelector.value

    // Validation
    if (month === "all") {
        alert("Select a month to set a budget")
        return
    }

    if (!amount) {
        alert("Enter an amount")
        return
    }

    const monthFormatted = month.toString().padStart(2, "0")

    // Send request
    const res = await fetch(`${API}/budgets`, {
        method: "POST",
        headers: {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category: category,
            amount: amount,
            month: `${year}-${monthFormatted}`
        })
    })

    if (res.ok) {

        // Reset input
        document.getElementById("budgetAmount").value = ""

        // Reload UI
        await loadBudgets(year, month)

        alert("Budget saved")

    } else {
        alert("Failed to save budget")
    }
}