function passwordsMatch () {
    return $("#password").val() == $("#password-retype").val();
}

$("#register-form").submit(function (event) {
    if(!passwordsMatch()) {
        alert("The passwords you entered do not match.");
        event.preventDefault();
    }
});