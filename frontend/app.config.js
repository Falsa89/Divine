const fs = require('fs');
const path = require('path');
const config = require('./app.json');

// Read .env file manually
function loadEnv() {
  const envPath = path.join(__dirname, '.env');
  const vars = {};
  try {
    const content = fs.readFileSync(envPath, 'utf-8');
    content.split('\n').forEach(line => {
      const [key, ...vals] = line.split('=');
      if (key && vals.length > 0) {
        vars[key.trim()] = vals.join('=').trim();
      }
    });
  } catch (e) {}
  return vars;
}

const env = loadEnv();

module.exports = () => {
  return {
    ...config.expo,
    extra: {
      ...config.expo.extra,
      EXPO_PACKAGER_PROXY_URL: process.env.EXPO_PACKAGER_PROXY_URL || env.EXPO_PACKAGER_PROXY_URL || '',
      EXPO_PACKAGER_HOSTNAME: process.env.EXPO_PACKAGER_HOSTNAME || env.EXPO_PACKAGER_HOSTNAME || '',
    },
  };
};
