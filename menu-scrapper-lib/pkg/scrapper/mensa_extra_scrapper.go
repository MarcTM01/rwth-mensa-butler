package scrapper

import (
	"errors"
	"fmt"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/utils"
	"github.com/PuerkitoBio/goquery"
)

func ScrapMensaExtras(rootNode *goquery.Selection) (*model.MensaMenuExtra, error) {
	categoryContainer := rootNode.Find("span.menue-category")
	if categoryContainer.Length() != 1 {
		return nil, errors.New(fmt.Sprintf("Expected 1 category container node, got %d", categoryContainer.Length()))
	}
	name := categoryContainer.Text()

	descriptionContainer := rootNode.Find("span.menue-desc").Clone()
	if descriptionContainer.Length() != 1 {
		return nil, errors.New(fmt.Sprintf("Expected 1 description container node, got %d", descriptionContainer.Length()))
	}

	descriptionContainerModified := descriptionContainer.
		ChildrenFiltered("sup").Remove().End().
		ChildrenFiltered("span.menue-nutr").Remove().End()

	separator := descriptionContainerModified.Find("span.seperator")
	if separator.Length() == 1 {
		separator.SetText(
			fmt.Sprintf(" %s ", separator.Text()),
		)
	}

	return &model.MensaMenuExtra{
		Name:        utils.RemoveRedundantWhitespace(name),
		Description: utils.RemoveRedundantWhitespace(descriptionContainerModified.Text()),
	}, nil
}
