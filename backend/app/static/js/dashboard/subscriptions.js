// =========================
// LOAD SUBSCRIPTIONS
// =========================

async function loadSubscriptions() {

    const list = document.getElementById("subscriptionList")

    try {
        // Fetch recurring subscriptions
        const res = await fetch(`${API}/subscriptions`, { headers })

        // If endpoint fails silently, do nothing
        if (!res.ok) return

        const data = await res.json()

        // Clear previous list
        list.innerHTML = ""

        // Render subscriptions
        data.forEach(sub => {

            const li = document.createElement("li")

            li.innerText = `🔁 ${sub.description} — ${formatINR(sub.amount)}`

            list.appendChild(li)
        })

    } catch (err) {
        // Fail gracefully (backend may not be available)
        console.log("Subscription endpoint unavailable")
    }
}