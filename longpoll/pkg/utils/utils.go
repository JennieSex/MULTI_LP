// Developer: th2empty
// Date: 17.03.2022

package utils

func HasString(str string, list []string) bool {
	for _, v := range list {
		if str == v {
			return true
		}
	}

	return false
}