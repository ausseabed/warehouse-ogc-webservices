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
      "lib/entity/**/*.ts"
   ],
   "migrations": [
      "lib/migration/**/*.ts"
   ],
   "subscribers": [
      "lib/subscriber/**/*.ts"
   ]
}

module.exports = devConfig