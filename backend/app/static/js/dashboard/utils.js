// =========================
// FORMAT HELPERS
// =========================

function formatINR(amount) {
    return "₹" + amount.toLocaleString("en-IN")
}


// =========================
// CATEGORY ICONS
// =========================

function getCategoryIcon(category) {

    const icons = {
        Food: "🍔",
        Transport: "🚗",
        Shopping: "🛍",
        Healthcare: "🏥",
        Utilities: "💡",
        Entertainment: "🎬"
    }

    // Default fallback icon
    return icons[category] || "💳"
}