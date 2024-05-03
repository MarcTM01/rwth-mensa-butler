FROM public.ecr.aws/docker/library/golang:1.21.9 as build-image
WORKDIR /src/menu-scrapper-lambda

ADD menu-scrapper-lib /src/menu-scrapper-lib
ADD menu-scrapper-lambda /src/menu-scrapper-lambda

RUN CGO_ENABLED=0 go build -o lambda-handler bin/main.go

FROM public.ecr.aws/lambda/provided:al2
COPY --from=build-image /src/menu-scrapper-lambda/lambda-handler .
ADD menu-scrapper-lib/config.yml .
ENTRYPOINT ./lambda-handler
