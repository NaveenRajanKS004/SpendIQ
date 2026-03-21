// =========================
// AUTH GUARD
// =========================

function requireLogin() {

    const token = localStorage.getItem("token")

    // If no token → redirect to login
    if (!token) {
        window.location.replace("/login-page")
    }
}


// =========================
// INITIAL CHECK
// =========================

// Run immediately on page load
requireLogin()