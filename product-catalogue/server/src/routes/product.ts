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

router.post('/:productId',
  async function (req, res, next) {
    let productEntry = plainToClass(ProductEntry, req.body);
    await getRepository(ProductEntry).save(productEntry);
    res.send('OK');
  }
);
module.exports = router;
