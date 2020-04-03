import Vue from 'vue'
import Vuex from 'vuex'

// import example from './module-example'
import products from './products'

Vue.use(Vuex)

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export default new Vuex.Store({
  modules: {
    products
  },

  // enable strict mode (adds overhead!)
  // for dev mode only
  strict: process.env.DEV
})
