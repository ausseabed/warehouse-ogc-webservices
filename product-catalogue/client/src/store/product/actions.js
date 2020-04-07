const axios = require('axios').default

export async function fetchData ({ commit }, recordId) {
  try {
    const response = await axios.get('/api/product/' + recordId)
    commit('updateSavedData', response.data)
  } catch (error) {
    console.error(error)
  }
}

export async function saveData ({ commit }, newProduct) {
  try {
    const response = await axios.put('/api/product/' + newProduct.id, newProduct)
    console.log(response)
  } catch (error) {
    console.error(error)
  }
}
