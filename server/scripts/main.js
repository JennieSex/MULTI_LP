"use strict";

function loadHTML(src) {
    return new Promise(function(resolve, reject) {
        let xhttp = new XMLHttpRequest();
        xhttp.onloadend = function() {
            if (this.readyState == 4 && this.status == 200) {
                resolve(this.responseText);
            } else {
                reject(new Error(this.statusText));
            }
        };
        xhttp.open("GET", src, true);
        xhttp.send();
    });
}

function postData(type, data, funcSuccess, funcFail) {
    let check = new XMLHttpRequest();
    check.onloadend = function() {
        if (this.readyState == 4 && this.status == 200) {
            let response = JSON.parse(this.responseText);
            if (response['status'] == "ok") {
                funcSuccess(response)
            } else if (response['status'] == "u/a") {
                failAuth()
            }
        }
    };
    check.open("POST", `/api/post/${type}`);
    check.send(JSON.stringify(data));
}

function render(template, func) {
    setContent(template)
}

function failAuth() {}

function getTokens() {
    getData("token", (response) => {
        document.getElementById('token').setAttribute("value", response['token']);
        document.getElementById('tokenme').setAttribute("value", response['tokenme']);
    }, failAuth)
}

function toggleInputs(ids, enable) {
    ids.forEach(item => {
        document.getElementById(item).disabled = !enable;
    });
}

function sendTokens() {
    const token = document.getElementById('token');
    const tokenme = document.getElementById('tokenme');
    const button = document.getElementById('tokenconfirm');
    toggleInputs(['token', 'tokenme'], false)
    button.setAttribute("disabled", "disabled");
    postData("token", {
            token: token.getAttribute('value'),
            tokenme: tokenme.getAttribute('value')
        },
        () => {
            toggleInputs(['token', 'tokenme'], true)
            button.removeAttribute("disabled");
            getTokens()
        },
        () => {})
}

function getData(type, funcSuccess, funcFail) {
    let check = new XMLHttpRequest();
    check.onload = function() {
        let response = JSON.parse(this.responseText);
        if (response['status'] == "ok") {
            funcSuccess(response);
        } else {
            funcFail(response);
        }
    }
    check.open("GET", `/api/get/${type}`);
    check.send();
}

function getRender(template, func) {
    let check = new XMLHttpRequest();
    check.onload = function() {
        if (this.readyState == 4 && this.status == 200) {
            render(this.responseText, func);
        } else console.log(this.response);
    }
    check.onerror = () => alert('Попробуй еще раз.');
    check.open("GET", `/templates/${template}.html`);
    check.send();
}

function setContent(text) {
    let content = document.getElementById("mainblock");
    content.innerHTML = text;
}

function setByID(name, text) {
    let content = document.getElementById(name);
    content.innerHTML = text;
}

function loadLogin() {
    loadHTML(`/templates/login.html`).then(result => {
        setContent(result);
        import ("/scripts/login.js")
    }, error => alert(error))
}

function loadPage(name) {
    loadHTML(`/templates/${name}.html`).then(result => {
        setContent(result);
    }, error => alert(error))
}

function setTheme(name) {
    document.getElementById('theme').href = `/styles/theme_${name}.css`;
}

loadHTML("/templates/header.html").then(result => {
    setByID("header", result);
}, error => alert(error))

loadHTML("/templates/index.html").then(result => setContent(result), error => alert(error))

var app = new Vue({
    el: '#mainblock',
    data: {
        token_main: 'Здесь могла быть ваша реклама, но здесь ваш токен'
    }
})