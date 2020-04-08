const devConfig = {
  "type": 'postgres',
  "host": process.env.POSTGRES_HOSTNAME,
  "port": process.env.POSTGRES_PORT,
  "username": process.env.POSTGRES_USER,
  "password": process.env.POSTGRES_PASSWORD,
  "database": process.env.POSTGRES_DATABASE,

  "synchronize": true,
  "logging": false,
  "entities": [
    "src/lib/entity/**/*.ts"
  ],
  "migrations": [
    "src/lib/migration/**/*.ts"
  ],
  "subscribers": [
    "src/lib/subscriber/**/*.ts"
  ]
}

module.exports = devConfig