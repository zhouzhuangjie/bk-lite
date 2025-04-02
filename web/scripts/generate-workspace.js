#!/usr/bin/env node
const { execSync } = require('child_process')

// Simple argument parsing function, no external dependencies
function parseArgs() {
  const args = {}
  process.argv.slice(2).forEach(arg => {
    if (arg.startsWith('--')) {
      const [key, value] = arg.substring(2).split('=')
      args[key] = value || true
    } else if (arg.startsWith('-')) {
      const key = arg.substring(1)
      args[key] = true
    }
  })
  return args
}

// Parse arguments with native approach
const cliArgs = parseArgs()

// npm automatically converts --app=value to npm_config_app=value environment variable
const npmConfigApp = process.env.npm_config_app

// Parameter priority: command line > npm config env > environment variable > default value
const apps = cliArgs.app || npmConfigApp || process.env.NEXTAPI_INSTALL_APP || '*'

// Add log for debugging
console.log(`Generating workspace configuration, app scope: ${apps}`)

// Call the original shell script (ensure correct path)
execSync(`bash scripts/generate-workspace.sh "${apps}"`, {
  stdio: 'inherit'
})
