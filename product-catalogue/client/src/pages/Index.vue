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

export default {
  data () {
    return store.state.products
  }
}
</script>
