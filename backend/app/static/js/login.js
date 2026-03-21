// =========================
// CONFIG
// =========================

const API = "http://127.0.0.1:8000"


// =========================
// LOGIN FUNCTION
// =========================

async function login() {

    // Get user inputs
    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    // Prepare form data (OAuth expects 'username' field)
    const form = new URLSearchParams()
    form.append("username", email)
    form.append("password", password)

    // Send login request
    const res = await fetch(`${API}/login`, {
        method: "POST",
        body: form
    })

    const data = await res.json()

    // Handle response
    if (data.access_token) {

        // Store token
        localStorage.setItem("token", data.access_token)

        // Redirect to dashboard
        window.location.href = "/dashboard"

    } else {
        alert("Login failed")
    }
}