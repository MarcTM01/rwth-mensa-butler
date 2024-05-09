package scrapper

import (
	"fmt"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/PuerkitoBio/goquery"
	"regexp"
)

func ScrapMensaDayOfferings(rootNode *goquery.Selection) (*model.MensaDayMenus, error) {
	date, err := getDateFromRootNode(rootNode)
	if err != nil {
		return nil, err
	}

	menus, err := getMenusFromRootNode(rootNode)
	if err != nil {
		return nil, err
	}

	extras, err := getExtrasFromRootNode(rootNode)
	if err != nil {
		return nil, err
	}

	mensaLayout := model.MensaDayMenus{
		Date:   date,
		Menus:  menus,
		Extras: extras,
	}

	return &mensaLayout, nil
}

func getExtrasFromRootNode(rootNode *goquery.Selection) ([]model.MensaMenuExtra, error) {
	extraMenuContainerNode := rootNode.Find("div > table.extras > tbody")
	if extraMenuContainerNode.Length() != 1 {
		return nil, fmt.Errorf("expected 1 extra menu container node, got %d", extraMenuContainerNode.Length())
	}
	childrenContainers := extraMenuContainerNode.Children()
	childrenNodes := make([]model.MensaMenuExtra, childrenContainers.Length())

	for i := range childrenNodes {
		child, err := ScrapMensaExtras(childrenContainers.Eq(i))
		if err != nil {
			return nil, err
		}
		childrenNodes[i] = *child
	}
	return childrenNodes, nil
}
func getMenusFromRootNode(rootNode *goquery.Selection) ([]model.MensaMenu, error) {
	menuContainerNode := rootNode.Find("div > table.menues > tbody")
	if menuContainerNode.Length() != 1 {
		return nil, fmt.Errorf("expected 1 menu container node, got %d", menuContainerNode.Length())
	}
	childrenContainers := menuContainerNode.Children()
	childrenNodes := make([]model.MensaMenu, childrenContainers.Length())

	for i := range childrenNodes {
		child, err := ScrapMensaMenu(childrenContainers.Eq(i))
		if err != nil {
			return nil, err
		}
		childrenNodes[i] = *child
	}

	return childrenNodes, nil
}

const dateRegex = `\d\d\.\d\d\.\d\d\d\d`
const dateLength = 10

func getDateFromRootNode(rootNode *goquery.Selection) (string, error) {
	candidateNode := rootNode.Find("h3 a")
	if candidateNode.Length() != 1 {
		return "", fmt.Errorf("expected 1 heading node, got %d", candidateNode.Length())
	}

	headingText := candidateNode.Text()
	if len(headingText) < dateLength {
		return "", fmt.Errorf("expected heading text to be at least %d characters long, got %d", dateLength, len(headingText))
	}

	expectedDateSubstring := headingText[len(headingText)-dateLength:]
	regex := regexp.MustCompile(dateRegex)

	if !regex.MatchString(expectedDateSubstring) {
		return "", fmt.Errorf("expected date to be of format DD.MM.YYYY god %s", expectedDateSubstring)
	}

	//        0123456789
	// Input  DD.MM.YYYY
	// Output YYYY-MM-DD
	return fmt.Sprintf("%s-%s-%s", expectedDateSubstring[6:10], expectedDateSubstring[3:5], expectedDateSubstring[0:2]), nil
}
