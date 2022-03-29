package controller

import (
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"lp/pkg/logging"
	"regexp"
	"strings"
	"time"
)

type AnswerMachine struct {
	UserId  int
	VK      *api.VK
	Enabled bool
	Logger  *logging.Logger
}

func (m *AnswerMachine) Enable() {
	m.Enabled = true
	return
}

func (m *AnswerMachine) Disable() {
	m.Enabled = false
	return
}

// Go
// @param message - message text from event @NewMessage
func (m *AnswerMachine) Go(message string, pid uint64) error {
	if !m.Enabled {
		return nil
	}

	var (
		rexTrigger  = regexp.MustCompile("Служба безопасности лаборатории")
		rexNumberId = regexp.MustCompile("id[0-9]+")
		allIds      = rexNumberId.FindAllString(message, -1)
	)

	if len(rexTrigger.FindString(message)) == 0 {
		return nil
	}

	if !strings.Contains(message, fmt.Sprintf("id%d", m.UserId)) {
		return nil
	}

	var valiantId string
	var err error
	for _, id := range allIds {
		if !(strings.Contains(id, fmt.Sprintf("%d", m.UserId))) {
			valiantId = rexNumberId.FindString(id)
			break
		}
	}

	var commands = []string{"!купить вакцину",
		fmt.Sprintf("Заразить [%s|ничтожество]\nЗнай свое место...", valiantId)}
	time.Sleep(5 * time.Second)

	for _, command := range commands {
		_, err = m.VK.MessagesSend(api.Params{"random_id": 0, "peer_id": pid, "message": command})
		if err != nil {
			m.Logger.Error(err)
		}

		time.Sleep(10 * time.Second)
	}

	return err
}