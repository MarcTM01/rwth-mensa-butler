package model

type ApplicationConfiguration struct {
	MensaConfigurations []MensaConfiguration `mapstructure:"mensas"`
}

type MensaConfiguration struct {
	MensaId   string           `mapstructure:"id"`
	MensaName string           `mapstructure:"name"`
	Urls      MensaRequestUrls `mapstructure:"urls"`
}

type MensaRequestUrls struct {
	GermanUrl  string `mapstructure:"de"`
	EnglishUrl string `mapstructure:"en"`
}
