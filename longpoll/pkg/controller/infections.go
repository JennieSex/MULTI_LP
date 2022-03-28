// Developer: th2empty
// Date: 27.03.2022

package controller

import (
	"errors"
	"fmt"
	"github.com/SevereCloud/vksdk/v2/api"
	"github.com/SevereCloud/vksdk/v2/object"
	"lp/pkg/logging"
	"lp/pkg/utils"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type Infection struct {
	TargetID      string
	UpToString    string
	BioExperience string
	InfectionTime int
}

func parseUserInfection(m string, uid string, targetID string, sentDate int64) (Infection, error) {
	var (
		rexOwnerInfected = regexp.MustCompile(`id[0-9]+`)
		rexDays          = regexp.MustCompile(`Заражение на [0-9]+`)
		rexExperience    = regexp.MustCompile(`\+([^)]+) био-опыта`)
		rexInt           = regexp.MustCompile(`[0-9]+`)
		days             int
		experience       string
		date             = time.Unix(sentDate, 0)
		upTo             string
		err              error
	)

	if len(rexOwnerInfected.FindAllString(m, -1)) == 0 ||
		rexOwnerInfected.FindAllString(m, -1)[0] != "id"+uid {
		return Infection{}, errors.New("invalid message")
	}

	days, err = strconv.Atoi(rexInt.FindString(rexDays.FindString(m)))
	if err != nil {
		return Infection{}, err
	}

	experience = rexExperience.FindString(m)
	if len(experience) == 0 {
		return Infection{}, err
	}

	experience = strings.Replace(experience, " био-опыта", "", 1)
	upTo = strings.Split(date.AddDate(0, 0, days).Format("02.01.2006"), " ")[0]

	return Infection{
		TargetID:      targetID,
		UpToString:    upTo,
		BioExperience: experience,
		InfectionTime: int(sentDate),
	}, nil
}

func getTargetId(logger *logging.Logger, vk *api.VK, msg object.MessagesMessage) (int, error) {
	var (
		rexTarget    = regexp.MustCompile(`([^)]+)`)
		rexTargetID  = regexp.MustCompile(`id[0-9]+`)
		rexTargetNum = regexp.MustCompile(`[0-9]+`)
		target       string
		targetNum    = rexTargetNum.FindString(msg.Text)
	)

	if msg.ReplyMessage != nil {
		if len(targetNum) == 0 {
			if msg.ReplyMessage.FromID < 0 {
				ids := rexTargetID.FindAllString(msg.ReplyMessage.Text, -1)

				for _, id := range ids {
					if id != fmt.Sprintf("id%d", msg.FromID) {
						target = strings.Replace(id, "id", "", 1)
						break
					}
				}
			}
		} else {
			var idx, _ = strconv.Atoi(targetNum)
			var targets = rexTargetID.FindAllString(msg.ReplyMessage.Text, -1)
			if len(targets) == 0 {
				targets = rexTarget.FindAllString(msg.ReplyMessage.Text, -1)
			}

			if idx > len(targets) {
				return 0, errors.New("invalid link number")
			}

			var tmp = strings.Split(targets[idx-1], " ")
			var t, err = GetUserIdByShortname(vk, utils.RemoveTrashFromTarget(tmp[len(tmp)-1]))
			if err != nil {
				return 0, err
			}
			target = strconv.Itoa(t)
		}
	} else if len(rexTargetID.FindString(msg.Text)) != 0 {
		var t, err = GetUserIdByShortname(vk, rexTargetID.FindString(msg.Text))
		if err != nil {
			return 0, err
		}
		target = strconv.Itoa(t)
	} else if len(utils.RemoveTrashFromTarget(rexTarget.FindString(msg.Text))) != 0 {
		link := strings.Split(utils.RemoveTrashFromTarget(rexTarget.FindString(msg.Text)), " ")[1]
		logger.Debugf("shortname: %s", link)
		var t, err = GetUserIdByShortname(vk, link)
		if err != nil {
			logger.Error(err)
			return 0, err
		}

		target = strconv.Itoa(t)
		logger.Debugf("Output id: id%s", target)
	} else if len(msg.Text) == 0 {
		return 0, nil
	}

	id, err := strconv.Atoi(target)
	if err != nil {
		logger.Error("invalid id")
	}

	return id, nil
}

func FindInfections(logger *logging.Logger, vk *api.VK, mid, ownerId, targetID int) string { // if you don't know target id, send -1
	var (
		answer       string
		message, err = GetMessageByID(vk, mid)

		genderSubstr string
		messages     []object.MessagesMessage
		res          api.MessagesSearchResponse

		found = false

		infectionObject Infection
		objs            []Infection
	)

	if err != nil {
		logger.Error(err)
		return "⚠ Не удалось сообщение получить... Вот же блин"
	}

	if targetID == -1 {
		targetID, err = getTargetId(logger, vk, message)
		if err != nil {
			logger.Error(err)
			return "⚠ Не удалось найти кого инфицировать... Капец блин, я в недоумении!"
		}
	}

	if targetID == ownerId {
		return "👿 Шути свои шутки в другом месте"
	}

	ownerProfile, err := vk.UsersGet(api.Params{
		"user_ids":  ownerId,
		"fields":    "sex",
		"name_case": "Nom",
	})

	if err != nil {
		logger.Error(err)
		return "⚠ Ушиб...ошиб0чка и почему она произошла только бо[id324150088|]гу известно"
	}

	targetProfile, err := vk.UsersGet(api.Params{
		"user_ids":  fmt.Sprintf("id%d", targetID),
		"fields":    "sex",
		"name_case": "Nom",
	})

	if err != nil {
		logger.Error(err)
		return "⚠ Ушиб...ошиб0чка и почему она произошла только бо[id324150088|]гу известно"
	}

	if ownerProfile[0].Sex == 1 {
		genderSubstr = "подвергла"
	} else {
		genderSubstr = "подверг"
	}

	q := fmt.Sprintf("id%d %s заражению id%d", ownerId, genderSubstr, targetID)
	var offset = 0
	for i := 0; i < 6; i++ {
		res, _ = vk.MessagesSearch(api.Params{
			"q":        q,
			"count":    100,
			"offset":   offset,
			"extended": 0,
		})

		messages = append(messages, res.Items...)
		offset += 100
		time.Sleep(time.Millisecond * 30)
	}

	for _, v := range messages {
		if strings.Contains(v.Text, "Служба безопасности") {
			continue
		}
		infectionObject, _ = parseUserInfection(v.Text, strconv.Itoa(ownerId), strconv.Itoa(targetID), int64(v.Date))
		objs = append(objs, infectionObject)
	}

	if len(objs) == 0 {
		return fmt.Sprintf("⚠ Этот [id%d|олег] ещё мною инфицирован ни разу не был...", targetID)
	}

	for _, v := range objs {
		if len(v.UpToString) != 0 {
			found = true
			break
		}
	}

	if !found {
		return fmt.Sprintf("⚠ Этот [id%d|олег] ещё мною инфицирован ни разу не был...", targetID)
	}

	answer = fmt.Sprintf("📃 Заражения объекта [id%d|%s]:\n\n", targetID, targetProfile[0].FirstName)
	var i int
	var j int
	for _, v := range objs {
		if !strings.Contains(v.TargetID, strconv.Itoa(targetID)) || len(v.UpToString) == 0 {
			continue
		}

		if !(i > 4) {
			j++
			var t = time.Now().Unix() - int64(v.InfectionTime)
			answer += "☣️ " + v.BioExperience + " до " + v.UpToString
			if t < 21600 {
				var cooldown = time.Date(0, 0, 0, 0, 0, 21600-int(t), 0, time.UTC)
				answer += " | кд " + cooldown.Format("15:04:05") + "\n"
			} else {
				answer += "\n"
			}
		}

		i++
	}

	answer += "\nВсего заражений: " + strconv.Itoa(i)

	return answer
}
