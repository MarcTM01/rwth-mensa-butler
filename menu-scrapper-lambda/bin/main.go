package main

import (
	"context"
	"fmt"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/model"
	"github.com/MarcTM01/rwth-mensa-butler/menu-scrapper-lib/pkg/scrapper"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/credentials"
	"github.com/aws/aws-sdk-go-v2/feature/dynamodb/attributevalue"
	"github.com/aws/aws-sdk-go-v2/service/dynamodb"
	"log"
	"os"
)

var (
	dynaClient          *dynamodb.Client
	tableName           = os.Getenv("TABLE_NAME")
	environmentName     = os.Getenv("ENVIRONMENT_NAME")
	scrapConfigurations *model.ApplicationConfiguration
)

type Response struct {
	Success  bool     `json:"success"`
	Messages []string `json:"message"`
}

func (r *Response) Merge(other *Response) *Response {
	r.Success = r.Success && other.Success
	r.Messages = append(r.Messages, other.Messages...)
	return r
}

type MensaOfferingsTable struct {
	MensaIdLanguageKeyDate string
	MensaId                string
	LanguageKey            string
	model.MensaDayMenus
}

func storeDayOfferings(mensaId string, languageKey string, offerings model.MensaDayMenus) error {
	tableEntry := MensaOfferingsTable{
		MensaIdLanguageKeyDate: mensaId + ";" + languageKey + ";" + offerings.Date,
		MensaId:                mensaId,
		LanguageKey:            languageKey,
		MensaDayMenus:          offerings,
	}

	item, err := attributevalue.MarshalMap(tableEntry)
	if err != nil {
		return err
	}
	_, err = dynaClient.PutItem(context.TODO(), &dynamodb.PutItemInput{
		TableName: aws.String(tableName), Item: item,
	})
	return err
}

func retrieveAndStoreOfferingsForMensaUrl(mensaId string, languageKey string, url string) Response {
	response := Response{
		Success:  true,
		Messages: []string{},
	}

	offerings, err := scrapper.RetrieveCurrentMensaOfferings(url)
	if err != nil {
		response.Success = false
		response.Messages = append(response.Messages, fmt.Sprintf("[%s-%s] Could not scrap offerings from website", mensaId, languageKey))
		log.Printf("[%s-%s] [ERROR] Could not scrap offerings from website: %v", mensaId, languageKey, err)
		return response
	}

	successCounter := 0
	for _, dailyOfferings := range offerings.DailyMenus {
		err = storeDayOfferings(mensaId, languageKey, dailyOfferings)
		if err != nil {
			response.Success = false
			response.Messages = append(response.Messages, fmt.Sprintf("[%s-%s] Could not store scrapped offerings to database for date %s", mensaId, languageKey, dailyOfferings.Date))
			log.Printf("[%s-%s] [ERROR] Could not store scrapped offerings to database for date %s: %v", mensaId, languageKey, dailyOfferings.Date, err)
		} else {
			successCounter++
		}
	}

	response.Messages = append(response.Messages, fmt.Sprintf("[%s-%s] Successfully stored %d days of offerings", mensaId, languageKey, successCounter))
	log.Printf("[%s-%s] [INFO] Successfully stored %d days of offerings", mensaId, languageKey, successCounter)
	return response
}

func retrieveAndStoreOfferingsForMensa(mensa model.MensaConfiguration) Response {
	response := Response{
		Success:  true,
		Messages: []string{},
	}

	responseDe := retrieveAndStoreOfferingsForMensaUrl(mensa.MensaId, "de", mensa.Urls.GermanUrl)
	response.Merge(&responseDe)

	responseEn := retrieveAndStoreOfferingsForMensaUrl(mensa.MensaId, "en", mensa.Urls.EnglishUrl)
	response.Merge(&responseEn)

	return response
}

func handler() (*Response, error) {
	response := Response{
		Success:  true,
		Messages: []string{},
	}

	for _, mensa := range scrapConfigurations.MensaConfigurations {
		mensaResponse := retrieveAndStoreOfferingsForMensa(mensa)
		response.Merge(&mensaResponse)
	}

	return &response, nil
}

func getAwsConfiguration() (aws.Config, error) {
	if environmentName == "localdev" {
		return config.LoadDefaultConfig(context.TODO(),
			config.WithRegion("localhost"),
			config.WithEndpointResolverWithOptions(aws.EndpointResolverWithOptionsFunc(
				func(service, region string, options ...interface{}) (aws.Endpoint, error) {
					return aws.Endpoint{URL: "http://host.docker.internal:8000"}, nil
				})),
			config.WithCredentialsProvider(credentials.StaticCredentialsProvider{
				Value: aws.Credentials{
					AccessKeyID: "something", SecretAccessKey: "somethingsecret", SessionToken: "",
					Source: "This stuff is just random.",
				},
			}))
	} else if environmentName == "prod" {
		return config.LoadDefaultConfig(context.TODO())
	} else {
		return aws.Config{}, fmt.Errorf("unknown environment name: %s", environmentName)
	}
}

func main() {
	// Load AWS configuration
	cfg, err := getAwsConfiguration()
	if err != nil {
		log.Fatal(err)
	}

	// Create DynamoDB client
	dynaClient = dynamodb.NewFromConfig(cfg)

	// Load scrapping configuration
	scrapConfigurations, err = scrapper.GetApplicationConfiguration()
	if err != nil {
		log.Fatal(err)
	}

	lambda.Start(handler)
}
