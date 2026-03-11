const API = "http://127.0.0.1:8000"

const token = localStorage.getItem("token")

if(!token){
    window.location.href="/login-page"
}

const headers = {
    "Authorization":"Bearer "+token
}

const yearSelector = document.getElementById("yearSelector")
const monthSelector = document.getElementById("monthSelector")
const csvUpload = document.getElementById("csvUpload")


function logout(){
    localStorage.removeItem("token")
    window.location.href="/login-page"
}


function triggerUpload(){
    csvUpload.click()
}


csvUpload.addEventListener("change", async function(){

    const file = csvUpload.files[0]
    if(!file) return

    const formData = new FormData()
    formData.append("file",file)

    const res = await fetch(`${API}/transactions/upload`,{
        method:"POST",
        headers:{
            "Authorization":"Bearer "+token
        },
        body:formData
    })

    const data = await res.json()

    alert(data.message || "Upload complete")

    loadDashboard()

})


function initYears(){

    const currentYear = new Date().getFullYear()

    for(let y=currentYear; y>=currentYear-5; y--){

        const option=document.createElement("option")

        option.value=y
        option.text=y

        yearSelector.appendChild(option)

    }

}


async function loadYearDashboard(year){

    const res = await fetch(`${API}/analytics/yearly?year=${year}`,{headers})
    const data = await res.json()

    document.getElementById("dashboardTitle").innerText = `Dashboard — ${year}`

    document.getElementById("income").innerText = formatINR(data.income)
    document.getElementById("expense").innerText = formatINR(data.expense)
    document.getElementById("balance").innerText = formatINR(data.balance)

    drawBarChart(data)
    drawCategoryChart(data.category_totals)

    generateInsights(data)

    document.getElementById("transactionsSection").style.display="none"

    loadSubscriptions()

}


async function loadMonthDashboard(year,month){

    const res = await fetch(`${API}/analytics/monthly?year=${year}&month=${month}`,{headers})
    const data = await res.json()

    const monthNames = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    document.getElementById("dashboardTitle").innerText =
        `Dashboard — ${monthNames[month-1]} ${year}`

    document.getElementById("income").innerText = formatINR(data.income)
    document.getElementById("expense").innerText = formatINR(data.expense)
    document.getElementById("balance").innerText = formatINR(data.balance)

    drawCategoryChart(data.category_totals)

    drawMonthBarChart(data,month)

    generateInsights(data)

    renderTransactions(data.transactions)
    
    document.getElementById("transactionsSection").style.display = "block"
    await loadBudgets(year, month)

}


async function loadDashboard(){

    const year = yearSelector.value
    const month = monthSelector.value

    if(month==="all"){
        loadYearDashboard(year)
    }else{
        loadMonthDashboard(year,month)
    }

}


yearSelector.addEventListener("change",loadDashboard)
monthSelector.addEventListener("change",loadDashboard)

initYears()
loadDashboard()