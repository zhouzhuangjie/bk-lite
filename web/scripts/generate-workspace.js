#!/usr/bin/env node
const { execSync } = require('child_process')
const argv = require('minimist')(process.argv.slice(2))

// Parameter priority: command line > environment variable > default value
const apps = argv.app || process.env.NEXTAPI_INSTALL_APP || '*'

// Call the original shell script (ensure correct path)
execSync(`bash scripts/generate-workspace.sh "${apps}"`, {
  stdio: 'inherit'
})
