export async function fetchData ({ commit }) {
  const axios = require('axios').default
  try {
    const response = await axios.get('/api/products')
    console.log(response)
    commit('updateSavedData', response.data)
  } catch (error) {
    console.error(error)
  }
}
