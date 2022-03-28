package main

import (
	"crypto/md5"
	"crypto/sha512"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/julienschmidt/httprouter"
)

type userData struct {
	VkID int    `json:"vk_id"`
	Role string `json:"role"`
	Name string `json:"name"`
}

type reqHandler func(w http.ResponseWriter, r *http.Request, ps httprouter.Params, user userData)

var secret = []byte("unsafe&shitty_1234")

func getRand() []byte {
	rnd := rand.New(rand.NewSource(time.Now().UnixNano()))
	b := make([]byte, rnd.Intn(30))
	for i := range b {
		b[i] = "abcdefghijklmnopqrstuvwxyz0123456789"[rnd.Intn(36)]
	}
	return b
}

func checkAuth(h reqHandler) httprouter.Handle {
	return func(w http.ResponseWriter, r *http.Request, ps httprouter.Params) {
		token, err := r.Cookie("token")
		if err != nil {
			fmt.Fprint(w, `{"status":"u/a"}`)
		}
		if user, ok := authUsers[token.Value]; ok {
			h(w, r, ps, user)
		} else {
			fmt.Fprint(w, `{"status":"u/a"}`)
		}
	}
}

func getUserData(uid int, role string, name string) (token string, uData userData) {
	user := userData{VkID: uid, Role: role, Name: name}
	jsonedUser, err := json.Marshal(user)
	if err != nil {
		panic("JSON Error!")
	}
	hasher := sha512.New()
	hasher.Write(append(append(jsonedUser, secret...), getRand()...))
	hash := hasher.Sum(nil)
	token = base64.RawStdEncoding.EncodeToString(hash)
	return token, user
}

func getAPI(w http.ResponseWriter, r *http.Request, ps httprouter.Params, user userData) {
	token, err := r.Cookie("token")
	if err != nil {
		w.WriteHeader(403)
	}
	auth := strings.Split(token.Value, ".")
	userJSON, _ := base64.RawStdEncoding.DecodeString(auth[0])
	var userData userData
	json.Unmarshal(userJSON, &userData)
	if ps.ByName("type") == "token" {
		fmt.Fprint(w, userData.Name)
	}
}

var tokenregular *regexp.Regexp

func postAPI(w http.ResponseWriter, r *http.Request, ps httprouter.Params, user userData) {
	var data map[string]string
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		panic(err)
	}
	fmt.Println(data)
	func() {
		defer func() {
			if rec := recover(); rec != nil {
				fmt.Fprint(w, rec)
			}
		}()
		if ps.ByName("type") == "token" {
			tokenme := tokenregular.FindString(data["tokenme"])
			token := tokenregular.FindString(data["token"])
			if token != "" {
				if _, err := vkMethod(token, "users.get", url.Values{}); err != 0 {
					token = "fail"
				} else {
					token = "ok"
				}
			}
			if tokenme != "" {
				if _, err := vkMethod(tokenme, "users.get", url.Values{}); err != 0 {
					tokenme = "fail"
				} else {
					tokenme = "ok"
				}
			}
			fmt.Fprintf(w, `{"status":"ok","token":"%s",tokenme:"%s"}`, token, tokenme)
		}
	}()
}

type vkAuth struct {
	Hash      string `json:"hash"`
	UID       int    `json:"uid"`
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name"`
}

var authUsers map[string]userData

func getMD5(data []byte) string {
	hasher := md5.New()
	hasher.Write(data)
	return hex.EncodeToString(hasher.Sum(nil))
}

func checkVKauth(w http.ResponseWriter, r *http.Request, p httprouter.Params) {
	var auth vkAuth
	if err := json.NewDecoder(r.Body).Decode(&auth); err != nil {
		panic(err)
	}
	fmt.Println(auth)
	toHash := append(append([]byte("7544710"), []byte(strconv.Itoa(auth.UID))...), []byte("5jf2bDiwsdIMkNWikZDX")...)
	token, user := getUserData(auth.UID, "default", auth.FirstName+" "+auth.LastName)
	if getMD5(toHash) == auth.Hash {
		authUsers[token] = user
		fmt.Fprintf(w, `{"status":"ok","token":"%s"}`, token)
	}
}

type vkResp struct {
	Response map[string]interface{} `json:"response"`
	Error    map[string]interface{} `json:"error"`
}

func vkMethod(token string, method string, query url.Values) (data map[string]interface{}, errCode float64) {
	var dat vkResp
	resp, err := http.Get(fmt.Sprintf("https://api.vk.com/method/%s?v=5.110&access_token=%s&lang=ru&%s", method, token, query.Encode()))
	if err != nil {
		return
	}
	defer resp.Body.Close()
	body, _ := ioutil.ReadAll(resp.Body)
	json.Unmarshal(body, &dat)
	if dat.Error["error_code"] != nil {
		fmt.Println(dat)
		return dat.Error, dat.Error["error_code"].(float64)
	}
	return dat.Response, 0
}

var mainHTML = `<!DOCTYPE html>
<html>
<head>
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
 <meta name="viewport" content="width=device-width, initial-scale=1">
 <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" type="text/css">
 <link rel="stylesheet" href="/styles/theme_light.css" type="text/css" id="theme">
 <link rel="stylesheet" href="/styles/style.css" type="text/css">
 <link rel="stylesheet" href="/styles/fonts.css" type="text/css">
 <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js"></script>
 <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"></script>
 <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script>
 <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
 <script src="https://vk.com/js/api/openapi.js?168"></script>
 <script src="/scripts/main.js"></script>
 <title id="title">админ блядь панель</title>
</head>
<header id="header"></header>
<body class="body">
 <div id="mainblock" class="pagecontent">
 <h1 style="font-size: 150%; font-weight: bold; text-align: center; margin: 70px;">Для работы сайта необходим javascript</h1>
</div>
</body>
<footer class="bg-light text-center text-lg-left">
<div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.2);">
Здесь могла быть <a class="text-dark" href="https://vk.com/id0">ваша</a> реклама.
</div>
</footer>
</html>`

func main() {
	println("Started!")
	authUsers = make(map[string]userData)
	tokenregular, _ = regexp.Compile(`[a-z0-9]{85}`)
	router := httprouter.New()
	router.ServeFiles("/scripts/*filepath", http.Dir("./scripts"))
	router.ServeFiles("/templates/*filepath", http.Dir("./templates"))
	router.ServeFiles("/styles/*filepath", http.Dir("./styles"))
	router.GET("/",
		func(w http.ResponseWriter, r *http.Request, _ httprouter.Params) {
			fmt.Fprint(w, mainHTML)
		})
	router.GET("/api/get/:type", checkAuth(getAPI))
	router.POST("/api/post/:type", checkAuth(postAPI))
	router.POST("/checkauth", checkVKauth)
	println("Listening...")
	log.Fatal(http.ListenAndServe(":8080", router))
}
