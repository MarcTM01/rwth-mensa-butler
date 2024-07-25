FROM public.ecr.aws/docker/library/golang:1.21.9 as build-image
WORKDIR /src/menu-scraper-lambda

ADD menu-scraper-lib /src/menu-scraper-lib
ADD menu-scraper-lambda /src/menu-scraper-lambda

RUN CGO_ENABLED=0 go build -o lambda-handler bin/main.go

FROM public.ecr.aws/lambda/provided:al2
COPY --from=build-image /src/menu-scraper-lambda/lambda-handler .
ADD menu-scraper-lib/config.yml .
ENTRYPOINT ./lambda-handler
