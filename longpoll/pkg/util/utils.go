// Developer: th2empty
// Date: 17.03.2022

package util

import (
	"strings"
)

func HasString(str string, list []string) bool {
	for _, v := range list {
		if str == v {
			return true
		}
	}

	return false
}

func RemoveTrashFromTarget(target string) string {
	var symbols = []string{"https://www.vk.com/", "vk.com/", "https://"}
	for _, v := range symbols {
		target = strings.Replace(target, v, "", -1)
	}

	return target
}
