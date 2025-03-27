#!/bin/bash
set -eo pipefail

APPS="$1"
APPS=$(echo "$APPS" | tr -d '"' | xargs)

{
  echo "# Auto-generated at $(date)"
  echo "packages:"

  if [ "$APPS" = "*" ]; then
    # If wildcard, add all applications
    echo "  - 'src/app/*'"
  else
    # Process specific app list
    IFS=', ' read -ra APP_ARRAY <<< "$APPS"
    for app in "${APP_ARRAY[@]}"; do
      echo "  - 'src/app/${app}'"
    done
  fi
} > pnpm-workspace.temp.yaml

# Atomic replacement
mv pnpm-workspace.temp.yaml pnpm-workspace.yaml

if [ "$APPS" = "*" ]; then
  echo "➤ Generated workspace for all applications (src/app/*)"
else
  IFS=', ' read -ra APP_ARRAY <<< "$APPS"
  echo "➤ Generated workspace for: ${APP_ARRAY[*]}"
fi
