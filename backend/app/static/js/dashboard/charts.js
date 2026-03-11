let barChart = null
let categoryChart = null


function drawBarChart(data){

    const months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    const ctx = document.getElementById("barChart").getContext("2d")

    if(barChart) barChart.destroy()

    barChart = new Chart(ctx,{
        type:"bar",
        data:{
            labels:months,
            datasets:[
                {
                    label:"Income",
                    data:data.monthly_income,
                    backgroundColor:"#22c55e"
                },
                {
                    label:"Expense",
                    data:data.monthly_expense,
                    backgroundColor:"#ef4444"
                }
            ]
        },
        options:{
            responsive:true,
            maintainAspectRatio:false,
            animation:{
                duration:1200,
                easing:'easeOutQuart'
            },
            scales:{
                y:{beginAtZero:true}
            }
        }
    })

}



function drawMonthBarChart(data,month){

    const ctx = document.getElementById("barChart").getContext("2d")

    if(barChart) barChart.destroy()

    barChart = new Chart(ctx,{
        type:"bar",
        data:{
            labels:["Income","Expense"],
            datasets:[
                {
                    label:"Amount",
                    data:[data.income,data.expense],
                    backgroundColor:["#22c55e","#ef4444"]
                }
            ]
        },
        options:{
            responsive:true,
            maintainAspectRatio:false,
            animation:{
                duration:1200
            },
            scales:{
                y:{beginAtZero:true}
            },
            plugins:{
                legend:{display:false}
            }
        }
    })

}



function drawCategoryChart(categories){

    const labels = Object.keys(categories)
    const values = Object.values(categories)

    const ctx = document.getElementById("categoryChart").getContext("2d")

    if(categoryChart) categoryChart.destroy()

    categoryChart = new Chart(ctx,{
        type:"pie",
        data:{
            labels:labels,
            datasets:[{data:values}]
        },
        options:{
            responsive:true,
            maintainAspectRatio:false,
            animation:{
                duration:1200
            },
            plugins:{
                legend:{position:"right"}
            }
        }
    })

}
