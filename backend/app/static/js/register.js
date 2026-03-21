// =========================
// CONFIG
// =========================

const API = "http://127.0.0.1:8000"


// =========================
// REGISTER FUNCTION
// =========================

async function register() {

    // Get user inputs
    const name = document.getElementById("name").value
    const email = document.getElementById("email").value
    const phone = document.getElementById("phone").value
    const dob = document.getElementById("dob").value
    const password = document.getElementById("password").value

    // Send registration request
    const res = await fetch(`${API}/register`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            email,
            phone,
            date_of_birth: dob,
            password
        })
    })

    // Handle response
    if (res.status === 200) {

        alert("Account created. Please login.")

        window.location.href = "/login-page"

    } else {

        const err = await res.json()

        alert(err.detail || "Registration failed")
    }
}