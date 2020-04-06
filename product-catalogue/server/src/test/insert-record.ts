import { ProductEntry } from '../lib/entity/product-entry';

import { addExampleObject, addExampleObject2 } from "../lib/addExampleObject";
import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';
import { createConnection } from "typeorm";
import { doesNotMatch } from 'assert';

//import {ConnectionOptions} from "connection";

var assert = require('assert');

describe('Array', function () {
  describe('#indexOf()', function () {
    it('should return -1 when the value is not present', function () {
      assert.equal([1, 2, 3].indexOf(4), -1);
    });
  });
});

describe('TypeORM', function () {
  describe('Connection()', function () {
    it('Should run without an error', function (done) {
      createConnection().then(async connection => {
        let connOpts = connection.options as PostgresConnectionOptions;
        console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
          `(${connOpts.type})`);
        await connection.close();
        done();

      }).catch(error => { console.log(error); done(); });
    }
    );
  }
  );

  describe('CreateObjects()', function () {
    it('Should run without an error', function (done) {
      createConnection().then(async connection => {
        let connOpts = connection.options as PostgresConnectionOptions;
        console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
          `(${connOpts.type})`);

        var productEntry = addExampleObject();

        await connection.manager.save(productEntry);
        productEntry = addExampleObject2();

        await connection.manager.save(productEntry);
        await connection.close();
        done();

      }).catch(error => { console.log(error); done(); });
    }
    );
  }
  );
});
