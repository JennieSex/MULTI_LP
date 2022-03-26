// Developer: th2empty
// Date: 17.03.2022

package controller

import (
	"strings"
	"time"

	"github.com/SevereCloud/vksdk/v2/api"
	"github.com/SevereCloud/vksdk/v2/object"
)

func GetMessageByID(token string, id int) (object.MessagesMessage, error) {
	vk := api.NewVK(token)
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

func GetMessagesHistory(token string, pid int) ([]object.MessagesMessage, error) {
	vk := api.NewVK(token)

	var messages, err = vk.MessagesGetHistory(api.Params{
		"count":   100,
		"peer_id": pid,
	})

	if err != nil {
		return nil, err
	}

	return messages.Items, nil
}

func EditMsg(token string, text string, mid int, pid int) {
	vk := api.NewVK(token)

	_, err := vk.MessagesEdit(api.Params{
		"message":               text,
		"message_id":            mid,
		"peer_id":               pid,
		"keep_forward_messages": 0,
		"keep_snippets":         1,
		"disable_mentions":      1,
		"dont_parse_links":      1})

	if err != nil {
		if strings.Contains(err.Error(), "Too many requests per second") {
			time.Sleep(time.Second * 5)
			EditMsg(token, text, mid, pid)
		}
	}
}