function formatINR(amount) {
    return "₹" + amount.toLocaleString("en-IN")
}

function getCategoryIcon(category){

    const icons = {
        Food:"🍔",
        Transport:"🚗",
        Shopping:"🛍",
        Healthcare:"🏥",
        Utilities:"💡",
        Entertainment:"🎬"
    }

    return icons[category] || "💳"
}