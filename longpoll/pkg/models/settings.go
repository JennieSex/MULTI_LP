package models

import (
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"lp/pkg/logging"
	"os"
	"path/filepath"
)

type Settings struct {
	UserID       int
	AutoInfector bool
	AutoVaccine  bool
}

// LoadSettings
// need to use only on create session and not after!!!
func (settings *Settings) LoadSettings(logger *logging.Logger, userId int) error {
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
		logger.Error(err)
	}

	defer db.Close()

	rows, err := db.Query(fmt.Sprintf("select uid, answering_machine, auto_vac from settings where uid=%d", userId))
	if err != nil {
		logger.Error(err)
	}

	for rows.Next() {
		rows.Scan(&settings.UserID, &settings.AutoInfector, &settings.AutoVaccine)
	}

	if settings.UserID == 0 {
		query := fmt.Sprintf(`INSERT INTO settings(uid, answering_machine, auto_vac) values('%d', %t, %t)
						ON DUPLICATE KEY UPDATE uid = VALUES(uid), answering_machine = VALUES(answering_machine), auto_vac = VALUES(auto_vac)`,
			userId, false, false)

		_, err = db.Exec(query)
		if err != nil {
			logger.Error(err)
			return err
		}
	}

	defer rows.Close()

	return nil
}
