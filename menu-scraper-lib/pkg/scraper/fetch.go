package scraper

import (
	"github.com/PuerkitoBio/goquery"
	"io"
	"net/http"
	"strings"
)

func FetchHtml(url string) (string, error) {
	res, err := http.Get(url)
	if err != nil {
		return "", err
	}

	content, err := io.ReadAll(res.Body)
	if err != nil {
		return "", err
	}

	err = res.Body.Close()
	if err != nil {
		return "", err
	}

	return string(content), nil
}

func FetchHtmlToGoQuery(url string) (*goquery.Document, error) {
	htmlString, err := FetchHtml(url)
	if err != nil {
		return nil, err
	}

	doc, err := goquery.NewDocumentFromReader(strings.NewReader(htmlString))
	if err != nil {
		return nil, err
	}
	return doc, nil
}
