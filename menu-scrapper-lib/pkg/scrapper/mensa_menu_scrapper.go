package scrapper

import (
	"errors"
	"fmt"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/utils"
	"github.com/PuerkitoBio/goquery"
	"strings"
)

func retrieveNutritionFlags(rootNode *goquery.Selection) (map[string]struct{}, error) {
	nutritionImageNodes := rootNode.Find("div.nutr-info > img.content-image")
	nutritionFlags := make(map[string]struct{})

	for i := range nutritionImageNodes.Nodes {
		imageNode := nutritionImageNodes.Eq(i)
		imageSrc, exists := imageNode.Attr("src")
		if !exists {
			return nil, errors.New("nutrition flag image node has no src attribute")
		}

		switch {
		case imageSrc == "resources/images/inhalt/OLV.png":
			nutritionFlags[model.FlagVegetarian] = struct{}{}
		case imageSrc == "resources/images/inhalt/vegan.png":
			nutritionFlags[model.FlagVegan] = struct{}{}
			nutritionFlags[model.FlagVegetarian] = struct{}{}
		case imageSrc == "resources/images/inhalt/Schwein.png":
			nutritionFlags[model.FlagPork] = struct{}{}
		case imageSrc == "resources/images/inhalt/Rind.png":
			nutritionFlags[model.FlagBeef] = struct{}{}
		case imageSrc == "resources/images/inhalt/Fisch.png":
			nutritionFlags[model.FlagFish] = struct{}{}
		case imageSrc == "resources/images/inhalt/Geflügel.png":
			nutritionFlags[model.FlagChicken] = struct{}{}
		default:
			return nil, errors.New(fmt.Sprintf("Unknown nutrition flag image src: %s", imageSrc))
		}
	}

	return nutritionFlags, nil
}

func retrievePrice(rootNode *goquery.Selection) (*string, error) {
	priceContainer := rootNode.Find("span.menue-price")
	switch {
	case priceContainer.Length() == 0:
		return nil, nil
	case priceContainer.Length() == 1:
		localPrice := utils.RemoveRedundantWhitespace(priceContainer.Text())
		return &localPrice, nil
	default:
		return nil, errors.New(fmt.Sprintf("Expected at most 1 price container node, got %d", priceContainer.Length()))
	}
}

func retrieveConents(rootNode *goquery.Selection) ([]string, error) {
	descriptionContainer := rootNode.Find("span.menue-desc > span.expand-nutr")
	if descriptionContainer.Length() != 1 {
		return nil, errors.New(fmt.Sprintf("Expected 1 description container node, got %d", descriptionContainer.Length()))
	}

	descriptionString := descriptionContainer.Clone().Children().Remove().End().Text()
	descriptionContents := strings.Split(descriptionString, "|")

	for i := range descriptionContents {
		descriptionContents[i] = utils.RemoveRedundantWhitespace(descriptionContents[i])
	}

	return descriptionContents, nil
}

func ScrapMensaMenu(rootNode *goquery.Selection) (*model.MensaMenu, error) {
	categoryContainer := rootNode.Find("span.menue-category")
	if categoryContainer.Length() != 1 {
		return nil, errors.New(fmt.Sprintf("Expected 1 category container node, got %d", categoryContainer.Length()))
	}
	name := categoryContainer.Text()

	price, err := retrievePrice(rootNode)
	if err != nil {
		return nil, err
	}

	descriptionContents, err := retrieveConents(rootNode)
	if err != nil {
		return nil, err
	}

	nutritionFlags, err := retrieveNutritionFlags(rootNode)
	if err != nil {
		return nil, err
	}

	return &model.MensaMenu{
		Name:           utils.RemoveRedundantWhitespace(name),
		Contents:       descriptionContents,
		Price:          price,
		NutritionFlags: nutritionFlags,
	}, nil
}
