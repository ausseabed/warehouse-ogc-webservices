var express = require('express');
var router = express.Router();
import { ProductEntry } from '../lib/entity/product-entry';


import { getRepository } from "typeorm";
/* GET products listing. */
router.get('/:productId',
  async function (req, res, next) {
    let productEntries = await getRepository(ProductEntry).findOne(req.params.productId);
    return res.json(productEntries);
  }
);

import { plainToClass } from "class-transformer";

router.put('/:productId',
  async function (req, res, next) {
    let productEntry = plainToClass(ProductEntry, req.body);
    console.log(productEntry);
    await getRepository(ProductEntry).save(productEntry);
    // Save to database
    // let productEntries = await getRepository(ProductEntry).findOne(req.params.productId);
    return 'Nothing';
  }
);
module.exports = router;
