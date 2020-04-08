export async function fetchData ({ commit }) {
  const axios = require('axios').default
  try {
    console.log('get products')
    const response = await axios.get('/api/products')
    commit('updateSavedData', response.data)
  } catch (error) {
    console.error(error)
  }
}
