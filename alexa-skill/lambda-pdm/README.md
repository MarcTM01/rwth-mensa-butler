# Alexa Skill Lambda PDM
This folder contains the source for the Alexa-Hosted Skill which forms the heart of this project.
The skill is written in Python and uses the `ask-sdk` library to interact with the Alexa Skills Kit.

I chose to develop this skill using the excellent [PDM](https://github.com/pdm-project/pdm) package manager,
which significantly simplifies managing dependencies and virtual environments.

To set up a local python interpreter with the required versions, simply run
`pdm install`.

## Development & Local testing
There is currently no way to perform integration or e2e-tests of this project without setting up
an AWS-hosted Alexa Skill and all the supporting infrastructure. This requires some setup.
Please open an issue, if you are interested in getting this setup.

## Code Quality & Testing
This project uses standard tooling to ensure consistency and promote high-quality code:
- We use [ruff](https://github.com/astral-sh/ruff) for formatting (`pdm run format`) and linting (`pdm run lint`)
- We use [mypy](https://github.com/python/mypy) for static type checking (`pdm run typecheck`)
- We use [pytest](https://github.com/pytest-dev/pytest) for unit-testing (`pdm run test`)
