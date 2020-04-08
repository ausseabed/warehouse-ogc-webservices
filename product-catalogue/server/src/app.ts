var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');

var indexRouter = require('./routes/index');
var productsRouter = require('./routes/products');
var productRouter = require('./routes/product');

// import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';
// import { getConnectionManager, ConnectionManager, Connection } from "typeorm";

// async function createConnectionAsync () {
//   const connectionManager = new ConnectionManager();
//   const connection = connectionManager.create();
//   let connOpts = connection.options as PostgresConnectionOptions;
//   console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
//     `(${connOpts.type})`);
//   await connection.connect();
// }
// createConnectionAsync();
import { PostgresConnectionOptions } from 'typeorm/driver/postgres/PostgresConnectionOptions';
import { createConnection } from "typeorm"
async function createDefaultConnection () {
  createConnection().then(async connection => {
    let connOpts = connection.options as PostgresConnectionOptions;
    console.log(`Connected to database ${connOpts.host}:${connOpts.port} ` +
      `(${connOpts.type})`);

  }).catch(error => { console.log(error); });
}

createDefaultConnection()

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/products', productsRouter);
app.use('/product', productRouter);

// catch 404 and forward to error handler
app.use(function (req, res, next) {
  next(createError(404));
});

// error handler
app.use(function (err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
