var express = require('express');
var router = express.Router();
import { getManager } from "typeorm";
import { ProductEntry } from '../lib/entity/product-entry';

/* GET products listing. */
router.get('/',
  async function (req, res, next) {
    let productEntries = await getManager().find(ProductEntry);
    return res.json(productEntries);

  }
);

module.exports = router;
