var express = require('express');
var router = express.Router();
//import { getConnection } from 'typeorm';
import { ProductEntry } from '../lib/entity/product-entry';
import { createConnection } from "typeorm";

import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';

/* GET products listing. */
router.get('/',
  function (req, res, next) {

    createConnection().then(async connection => {
      let connOpts = connection.options as PostgresConnectionOptions;
      console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
        `(${connOpts.type})`);

      let productEntries = await connection.manager.find(ProductEntry);
      await connection.close();

      return res.json(productEntries);
    }).catch(error => {
      console.log(error)
    });
  }
);

module.exports = router;
