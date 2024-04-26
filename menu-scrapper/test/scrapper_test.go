package test

import (
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper/scrapper"
	"github.com/PuerkitoBio/goquery"
	"os"
	"strings"
	"testing"
)

func TestScrapMensaMenuOfferings(t *testing.T) {
	dat, err := os.ReadFile("data/2024-04-26-academica-en.html")
	if err != nil {
		t.Error(err)
	}
	documentText := string(dat)

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(documentText))
	if err != nil {
		t.Error(err)
	}

	results, err := scrapper.ScrapMensaMenuOfferings(doc)
	if err != nil {
		t.Error(err)
	}

	if results.MensaName != "Mensa Academica" {
		t.Error("Expected mensa name to be 'Mensa Academica', got", results.MensaName)
	}

	if len(results.DailyMenus) != 9 {
		t.Error("Expected 9 daily menus, got", len(results.DailyMenus))
	}

	sampleDay, ok := results.DailyMenus["2024-04-22"]
	if !ok {
		t.Error("Expected to find menu for 2024-04-22")
	}

	if sampleDay.Date != "2024-04-22" {
		t.Error("Expected date to be 2024-04-22, got", sampleDay.Date)
	}

	if len(sampleDay.Menus) != 8 {
		t.Error("Expected 8 menus, got", len(sampleDay.Menus))
	}

	sampleMenu := sampleDay.Menus[0]

	if sampleMenu.Name != "Stew" {
		t.Error("Expected menu name to be 'Stew', got", sampleMenu.Name)
	}

	if len(sampleMenu.Contents) != 2 || sampleMenu.Contents[0] != "Goucho hotpot with beef" || sampleMenu.Contents[1] != "Bread roll" {
		t.Error("Expected menu contents to be ['Goucho hotpot with beef', 'Bread roll", sampleMenu.Contents)
	}

	if sampleMenu.Price == nil || *sampleMenu.Price != "2,00 €" {
		t.Error("Expected price to be '2,00 €', got", *sampleMenu.Price)
	}

	if _, hasBeef := sampleMenu.NutritionFlags["beef"]; len(sampleMenu.NutritionFlags) != 1 || !hasBeef {
		t.Error("Expected nutrition flags to be ['beef'], got", sampleMenu.NutritionFlags)
	}
}
