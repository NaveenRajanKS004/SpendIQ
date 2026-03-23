// =========================
// CONFIG
// =========================

const API = "http://127.0.0.1:8000"
const token = localStorage.getItem("token")

const headers = {
    "Authorization": "Bearer " + token
}


// =========================
// INIT (ENTRY POINT)
// =========================

window.onload = () => {
    console.log("✅ JS loaded")

    loadProfile()
    setupUpload()
}


// =========================
// LOAD PROFILE
// =========================

async function loadProfile() {

    console.log("➡️ Loading profile...")

    try {
        const res = await fetch(`${API}/me`, { headers })

        if (!res.ok) {
            alert("Failed to load profile")
            return
        }

        const data = await res.json()
        console.log("PROFILE DATA:", data)

        document.getElementById("name").innerText = data.name || "-"
        document.getElementById("email").innerText = data.email || "-"
        document.getElementById("phone").innerText = data.phone || "-"
        document.getElementById("age").innerText =
            data.date_of_birth
                ? new Date().getFullYear() - new Date(data.date_of_birth).getFullYear()
                : "-"

        if (data.profile_picture) {
            document.getElementById("profilePic").src = data.profile_picture
        }

        enableInlineEdit()

    } catch (err) {
        console.error("❌ loadProfile failed:", err)
    }
}


// =========================
// INLINE EDIT
// =========================

function enableInlineEdit() {

    document.querySelectorAll(".editable").forEach(el => {

        el.onclick = () => {

            const field = el.dataset.field
            const oldValue = el.innerText

            const input = document.createElement("input")
            input.value = oldValue
            input.className = "inline-input"

            el.replaceWith(input)
            input.focus()

            input.onblur = async () => {

                const newValue = input.value || oldValue

                const span = document.createElement("span")
                span.className = "editable"
                span.dataset.field = field
                span.id = field
                span.innerText = newValue

                input.replaceWith(span)

                if (newValue !== oldValue) {
                    await fetch(`${API}/profile`, {
                        method: "PUT",
                        headers: {
                            ...headers,
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ [field]: newValue })
                    })
                }

                enableInlineEdit()
            }
        }
    })
}


// =========================
// UPLOAD SETUP
// =========================

function setupUpload() {

    const input = document.getElementById("picUpload")

    if (!input) {
        console.error("❌ picUpload not found")
        return
    }

    input.onchange = async function () {

        console.log("📤 Upload triggered")

        const file = this.files[0]
        if (!file) return

        document.getElementById("profilePic").src = URL.createObjectURL(file)

        const formData = new FormData()
        formData.append("file", file)

        try {
            const res = await fetch(`${API}/profile/upload-picture`, {
                method: "POST",
                headers,
                body: formData
            })

            const data = await res.json()
            console.log("UPLOAD RESPONSE:", data)

        } catch (err) {
            console.error("❌ Upload failed:", err)
        }
    }
}


// =========================
// CHANGE PASSWORD
// =========================

async function changePassword() {

    const old_password = document.getElementById("oldPassword").value
    const new_password = document.getElementById("newPassword").value

    try {
        const res = await fetch(`${API}/change-password`, {
            method: "PUT",
            headers: {
                ...headers,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                old_password,
                new_password
            })
        })

        const data = await res.json()

        if (res.ok) {
            alert("Password changed successfully")
        } else {
            alert(data.detail || "Failed to change password")
        }

    } catch (err) {
        console.error(err)
        alert("Network error")
    }
}


// =========================
// TRIGGER FILE PICKER
// =========================

function triggerUpload() {
    document.getElementById("picUpload").click()
}