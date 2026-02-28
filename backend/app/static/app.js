// ==============================
// AUTH TOKEN CHECK
// ==============================

const token = localStorage.getItem("token");

if (!token) {
    window.location.href = "/login-page";
}

// Store transactions globally for search filtering
let allTransactions = [];

// ==============================
// LOAD SUMMARY
// ==============================

async function loadSummary() {
    const response = await fetch("/summary", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        console.error("Summary fetch failed");
        return;
    }

    const data = await response.json();

    animateValue("income", data.total_income);
    animateValue("expense", data.total_expense);
    animateValue("balance", data.balance);
}

// ==============================
// LOAD INSIGHTS
// ==============================

async function loadInsights() {
    const response = await fetch("/summary/insights", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        console.error("Insights fetch failed");
        return;
    }

    const data = await response.json();

    document.getElementById("totalTransactions").innerText =
        data.total_transactions;

    document.getElementById("topCategory").innerText =
        data.top_category || "-";

    document.getElementById("highestExpense").innerText =
        `₹${data.highest_expense}`;
        // Generate smart AI insight sentence
let insightText = "";

if (data.top_category) {
    insightText += `You spent most on ${data.top_category}. `;
}

if (data.highest_expense > 0) {
    insightText += `Your highest single expense was ₹${data.highest_expense}.`;
}

const insightElement = document.getElementById("aiInsight");
if (insightElement) {
    insightElement.innerText = insightText;
}
}

// ==============================
// LOAD TRANSACTIONS
// ==============================

async function loadTransactions() {
    const response = await fetch("/transactions", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        console.error("Transactions fetch failed");
        return;
    }

    const transactions = await response.json();
    allTransactions = transactions;

    const emptyMessage = document.getElementById("emptyMessage");

    if (transactions.length === 0) {
        emptyMessage.style.display = "block";
    } else {
        emptyMessage.style.display = "none";
    }

    renderTransactions(transactions);
}

// ==============================
// RENDER TRANSACTIONS
// ==============================

function renderTransactions(transactions) {
    const tableBody = document.querySelector("#transactionTable tbody");
    tableBody.innerHTML = "";

    transactions.forEach(txn => {

        const amountClass =
            txn.transaction_type === "expense"
                ? "amount-expense"
                : "amount-income";

        const rowClass =
            txn.transaction_type === "expense"
                ? "row-expense"
                : "row-income";

        const row = document.createElement("tr");
        row.className = rowClass;

        row.innerHTML = `
            <td>${new Date(txn.created_at).toLocaleDateString()}</td>
            <td>${txn.description}</td>
            <td>
                <span class="category-badge">
                    ${txn.category}
                </span>
            </td>
            <td class="${amountClass}">
                ₹${txn.amount}
            </td>
            <td>${txn.transaction_type}</td>
            <td>
                <button class="correct-btn" data-id="${txn.id}">
                    Correct
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Attach event listeners AFTER rows are added
    document.querySelectorAll(".correct-btn").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.getAttribute("data-id");
            correctTransaction(id);
        });
    });
}

// ==============================
// LOAD CATEGORY CHART
// ==============================

let categoryChartInstance = null;

async function loadCategoryChart() {
    const response = await fetch("/summary/categories", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        console.error("Category summary fetch failed");
        return;
    }

    const data = await response.json();

    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }

    const values = Object.values(data);
    const labels = Object.keys(data);
    const total = values.reduce((a, b) => a + b, 0);

    categoryChartInstance = new Chart(
        document.getElementById("categoryChart"),
        {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                layout: {
                    padding: {
                        top: 20,
                        bottom: 20,
                        left: 20,
                        right: 20
                    }
                },

                plugins: {
                    legend: {
                        display: false
                    },
                    datalabels: {
                        color: '#1f2937',
                        font: {
                            weight: '600',
                            size: 11
                        },
                        formatter: (value, context) => {
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${context.chart.data.labels[context.dataIndex]} ${percentage}%`;
                        },
                        anchor: 'end',
                        align: 'end',
                        offset: 14,
                        clip: false
                    }
                },

                radius: '68%',   // slightly adjusted for balance

                animation: {
                    duration: 800
                }
            },
            plugins: [ChartDataLabels]
        }
    );
}

