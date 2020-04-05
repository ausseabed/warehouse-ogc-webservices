<template>
  <q-page class="flex flex-center">

    <div class="q-pa-md">
      <q-table
        title="Datasets"
        :data="data"
        :columns="columns"
        row-key="name"
      />
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
          name: 'id',
          required: true,
          label: 'UUID',
          align: 'left',
          field: row => row.id,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'gazeteerName', align: 'center', label: 'Gazeteer', field: 'gazeteerName', sortable: true },
        // { name: 'year', label: 'Year', field: 'year', sortable: true },
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
