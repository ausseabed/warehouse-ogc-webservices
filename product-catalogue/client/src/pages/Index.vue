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
        <q-markup-table>
          <thead>
            <tr>
              <th colspan="2">
                <div class="text-h6 q-ml-md">Dataset Detail</div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <q-item-label>UUID</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].UUID}}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Gazeteer</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].gazeteerName }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Year</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].year }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Resolution</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].resolution }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>SRS</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].srs }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Metadata Persistent Id</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].metadataPersistentId }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Product Tif Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].l3ProductTifLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L0 Coverage Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].l0CoverageLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Coverage Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].l3CoverageLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Hillshade Tif Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ selected[0].hillshadeLocation }}</q-item-label>
              </td>
            </tr>
          </tbody>
        </q-markup-table>
        <!--<q-input
          v-model="text"
          label="Standard"
        />-->
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
