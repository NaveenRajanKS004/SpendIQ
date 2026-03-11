function renderTransactions(transactions){

    const tbody = document.querySelector("#transactionTable tbody")

    tbody.innerHTML = ""

    transactions.forEach(tx=>{

        const row = document.createElement("tr")

        row.innerHTML = `
        <td>${tx.date}</td>
        <td>${getCategoryIcon(tx.category)} ${tx.category}</td>
        <td>${tx.description || ""}</td>
        <td>${formatINR(tx.amount)}</td>
        <td>${tx.type}</td>
        `

        tbody.appendChild(row)

    })

}