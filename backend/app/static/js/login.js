const API = "http://127.0.0.1:8000"

async function login() {

    const email = document.getElementById("email").value
    const password = document.getElementById("password").value

    const form = new URLSearchParams()
    form.append("username", email)
    form.append("password", password)

    const res = await fetch(`${API}/login`, {
        method: "POST",
        body: form
    })

    const data = await res.json()

    if (data.access_token) {

        localStorage.setItem("token", data.access_token)

        window.location.href = "/dashboard"

    } else {

        alert("Login failed")

    }

}