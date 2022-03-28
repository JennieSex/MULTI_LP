// Developer: th2empty
// Date: 18.03.2022

package controller

import (
	"errors"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"lp/pkg/logging"
	"lp/pkg/models"
	"strings"

	"lp/pkg/utils"
)

// CommandHandler
// monitors for new messages and executes a command if identified.
// Returns error
func CommandHandler(logger *logging.Logger, token string, s *map[string]models.Settings, message string, pid int, mid int, ownerId int) error {
	var (
		_key      = fmt.Sprintf("id%d", ownerId)
		_settings = *s
		_         = _settings[_key]

		vk           = api.NewVK(token)
		messageParts = strings.Split(message, " ")
		answer       string
	)

	if len(messageParts) == 0 {
		return errors.New("invalid message")
	}

	switch true {
	case utils.HasString(messageParts[0], GetLabAliases):
		answer = GetLab(token, logger)
	case utils.HasString(messageParts[0], FindPathogenAliases):
		answer = FindAuthorOfPathogen(logger, vk, mid, ownerId)
	case utils.HasString(messageParts[0], FinInfectionsAliases):
		answer = FindInfections(logger, vk, mid, ownerId, -1)
	case utils.HasString(messageParts[0], InfectAliases):
		go InfectUsers(vk, mid, logger)
	default:
		return nil
	}

	if len(answer) != 0 {
		EditMsg(vk, answer, mid, pid)
	}

	return nil
}
