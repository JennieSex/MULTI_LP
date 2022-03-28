VK.init({ apiId: 7544710 });
VK.Widgets.Auth("vk_auth", { "onAuth": data => checkAuth(data) });

async function checkAuth(data) {
    let check = new XMLHttpRequest();
    check.onloadend = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response['status'] == "ok") {
                loadPage('index');
                document.cookie = `token=${response['token']}`
            } else {
                alert('Авторизация не удалась. Попробуй еще раз.');
            }
        }
    };
    check.onerror = () => alert('Авторизация не удалась. Попробуй еще раз.');
    check.open("POST", "/checkauth");
    check.send(JSON.stringify(data));
}