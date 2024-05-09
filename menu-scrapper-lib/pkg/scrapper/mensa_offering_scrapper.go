package scrapper

import (
	"fmt"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/utils"
	"github.com/PuerkitoBio/goquery"
)

func RetrieveCurrentMensaOfferings(menuUrl string) (*model.MensaOfferings, error) {
	doc, err := FetchHtmlToGoQuery(menuUrl)
	if err != nil {
		return nil, err
	}

	mensaRootNode, err := ScrapMensaMenuOfferings(doc)
	if err != nil {
		return nil, err
	}

	return mensaRootNode, nil
}

func ScrapMensaMenuOfferings(doc *goquery.Document) (*model.MensaOfferings, error) {
	rootNode := doc.Find("div.col-wrap")
	if rootNode.Length() != 1 {
		return nil, fmt.Errorf("expected 1 root node, got %d", rootNode.Length())
	}

	mensaName, err := getMensaNameFromRootNode(rootNode)
	if err != nil {
		return nil, err
	}

	dayNodes, err := getDayNodesFromRootNode(rootNode)
	if err != nil {
		return nil, err
	}

	mensaLayout := model.MensaOfferings{
		MensaName:  utils.RemoveRedundantWhitespace(mensaName),
		DailyMenus: dayNodes,
	}

	return &mensaLayout, nil
}

func getMensaNameFromRootNode(rootNode *goquery.Selection) (string, error) {
	candidateNode := rootNode.Find("h2 > b")
	if candidateNode.Length() != 1 {
		return "", fmt.Errorf("expected 1 mensa name node, got %d", candidateNode.Length())
	}
	return candidateNode.Text(), nil
}

func getDayNodesFromRootNode(rootNode *goquery.Selection) (map[string]model.MensaDayMenus, error) {
	dayNodes := rootNode.Find("div.accordion > div.preventBreak")
	childrenNodes := make(map[string]model.MensaDayMenus, dayNodes.Length())

	for i := range dayNodes.Nodes {
		child, err := ScrapMensaDayOfferings(dayNodes.Eq(i))
		if err != nil {
			return nil, err
		}
		childrenNodes[child.Date] = *child
	}

	return childrenNodes, nil
}