// ==============================
// LOAD MONTHLY CHART
// ==============================

let monthlyChartInstance = null;

async function loadMonthlyChart() {
    const response = await fetch("/summary/monthly", {
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        console.error("Monthly summary fetch failed");
        return;
    }

    const data = await response.json();

    const months = Object.keys(data);
    const income = months.map(m => data[m].income);
    const expense = months.map(m => data[m].expense);

    if (monthlyChartInstance) {
        monthlyChartInstance.destroy();
    }

    monthlyChartInstance = new Chart(
        document.getElementById("monthlyChart"),
        {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    {
                        label: "Income",
                        data: income,
                        backgroundColor: "#1abc9c",
                        barPercentage: 0.6,
                        categoryPercentage: 0.6
                    },
                    {
                        label: "Expense",
                        data: expense,
                        backgroundColor: "#ff6b6b",
                        barPercentage: 0.6,
                        categoryPercentage: 0.6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,

                layout: {
                    padding: {
                        bottom: 20
                    }
                },

                plugins: {
                    legend: {
                        position: 'top'
                    }
                },

                scales: {
                    x: {
                        ticks: {
                            padding: 10
                        }
                    },
                    y: {
                        beginAtZero: true
                    }
                },

                animation: {
                    duration: 800
                }
            }
        }
    );
}

// ==============================
// LOGOUT
// ==============================

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login-page";
}

// ==============================
// CORRECT TRANSACTION
// ==============================

async function correctTransaction(id) {
    const newCategory = prompt("Enter correct category:");

    if (!newCategory) return;

    const response = await fetch(`/transactions/${id}/correct`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            corrected_category: newCategory
        })
    });

    if (response.ok) {
        alert("Category updated!");

        loadSummary();
        loadTransactions();
        loadCategoryChart();
        loadMonthlyChart();
        loadInsights();
    } else {
        alert("Correction failed.");
    }
}

// ==============================
// UPLOAD CSV
// ==============================

async function uploadCSV(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/transactions/upload", {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${token}`
        },
        body: formData
    });

    const data = await response.json();

    if (response.ok) {
        alert(`Uploaded ${data.transactions_inserted} transactions`);

        loadSummary();
        loadTransactions();
        loadCategoryChart();
        loadMonthlyChart();
        loadInsights();
    } else {
        alert("Upload failed");
        console.error(data);
    }
}

// ==============================
// INIT + EVENT WIRING
// ==============================

document.addEventListener("DOMContentLoaded", () => {
    const uploadBtn = document.getElementById("uploadBtn");
    const csvFile = document.getElementById("csvFile");
    const searchInput = document.getElementById("searchInput");

    if (uploadBtn && csvFile) {
        uploadBtn.addEventListener("click", () => {
            csvFile.click();
        });

        csvFile.addEventListener("change", uploadCSV);
    }

    // Live search filtering
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.toLowerCase();

            const filtered = allTransactions.filter(txn =>
                txn.description.toLowerCase().includes(query) ||
                txn.category.toLowerCase().includes(query) ||
                txn.transaction_type.toLowerCase().includes(query)
            );

            renderTransactions(filtered);
        });
    }

        let sortAscending = true;

    const amountHeader = document.getElementById("amountHeader");

    if (amountHeader) {
        amountHeader.addEventListener("click", () => {
            sortAscending = !sortAscending;

            const sorted = [...allTransactions].sort((a, b) => {
                return sortAscending
                    ? a.amount - b.amount
                    : b.amount - a.amount;
            });

            renderTransactions(sorted);
        });
    }

    loadSummary();
    loadTransactions();
    loadCategoryChart();
    loadMonthlyChart();
    loadInsights();
});

// ==============================
// ANIMATED COUNTER
// ==============================

function animateValue(id, endValue) {
    const element = document.getElementById(id);
    const duration = 800;
    const startValue = 0;
    const increment = endValue / (duration / 16);

    let current = startValue;

    const counter = setInterval(() => {
        current += increment;

        if ((increment > 0 && current >= endValue) ||
            (increment < 0 && current <= endValue)) {
            element.innerText = `₹${endValue}`;
            clearInterval(counter);
        } else {
            element.innerText = `₹${Math.floor(current)}`;
        }
    }, 16);
}