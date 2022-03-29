// Developer: th2empty
// Date: 17.03.2022

package controller

import (
	"errors"
	"math/rand"
	"strings"
	"time"

	"github.com/SevereCloud/vksdk/v2/api"
	"github.com/SevereCloud/vksdk/v2/object"
)

func GetMessageByID(vk *api.VK, id int) (object.MessagesMessage, error) {
	res, err := vk.MessagesGetByID(api.Params{
		"message_ids": id,
		"extended":    1,
	})

	if err != nil {
		return object.MessagesMessage{Text: "NOT_FOUND"}, err
	}

	if len(res.Items) == 0 {
		return object.MessagesMessage{Text: "NOT_FOUND"}, err
	}

	return res.Items[len(res.Items)-1], nil
}

func GetMessagesHistory(vk *api.VK, pid int) ([]object.MessagesMessage, error) {
	var messages, err = vk.MessagesGetHistory(api.Params{
		"count":   100,
		"peer_id": pid,
	})

	if err != nil {
		return nil, err
	}

	return messages.Items, nil
}

func EditMsg(vk *api.VK, text string, mid int, pid int) {
	_, err := vk.MessagesEdit(api.Params{
		"message":               text,
		"message_id":            mid,
		"peer_id":               pid,
		"keep_forward_messages": 1,
		"keep_snippets":         1,
		"disable_mentions":      1,
		"dont_parse_links":      1})

	if err != nil {
		if strings.Contains(err.Error(), "Too many requests per second") {
			time.Sleep(time.Second * 5)
			EditMsg(vk, text, mid, pid)
		}
	}
}

func SendMessage(vk *api.VK, pid int, msgText string, reply int) error {
	rand.Seed(time.Now().UnixNano())
	_, err := vk.MessagesSend(api.Params{
		"random_id":        rand.Int31(),
		"peer_id":          pid,
		"message":          msgText,
		"disable_mentions": 1,
		"reply_to":         reply,
	})

	if err != nil {
		return err
	}

	return nil
}

func GetUserIdByShortname(vk *api.VK, shortname string) (int, error) {
	res, err := vk.UsersGet(api.Params{
		"user_ids":  shortname,
		"name_case": "Nom",
	})
	if err != nil {
		return -1, err
	}

	if len(res) == 0 {
		return -1, errors.New("response is empty")
	}

	return res[0].ID, nil
}
