package utils

import (
	"regexp"
)

var trimWhitespaceRegex = regexp.MustCompile(`^[\s\p{Zs}]+|[\s\p{Zs}]+$`)
var doubleWhitespaceRegex = regexp.MustCompile(`[\s\p{Zs}]{2,}`)

func RemoveRedundantWhitespace(input string) string {
	result := trimWhitespaceRegex.ReplaceAllString(input, "")
	result = doubleWhitespaceRegex.ReplaceAllString(result, " ")
	return result
}
