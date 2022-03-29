// Developer: th2empty
// Date: 17.03.2022

package controller

import (
	"errors"
	"fmt"
	"lp/pkg/logging"
	"lp/pkg/util"
	"regexp"
	"strings"
	"time"

	"lp/pkg/models"

	"github.com/SevereCloud/vksdk/v2/api"
)

func ParseLab(vk *api.VK, peerId int) (models.Laboratory, error) {
	messagesHistory, err := util.GetMessagesHistory(vk, peerId)
	if err != nil {
		return models.Laboratory{}, err
	}

	for i, j := 0, len(messagesHistory)-1; i < j; i, j = i+1, j-1 {
		messagesHistory[i], messagesHistory[j] = messagesHistory[j], messagesHistory[i]
	}

	if len(messagesHistory) == 0 {
		return models.Laboratory{}, errors.New("history empty")
	}

	_, _ = vk.MessagesMarkAsRead(api.Params{
		"peer_id": -174105461,
	})
	if err != nil {
		return models.Laboratory{}, err
	}

	var labMessage = messagesHistory[len(messagesHistory)-1].Text
	var infectionName string

	if strings.Contains(labMessage, "болезнью") {
		infectionName = `Руководитель в состоянии горячки, вызванной болезнью «([^)]+)», ещё [0-9]+ ([^)]+) [0-9]+ ([^)]+)`
	} else {
		infectionName = `Руководитель в состоянии горячки ещё [0-9]+ ([^)]+) [0-9]+ ([^)]+)`
	}

	var (
		rexPathogens = regexp.MustCompile(`🧪 Готовых патогенов: [0-9]+ из [0-9]+`)
		pathogens    = rexPathogens.FindString(labMessage)

		rexNewPathogen = regexp.MustCompile(`Новый патоген: (([^)]+)\n\n)`)
		newPathogen    = rexNewPathogen.FindString(labMessage)

		rexExperience = regexp.MustCompile(`Био-опыт: ([^)]+)`)
		experience    = rexExperience.FindString(labMessage)

		rexResources = regexp.MustCompile(`Био-ресурс: ([^)]+)😷`)
		resources    = rexResources.FindString(labMessage)

		rexHealth = regexp.MustCompile(infectionName)
		health    = rexHealth.FindString(labMessage)
	)

	if len(pathogens) == 0 || len(experience) == 0 {
		return models.Laboratory{Pathogens: "NULL"}, nil
	}

	resources = strings.Replace(resources, "Био-ресурс:", "Ресурсы:", -1)
	if len(health) == 0 {
		health = "✅ Горячки нет, руководитель жив и здоров"
	}
	if len(newPathogen) == 0 {
		newPathogen = "🔥 Хранилище торпед переполнено"
	} else {
		newPathogen = "⏱ " + strings.Replace(newPathogen, "Новый патоген:", "Появление следующей торпеды:", -1)
	}

	return models.Laboratory{
		Pathogens:          strings.Replace(pathogens, "🧪 Готовых патогенов", "🤠 Торпед в наличии", -1),
		NewPathogen:        newPathogen,
		Expirence:          "☣ " + strings.Replace(experience, "Био-опыт:", "Опыт:", -1),
		ResourcesAvailable: "💫 " + strings.Replace(resources, "😷", "", -1),
		Health:             health,
	}, nil
}

func GetLab(vk *api.VK, logger *logging.Logger) string {
	msg, err := vk.MessagesSend(api.Params{
		"user_id":   "-174105461",
		"random_id": 0,
		"message":   "!лаб",
	})

	if err != nil {
		//EditMsg(token, fmt.Sprintf("⚠ Произошла ошибка, а текст ее звучит так:\n %s", err.Error()), mid, pid)
		return fmt.Sprintf("⚠ Произошла ошибка, а текст ее звучит так:\n %s", err.Error())
	}

	var res models.Laboratory

	for i := 0; i < 21; i++ {
		time.Sleep(time.Second * 1)
		if len(res.Pathogens) == 0 || strings.Contains(res.Pathogens, "NULL") {
			res, err = ParseLab(vk, -174105461)
			if err != nil {
				continue
			}
		} else {
			break
		}
	}

	if strings.Contains(res.Pathogens, "NULL") {
		err = util.DeleteMessages(vk, msg, 2, logger)
		if err != nil {
			logger.Error(err)
		}

		return "⚠ Сообщение от ириса не найдено"
	}

	var info = "" +
		res.Pathogens + "\n" +
		strings.ReplaceAll(res.NewPathogen, "\n", "") + "\n" +
		strings.Split(res.Expirence, "\n")[0] + "\n" +
		res.ResourcesAvailable

	if len(res.Health) > 0 {
		info += "\n\n" + res.Health
	}

	err = util.DeleteMessages(vk, msg, 2, logger)
	if err != nil {
		logger.Error(err)
	}

	return info
}
