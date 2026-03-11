function requireLogin() {

    const token = localStorage.getItem("token")

    if (!token) {

        window.location.replace("/login-page")

    }

}

requireLogin()