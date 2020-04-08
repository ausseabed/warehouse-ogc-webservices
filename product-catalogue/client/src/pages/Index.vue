<template>
  <q-page class="flex">
    <div class="col">
      <div
        class="q-pa-md"
        v-if="data.length==0"
      >
        <q-spinner
          color="primary"
          size="3em"
          :thickness="10"
        />
      </div>
      <div
        class="q-pa-md"
        v-if="data.length>0"
      >
        <q-table
          title="Datasets"
          :data="data"
          :columns="columns"
          row-key="id"
          selection="single"
          :selected.sync="selected"
          @selection="filterBySelection"
        />
      </div>
      <div
        class="q-mt-sm"
        v-if="selected.length==0"
      >
        <div class="text-h6 q-ml-md text-center">Select an item for specifics</div>
      </div>
      <div
        class="q-pa-md"
        v-if="selected.length>0"
      >
        <!--<q-markup-table class="q-gutter-y-md column">-->
        <q-form ref="myForm">
          <div class="text-h6 q-ml-md">Dataset Detail</div>
          <q-input
            class="q-ml-md"
            :value="selectedProduct.UUID"
            @input="value=>updateProduct('UUID',value)"
            label="UUID"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.gazeteerName"
            @input="value=>updateProduct('gazeteerName',value)"
            label="Gazeteer"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.year"
            @input="value=>updateProduct('year',value)"
            label="Year"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.resolution"
            @input="value=>updateProduct('resolution',value)"
            label="Resolution"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.srs"
            @input="value=>updateProduct('srs',value)"
            label="SRS"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.metadataPersistentId"
            @input="value=>updateProduct('metadataPersistentId',value)"
            label="Metadata Persistent Id"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.l3ProductTifLocation"
            @input="value=>updateProduct('l3ProductTifLocation',value)"
            label="L3 Product Tif Location"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.l0CoverageLocation"
            @input="value=>updateProduct('l0CoverageLocation',value)"
            label="L0 Coverage Location"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.l3CoverageLocation"
            @input="value=>updateProduct('l3CoverageLocation',value)"
            label="L3 Coverage Location"
          />
          <q-input
            class="q-ml-md"
            :value="selectedProduct.hillshadeLocation"
            @input="value=>updateProduct('hillshadeLocation',value)"
            label="L3 Hillshade Tif Location"
          />
          <q-btn
            class="q-ml-md"
            label="Submit"
            type="submit"
            color="primary"
            @click="_ => submitProduct(selectedProduct.id)"
          />
          <q-btn
            class="q-ml-md"
            label="Reset"
            type="reset"
            color="primary"
            @click="_ => resetProduct(selectedProduct.id)"
            flat
          />
        </q-form>
        <!--</q-markup-table>-->
      </div>
    </div>
  </q-page>
</template>

<script>
export default {
  name: 'PageIndex'
}
</script>
<script>

import '../store/products'
import { mapActions, mapState } from 'vuex'

export default {
  methods: {
    ...mapActions('products', [
      'fetchData'
    ], 'product', ['fetchData', 'updateProduct']),
    filterBySelection: function (details) {
      if (details === undefined || details.rows.length == 0) {
        return
      }
      var recordId = details.rows[0].id
      this.$store.dispatch('product/fetchData', recordId)
    },
    updateProduct (element, value) {
      this.$store.commit('product/updateProduct', { 'element': element, 'value': value })
    },
    resetProduct (id) {
      this.$store.dispatch('product/fetchData', id)
    },
    submitProduct (id) {
      this.$store.dispatch('product/saveData', this.selectedProduct)
    }
  },
  computed:
    mapState({
      data: state => state.products.data,
      selectedProduct: state => state.product.selectedProduct,
      countAlias: ['data', 'selectedProduct']
    }),
  data () {
    return {
      selected: [],
      columns: [
        {
          name: 'UUID',
          required: true,
          label: 'UUID',
          align: 'left',
          field: row => row.UUID,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'gazeteerName', label: 'Gazeteer', field: 'gazeteerName', align: 'left', sortable: true },
        { name: 'year', label: 'Year', field: 'year', align: 'left', sortable: true },
        { name: 'resolution', label: 'Resolution', align: 'left', field: 'resolution' },
        { name: 'srs', label: 'SRS', align: 'left', field: 'srs' }
      ]
    }
  },
  created () {
    this.$store.dispatch('products/fetchData')
  }
}
</script>
