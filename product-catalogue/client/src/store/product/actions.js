export async function fetchData ({ commit }, selected) {
  if (selected === undefined) {
    return
  }
  var recordId = selected.rows[0].id

  const axios = require('axios').default
  try {
    const response = await axios.get('/api/product/' + recordId)
    commit('updateSavedData', response.data)
  } catch (error) {
    console.error(error)
  }
}
