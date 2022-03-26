// Developer: th2empty
// Date: 18.03.2022

package controller

import (
	"errors"
	"strings"

	"lp/pkg/utils"
)

func IdentifyCommand(token string, message string, pid int, mid int) error {
	messageParts := strings.Split(message, " ")
	if len(messageParts) == 0 {
		return errors.New("invalid message")
	}

	switch true {
	case utils.HasString(messageParts[0], GET_LAB):
		GetLab(token, mid, pid)
	case utils.HasString(messageParts[0], FIND_PAT):
		FindAuthoOfPathogen(token, pid, mid)
	}

	return nil
}
