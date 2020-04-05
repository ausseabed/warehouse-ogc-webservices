<template>
  <q-page class="flex flex-center">

    <div class="col">
      <div class="q-pa-md">
        <q-table
          title="Datasets"
          :data="data"
          :columns="columns"
          row-key="name"
        />
      </div>
      <div class="q-pa-md">
        <h5>Dataset Detail</h5>
        <q-markup-table>
          <tbody>
            <tr>
              <td>
                <q-item-label>UUID</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].UUID }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Gazeteer</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].gazeteerName }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Year</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].year }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Resolution</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].resolution }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>SRS</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].srs }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>Metadata Persistent Id</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].metadataPersistentId }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Product Tif Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].l3ProductTifLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L0 Coveratge Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].l0CoverageLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Coveratge Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].l3CoverageLocation }}</q-item-label>
              </td>
            </tr>
            <tr>
              <td>
                <q-item-label>L3 Hillshade Tif Location</q-item-label>
              </td>
              <td>
                <q-item-label>{{ data[0].hillshadeLocation }}</q-item-label>
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
const axios = require('axios').default;
async function getProducts () {
  try {
    const response = await axios.get('/api/products');
    console.log(response);
    return response['data'];
  } catch (error) {
    console.error(error);
    return [];
  }
}
import '../store/products'
import { mapState } from 'vuex'

export default {
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
        { name: 'gazeteerName', align: 'center', label: 'Gazeteer', field: 'gazeteerName', sortable: true },
        { name: 'year', label: 'Year', field: 'year', sortable: true },
        { name: 'resolution', label: 'Resolution', field: 'resolution' },
        { name: 'srs', label: 'SRS', field: 'srs' }
      ]
    }
  },
  async created () {
    this.$store.state.products.data = await getProducts();
  }
}
</script>
