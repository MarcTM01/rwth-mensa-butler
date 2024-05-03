package scrapper

import (
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/spf13/viper"
)

func GetApplicationConfiguration() (*model.ApplicationConfiguration, error) {
	viper.SetConfigName("config")
	viper.AddConfigPath(".")
	viper.SetConfigType("yml")

	var config model.ApplicationConfiguration
	err := viper.ReadInConfig()
	if err != nil {
		return nil, err
	}

	err = viper.Unmarshal(&config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}
