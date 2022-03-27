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
		linkNum = -1
	} else {
		if strings.EqualFold(msgParts[1], "стоп") {
			infectEnabled = false
		} else {
			linkNum, err = strconv.Atoi(msgParts[1])
			if err != nil {
				EditMsg(vk, "⚠ Писать надо так: еб <номер ссылки>! А номер ссылки - целое число", mid, message.PeerID)
				return "",
					errors.New("invalid link number")
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
				EditMsg(vk, "👻 Остановка остановлена", message.ID, message.PeerID)
				return "", err
			}

			err := SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", id), message.ReplyMessage.ID)
			if err != nil {
				logger.Warn(err)
				time.Sleep(5 * time.Second)
				SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", id), message.ReplyMessage.ID)
			}
			time.Sleep(10 * time.Second)
		}

		SendMessage(vk, message.PeerID, "👻 Бомжи - всё.", 0)
		return "", nil
	} else {
		if len(ids) < linkNum {
			EditMsg(vk, "⚠ Произошла ошибка и виноват по любому вк", mid, message.PeerID)
			return "", errors.New("invalid ids")
		}

		SendMessage(vk, message.PeerID, fmt.Sprintf("Заразить [%s|бомжа]", ids[linkNum-1]), 0)
		infectEnabled = false
	}

	return "", err
}
