// Developer: th2empty
// Date: 29.03.2022

package models

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"io/ioutil"
	"lp/pkg/logging"
	"lp/pkg/util"
	"os"
	"path/filepath"
	"regexp"
	"time"
)

type AutoVaccine struct {
	UserId  int
	VK      *api.VK
	Enabled bool
	Logger  *logging.Logger
}

func (m *AutoVaccine) Enable() error {
	m.Enabled = true
	return m.update()
}

func (m *AutoVaccine) Disable() error {
	m.Enabled = false
	return m.update()
}

func (m *AutoVaccine) update() error {
	var ex, _ = os.Executable()
	var exPath = filepath.Dir(ex)
	var config DBConfig

	var f = exPath + "/configs/mysql_conn.json"
	var fData, err = ioutil.ReadFile(f)
	if err != nil {
		return errors.New("failed to read file 'mysql_conn.json', no such file")
	}

	err = json.Unmarshal(fData, &config)
	if err != nil {
		return err
	}

	connData := fmt.Sprintf("%s:%s@tcp(127.0.0.1:3306)/%s", config.Username, config.Password, config.Database)
	db, err := sql.Open("mysql", connData)
	if err != nil {
		m.Logger.Error(err)
	}

	defer db.Close()

	query := fmt.Sprintf(`UPDATE settings SET auto_vac = %t WHERE uid = %d`,
		m.Enabled, m.UserId)

	_, err = db.Exec(query)
	if err != nil {
		m.Logger.Error(err)
		return err
	}

	return nil
}

// Go
// @param message - message text from event @NewMessage
func (m *AutoVaccine) Go(message string) error {
	if !m.Enabled {
		return nil
	}

	var (
		rexTrigger = regexp.MustCompile("([^)]+) заражению ([^)]+)")
		//rexNumberId = regexp.MustCompile("id[0-9]+")
		//allIds      = rexNumberId.FindAllString(message, -1)
	)

	if len(rexTrigger.FindString(message)) == 0 {
		return nil
	}

	time.Sleep(5 * time.Second)

	id, err := m.VK.MessagesSend(api.Params{"random_id": 0, "peer_id": -174105461, "message": "!купить вакцину"})
	if err != nil {
		m.Logger.Error(err)
	}

	time.Sleep(10 * time.Second)

	err = util.DeleteMessages(m.VK, id, 2, m.Logger)
	if err != nil {
		m.Logger.Error(err)
	}

	return err
}
