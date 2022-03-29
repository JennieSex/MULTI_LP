// Developer: th2empty
// Date: 18.03.2022

package controller

import (
	"errors"
	"github.com/SevereCloud/vksdk/v2/api"
	"lp/pkg/logging"
	"lp/pkg/models"
	"strings"

	"lp/pkg/utils"
)

type CommandHandler struct {
	Logger     *logging.Logger
	OwnerId    int
	Prefix     string
	VK         *api.VK
	AnsMachine *models.AnsweringMachine
	AutoVac    *models.AutoVaccine
	Settings   *map[string]models.Settings
}

// IdentifyAndExec
// monitors for new messages and executes a command if identified.
// Returns error
func (h *CommandHandler) IdentifyAndExec(message string, pid int, mid int) error {

	message = strings.Replace(message, h.Prefix, "", 1)
	var (
		messageParts = strings.Split(message, " ")
		answer       string
	)

	if len(messageParts) == 0 {
		return errors.New("invalid message")
	}

	switch true {
	case utils.HasString(messageParts[0], GetLabAliases):
		answer = GetLab(h.VK, h.Logger)
	case utils.HasString(messageParts[0], FindPathogenAliases):
		answer = FindAuthorOfPathogen(h.Logger, h.VK, mid, h.OwnerId)
	case utils.HasString(messageParts[0], FinInfectionsAliases):
		answer = FindInfections(h.Logger, h.VK, mid, h.OwnerId, -1)
	case utils.HasString(messageParts[0], InfectAliases):
		go InfectUsers(h.VK, mid, h.Logger)
	case utils.HasString(messageParts[0], EnableAnsweringMachine):
		answer = h.updateAnsweringMachineSettings(true)
	case utils.HasString(messageParts[0], DisableAnsweringMachine):
		answer = h.updateAnsweringMachineSettings(false)
	case utils.HasString(messageParts[0], EnableAutoVaccine):
		answer = h.updateAutoVaccineSettings(true)
	case utils.HasString(messageParts[0], DisableAutoVaccine):
		answer = h.updateAutoVaccineSettings(false)
	default:
		return nil
	}

	if len(answer) != 0 {
		EditMsg(h.VK, answer, mid, pid)
	}

	return nil
}

func (h *CommandHandler) updateAnsweringMachineSettings(b bool) string {
	var err error
	if b {
		if h.AutoVac.Enabled {
			return "👿 Нельзя использовать автовакцину и автоответчик одновременно"
		}
		err = h.AnsMachine.Enable()
	} else {
		err = h.AnsMachine.Disable()
	}

	if err != nil {
		h.Logger.Error(err)
		return "🕯 Не удалось обновить настройки"
	} else {
		if b {
			return "🤖 Автоответчик активирован... Бойтесь хейтеры"
		} else {
			return "🤖 Автоответчик деактивирован..."
		}
	}
}

func (h *CommandHandler) updateAutoVaccineSettings(b bool) string {
	var err error
	if b {
		if h.AnsMachine.Enabled {
			return "👿 Нельзя использовать автовакцину и автоответчик одновременно"
		}
		err = h.AutoVac.Enable()
	} else {
		err = h.AutoVac.Disable()
	}

	if err != nil {
		h.Logger.Error(err)
		return "🕯 Не удалось обновить настройки"
	}

	if b {
		return "🤖 Автовакцина активирована"
	} else {
		return "🤖 Автовакцина деактивирована"
	}
}
