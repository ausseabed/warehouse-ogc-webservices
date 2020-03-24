import "reflect-metadata";
import {createConnection} from "typeorm";
import { addExampleObject } from "./addExampleObject";
var logger = require('morgan');
import { ProductEntry } from './entity/product-entry';

import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';

function saveRecord(productEntry : ProductEntry)
{

  //await repository.save(productEntry);
}


createConnection().then(connection => {
    let connOpts = connection.options as PostgresConnectionOptions;
    console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
      `(${connOpts.type})`);
  
    var productEntry = addExampleObject();
    saveRecord(productEntry)

  }).catch(error => console.log(error));;