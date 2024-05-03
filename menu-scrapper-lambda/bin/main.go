package main

import (
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/scrapper"
	"github.com/aws/aws-lambda-go/lambda"
)

type Response struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func handler() (*Response, error) {
	configuration, err := scrapper.GetApplicationConfiguration()
	if err != nil {
		return nil, err
	}

	results, err := scrapper.RetrieveCurrentMensaOfferings(configuration.MensaConfigurations[0].Urls.GermanUrl)

	return &Response{
		Success: true,
		Message: results.MensaName,
	}, nil
}

func main() {
	lambda.Start(handler)
}
