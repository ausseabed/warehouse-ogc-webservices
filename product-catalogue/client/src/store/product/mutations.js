export function updateSavedData (state, selectedProduct) {
  state.selectedProduct = selectedProduct
}
export function updateProduct (state, elementValuePair) {
  state.selectedProduct[elementValuePair.element] = elementValuePair.value
}
