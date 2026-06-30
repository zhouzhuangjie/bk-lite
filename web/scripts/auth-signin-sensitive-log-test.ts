import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const signinClientSource = readFileSync(
  join(__dirname, '../src/app/(core)/auth/signin/SigninClient.tsx'),
  'utf8',
);

assert.equal(
  /console\.(?:log|debug|info|warn|error)\([^)]*userDataForAuth/s.test(signinClientSource),
  false,
  'SigninClient must not log the authentication user object because it contains token',
);

assert.equal(
  /console\.(?:log|debug|info|warn|error)\([^)]*targetUrl/s.test(signinClientSource),
  false,
  'SigninClient must not log redirect targetUrl because third-login callbacks can contain token',
);

console.log('auth signin sensitive log validation passed');
