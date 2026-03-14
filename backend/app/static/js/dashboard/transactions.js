function renderTransactions(transactions){

    const tbody = document.querySelector("#transactionTable tbody")
    tbody.innerHTML = ""

    const categories = [
        "Food",
        "Transport",
        "Shopping",
        "Healthcare",
        "Utilities",
        "Entertainment",
        "Income",
        "Transfers"
    ]

    transactions.forEach(tx => {

        const row = document.createElement("tr")

        let options = ""

        categories.forEach(cat => {

            const selected =
            cat.toLowerCase() === (tx.category || "").toLowerCase().trim()
            ? "selected"
            : ""

            options += `<option value="${cat}" ${selected}>${cat}</option>`

        })

        row.innerHTML = `
        <td>${tx.date}</td>
        <td>${getCategoryIcon(tx.category)} ${tx.category}</td>
        <td>${tx.description || ""}</td>
        <td>${formatINR(tx.amount)}</td>
        <td>${tx.transaction_type || tx.type}</td>

        <td>
            <select id="cat-${tx.id}">
                ${options}
            </select>

            <button onclick="correctTransaction(${tx.id})">
                Correct
            </button>
        </td>
        `

        tbody.appendChild(row)

    })
}


async function correctTransaction(id){

    const category = document.getElementById(`cat-${id}`).value

    const res = await fetch(`${API}/transactions/${id}/correct`,{
        method:"PUT",
        headers:{
            "Authorization":"Bearer " + localStorage.getItem("token"),
            "Content-Type":"application/json"
        },
        body: JSON.stringify({
            category: category
        })
    })

    const data = await res.json()

    alert(data.message)

    loadDashboard()

}