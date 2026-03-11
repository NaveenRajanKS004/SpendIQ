function generateInsights(data){

    const list = document.getElementById("insightsList")

    list.innerHTML = ""

    if(!data.category_totals) return

    const categories = data.category_totals

    const topCategory = Object.keys(categories).reduce((a,b)=>
        categories[a] > categories[b] ? a : b
    )

    const li = document.createElement("li")
    li.innerText = `${getCategoryIcon(topCategory)} Highest spending category: ${topCategory} (${formatINR(categories[topCategory])})`
    list.appendChild(li)

}