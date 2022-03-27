// Developer: th2empty
// Date: 18.03.2022

package controller

import (
	"encoding/json"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"io/ioutil"
	"lp/pkg/logging"
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

func FindAuthorOfPathogen(logger *logging.Logger, vk *api.VK, mid, ownerId int) string {
	var rexPathogen = regexp.MustCompile(`«([^)]+)»`)

	var pat string
	message, err := GetMessageByID(vk, mid)
	if err != nil {
		logger.Error(err)
		return "❗ Произошла следующая ошибка: %s\", err.Error()"
	}

	if len(strings.Split(message.Text, " ")) == 1 {
		if message.ReplyMessage == nil {
			return "🤡 А что искать?"
		}
		fwdText := message.ReplyMessage.Text
		pat = rexPathogen.FindString(fwdText)
		pat = strings.Replace(pat, "«", "", -1)
		pat = strings.Replace(pat, "»", "", -1)
		if len(pat) == 0 {
			return "🤡 А что искать?"
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
		logger.Fatal("config file is filled incorrectly")
		return "[FATAL ERROR]: config file is filled incorrectly"
	}

	connData := fmt.Sprintf("%s:%s@tcp(127.0.0.1:3306)/%s", config.Username, config.Password, config.Database)
	db, err := sql.Open("mysql", connData)
	if err != nil {
		logger.Fatal(err)
	}

	defer db.Close()

	query := fmt.Sprintf(`SELECT name, author_id, author_name, upd_date from pathogens where name='%s'`, pat)

	rows, err := db.Query(query)
	if err != nil {
		logger.Error(err)
	}

	defer rows.Close()

	var pathogen models.Pathogen
	var objs []models.Pathogen
	for rows.Next() {
		rows.Scan(&pathogen.Name, &pathogen.AuthorID, &pathogen.AuthorName, &pathogen.UpdateDate)
		objs = append(objs, pathogen)
	}

	if len(objs) == 0 {
		return fmt.Sprintf("🔍 Не удалось найти ни единого упоминания болезни «%s»", pat)
	}

	info := fmt.Sprintf("💩 Патоген: «%s»\n🐓 Гигант мыслей: [id%d|%s]\n💾 Обновлен: %s\n\n",
		pathogen.Name, pathogen.AuthorID, pathogen.AuthorName,
		time.Unix(pathogen.UpdateDate, 0).Format("02.01.2006"))

	infections := FindInfections(logger, vk, mid, ownerId, pathogen.AuthorID)
	info += infections

	return info
}
