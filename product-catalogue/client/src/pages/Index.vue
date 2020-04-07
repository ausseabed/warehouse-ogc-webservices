<template>
  <q-page class="flex">
    <div class="col">
      <div class="q-pa-md">
        <q-table
          title="Datasets"
          :data="data"
          :columns="columns"
          row-key="id"
          selection="single"
          :selected.sync="selected"
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
            v-model.lazy="selected[0].UUID"
            label="UUID"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].gazeteerName"
            label="Gazeteer"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].year"
            label="Year"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].resolution"
            label="Resolution"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].srs"
            label="SRS"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].metadataPersistentId"
            label="Metadata Persistent Id"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].l3ProductTifLocation"
            label="L3 Product Tif Location"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].l0CoverageLocation"
            label="L0 Coverage Location"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].l3CoverageLocation"
            label="L3 Coverage Location"
          />
          <q-input
            class="q-ml-md"
            v-model="selected[0].hillshadeLocation"
            label="L3 Hillshade Tif Location"
          />
          <q-btn
            class="q-ml-md"
            label="Submit"
            type="submit"
            color="primary"
          />
          <q-btn
            class="q-ml-md"
            label="Reset"
            type="reset"
            color="primary"
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
    ])
  },
  computed: mapState({
    data: state => state.products.data,
    countAlias: 'data'
  }),
  // {
  //   data: {
  //     get () {
  //       console.log(this.$store.state.products.data);
  //       return this.$store.state.products.data
  //     },
  //     set (val) {
  //       console.log('do nothing')
  //     }
  //   }
  // },
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
  async created () {
    this.$store.dispatch('products/fetchData')
  }
}
</script>
