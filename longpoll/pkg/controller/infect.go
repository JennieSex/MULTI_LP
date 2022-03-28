// Developer: th2empty
// Date: 27.03.2022

package controller

import (
	"errors"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"lp/pkg/logging"
	"regexp"
	"strconv"
	"strings"
	"time"
)

var (
	infectEnabled = false
)

// InfectUsers
// infects a user or users by their id
func InfectUsers(vk *api.VK, mid int, logger *logging.Logger) (string, error) {
	var message, err = GetMessageByID(vk, mid)
	if err != nil {
		logger.Error(err)
	}

	var (
		rexID    = regexp.MustCompile(`id[0-9]+`)
		msgParts = strings.Split(strings.ToLower(message.Text), " ")
		ids      []string
		linkNum  int
	)

	if len(msgParts) < 2 {
		if message.ReplyMessage.FromID < 0 {
			logger.Infof("@id%d attempt to infect a group club%d", message.FromID, message.ReplyMessage.FromID)
			return "", errors.New("attempt to infect a group")
		}

		if message.FromID == message.ReplyMessage.FromID {
			logger.Infof("@id%d tried to infect himself", message.FromID)
			EditMsg(vk,
				"🔪 Нож видишь? Пока он в моей руке. Но ещё один такой рофл и будет он уже в тебе.",
				mid, message.PeerID)
			return "", nil
		}

		err := SendMessage(vk, message.PeerID,
			fmt.Sprintf("Заразить [id%d|бомжа]", message.ReplyMessage.FromID), message.ReplyMessage.ID)
		if err != nil {
			logger.Error(err)
			return "", err
		}

		return "", nil
	} else if strings.EqualFold(msgParts[1], "всех") {
		linkNum = -1
	} else {
		if strings.EqualFold(msgParts[1], "стоп") {
			infectEnabled = false
			EditMsg(vk, "👻 Остановка остановлена", message.ID, message.PeerID)
		} else {
			linkNum, err = strconv.Atoi(msgParts[1])
			if err != nil {
				err = SendMessage(vk, message.PeerID,
					fmt.Sprintf("Заразить %s", msgParts[1]), 0)
				if err != nil {
					logger.Error(err)
					return "", err
				}
			}
		}
	}

	if message.ReplyMessage != nil {
		ids = rexID.FindAllString(message.ReplyMessage.Text, -1)
	} else {
		ids = rexID.FindAllString(message.Text, -1)
	}

	if linkNum == -1 {
		infectEnabled = true
		EditMsg(vk,
			fmt.Sprintf("🔪 Режим мясорубка -> on\n👻 Хреначим всех подряд\n💩 Всего целей: %d", len(ids)),
			mid, message.PeerID)
		logger.Debug(ids)
		for _, id := range ids {
			if !infectEnabled {
				return "", err
			}

			if id == fmt.Sprintf("id%d", message.FromID) {
				logger.Infof("@%s started mass infection and [ids] contains him id; skipping iteration", id)
				continue
			}

			err := SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", id), message.ReplyMessage.ID)
			if err != nil {
				logger.Warn(err)
				time.Sleep(5 * time.Second)
				err := SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", id), message.ReplyMessage.ID)
				if err != nil {
					logger.Warn(err)
					return "", err
				}
			}
			time.Sleep(10 * time.Second)
		}

		err := SendMessage(vk, message.PeerID, "👻 Бомжи - всё.", 0)
		if err != nil {
			logger.Warn(err)
			return "", err
		}
		return "", nil
	} else {
		if len(ids) < linkNum {
			EditMsg(vk, "⚠ Где-то ты в жизни не туда свернул...", mid, message.PeerID)
			return "", errors.New("invalid ids")
		}

		if linkNum <= 0 {
			return "", nil
		}

		err := SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", ids[linkNum-1]), 0)
		if err != nil {
			logger.Warn(err)
			return "", err
		}
		infectEnabled = false
	}

	return "", err
}
