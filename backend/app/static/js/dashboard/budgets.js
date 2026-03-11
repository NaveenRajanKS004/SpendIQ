function getBudgetColor(percent){

    if(percent < 70) return "green"
    if(percent < 90) return "yellow"

    return "red"

}



async function loadBudgets(year, month){

    const container = document.getElementById("budgetContainer")

    if(month === "all"){
        container.innerHTML = ""
        return
    }

    const monthFormatted = month.toString().padStart(2,"0")

    const res = await fetch(`${API}/budgets/summary?month=${year}-${monthFormatted}`,{
        headers
    })

    const data = await res.json()

    container.innerHTML = ""

    Object.keys(data).forEach(cat=>{

        const b = data[cat]

        const percent = Math.min((b.spent / b.budget) * 100,100)

        const color = getBudgetColor(percent)

        const div = document.createElement("div")

        div.className = "budget-item"

        div.innerHTML = `
        <div class="budget-header">
            <span>${getCategoryIcon(cat)} ${cat}</span>
            <span>${formatINR(b.spent)} / ${formatINR(b.budget)}</span>
        </div>

        <div class="budget-bar">
            <div class="budget-progress ${color}" style="width:${percent}%"></div>
        </div>
        `

        container.appendChild(div)

    })

}



async function setBudget(){

    const category = document.getElementById("budgetCategory").value
    const amount = Number(document.getElementById("budgetAmount").value)

    const year = yearSelector.value
    const month = monthSelector.value

    if(month === "all"){
        alert("Select a month to set a budget")
        return
    }

    if(!amount){
        alert("Enter an amount")
        return
    }

    const monthFormatted = month.toString().padStart(2,"0")

    const res = await fetch(`${API}/budgets`,{
        method:"POST",
        headers:{
            "Authorization":"Bearer "+token,
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            category:category,
            amount:amount,
            month:`${year}-${monthFormatted}`
        })
    })

    if(res.ok){

        document.getElementById("budgetAmount").value=""

        await loadBudgets(year,month)

        alert("Budget saved")

    }else{

        alert("Failed to save budget")

    }

}