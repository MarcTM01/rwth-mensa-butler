package model

type MensaOfferings struct {
	MensaName  string
	DailyMenus map[string]MensaDayMenus
}

type MensaDayMenus struct {
	Date   string // YYYY-MM-DD
	Menus  []MensaMenu
	Extras []MensaMenuExtra
}

type MensaMenu struct {
	Name           string
	Contents       []string
	Price          *string
	NutritionFlags map[string]struct{}
}

type MensaMenuExtra struct {
	Name        string
	Description string
}

const (
	FlagVegetarian string = "vegetarian"
	FlagVegan      string = "vegan"
	FlagPork       string = "pork"
	FlagBeef       string = "beef"
	FlagFish       string = "fish"
	FlagChicken    string = "chicken"
)
