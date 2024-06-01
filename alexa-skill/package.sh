#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <alexa-code-commit-repository-folder>"
    exit 1
fi

TARGET_DIRECTORY="$1"
echo "Packaging Alexa Skill to '${TARGET_DIRECTORY}'"

if [ ! -d "$TARGET_DIRECTORY" ]; then
    echo "ERROR: The path $TARGET_DIRECTORY is not a directory or does not exist."
    exit 1
fi

if [ ! -d "$TARGET_DIRECTORY/lambda" ] || [ ! -d "$TARGET_DIRECTORY/skill-package" ]; then
    echo "ERROR: The path $TARGET_DIRECTORY does not look like a valid Alexa Skill repository."
    exit 1
fi

echo "Copying lambda source code"
rsync -a -v --delete-after --exclude '*/__pycache__' lambda-pdm/src/ "$TARGET_DIRECTORY/lambda/"

echo "Updating requirements.txt"
(cd lambda-pdm && pdm export --prod --format requirements --no-hashes) > "$TARGET_DIRECTORY/lambda/requirements.txt"

echo "Compiling language files"
(cd "$TARGET_DIRECTORY/lambda" && pybabel compile -i locales/en-US/LC_MESSAGES/skill.po -o locales/en-US/LC_MESSAGES/skill.mo &&
                                  pybabel compile -i locales/de-DE/LC_MESSAGES/skill.po -o locales/de-DE/LC_MESSAGES/skill.mo)

echo "Updating skill-package"
rsync -a -v --delete-after skill-package/interactionModels/ "$TARGET_DIRECTORY/skill-package/interactionModels/"

echo "Building skill.json and .env"
envsubst < skill-package/skill.json > "$TARGET_DIRECTORY/skill-package/skill.json"
envsubst < lambda-pdm/src/.env.template > "$TARGET_DIRECTORY/lambda/.env"

if [ "$#" -eq 2 ] && [ "$2" == "commit" ]; then
  echo "Commiting changes"
  (cd "$TARGET_DIRECTORY" && git add lambda skill-package && git commit -m "Update lambda source code and requirements.txt" && git push)
fi
