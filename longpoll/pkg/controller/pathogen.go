// Developer: th2empty
// Date: 18.03.2022

package controller

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	"database/sql"

	_ "github.com/go-sql-driver/mysql"

	"lp/pkg/models"

	_ "github.com/SevereCloud/vksdk/v2/api"
)

type DBConfig struct {
	Host     string `json:"host"`
	Username string `json:"username"`
	Password string `json:"password"`
	Database string `json:"database"`
}

func FindAuthoOfPathogen(token string, pid, mid int) {
	var rexPathogen *regexp.Regexp = regexp.MustCompile(`«([^)]+)»`)

	var pat string
	message, err := GetMessageByID(token, mid)
	if err != nil {
		log.Printf("\033[31m [ERROR]: config file is filled incorrectly")
		EditMsg(token, fmt.Sprintf("❗ Произошла следующая ошибка: %s", err.Error()), mid, pid)
		return
	}

	if len(strings.Split(message.Text, " ")) == 1 {
		if message.ReplyMessage == nil {
			EditMsg(token, "🤡 А что искать?", mid, pid)
			return
		}
		fwdText := message.ReplyMessage.Text
		pat = rexPathogen.FindString(fwdText)
		pat = strings.Replace(pat, "«", "", -1)
		pat = strings.Replace(pat, "»", "", -1)
		if len(pat) == 0 {
			EditMsg(token, "🤡 А что искать?", mid, pid)
			return
		}
	} else {
		cmdPrefix := strings.Split(message.Text, " ")[0] + " "
		pat = strings.Replace(message.Text, cmdPrefix, "", -1)
	}

	var ex, _ = os.Executable()
	var exPath = filepath.Dir(ex)
	var config DBConfig

	var f = exPath + "/configs/mysql_conn.json"
	fData, err := ioutil.ReadFile(f)
	if err != nil {
		panic("\033[31m [FATAL ERROR]: failed to read file 'mysql_conn.json', no such file")
	}

	err = json.Unmarshal(fData, &config)
	if err != nil {
		log.Printf("\033[31m [ERROR]: config file is filled incorrectly")
		return
	}

	connData := fmt.Sprintf("%s:%s@tcp(127.0.0.1:3306)/%s", config.Username, config.Password, config.Database)
	db, err := sql.Open("mysql", connData)
	if err != nil {
		log.Printf("\033[31m [ERROR]: %s", err.Error())
	}

	defer db.Close()

	query := fmt.Sprintf(`SELECT name, author_id, author_name, upd_date from pathogens where name='%s'`, pat)

	rows, err := db.Query(query)
	if err != nil {
		log.Printf("\033[31m [ERROR]: %s", err.Error())
	}

	defer rows.Close()

	var pathogen models.Pathogen
	var objs []models.Pathogen
	for rows.Next() {
		rows.Scan(&pathogen.Name, &pathogen.AuthorID, &pathogen.AuthorName, &pathogen.UpdateDate)
		objs = append(objs, pathogen)
	}

	if len(objs) == 0 {
		EditMsg(token, fmt.Sprintf("🔍 Не удалось найти ни единого упоминания болезни «%s»", pat), mid, pid)
		return
	}

	info := fmt.Sprintf("💩 Патоген: «%s»\n🐓 Гигант мыслей: [id%d|%s]\n💾 Обновлен: %s",
		pathogen.Name, pathogen.AuthorID, pathogen.AuthorName,
		time.Unix(pathogen.UpdateDate, 0).Format("02.01.2006"))

	EditMsg(token, info, mid, pid)
	return
}
