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
export default {
  data () {
    return {
      columns: [
        {
          name: 'name',
          required: true,
          label: 'UUID',
          align: 'left',
          field: row => row.name,
          format: val => `${val}`,
          sortable: true
        },
        { name: 'gazeteer', align: 'center', label: 'Gazeteer', field: 'gazeteer', sortable: true },
        { name: 'year', label: 'Year', field: 'year', sortable: true },
        { name: 'resolution', label: 'Resolution', field: 'resolution' },
        { name: 'srs', label: 'SRS', field: 'srs' }
      ],
      data: [
        {
          name: 'Frozen Yogurt',
          gazeteer: 159,
          year: 6.0,
          resolution: 24,
          srs: 4.0
        },
        {
          name: 'Ice cream sandwich',
          gazeteer: 237,
          year: 9.0,
          resolution: 37,
          srs: 4.3
        },
        {
          name: 'Eclair',
          gazeteer: 262,
          year: 16.0,
          resolution: 23,
          srs: 6.0
        },
        {
          name: 'Cupcake',
          gazeteer: 305,
          year: 3.7,
          resolution: 67,
          srs: 4.3
        },
        {
          name: 'Gingerbread',
          gazeteer: 356,
          year: 16.0,
          resolution: 49,
          srs: 3.9
        },
        {
          name: 'Jelly bean',
          gazeteer: 375,
          year: 0.0,
          resolution: 94,
          srs: 0.0
        },
        {
          name: 'Lollipop',
          gazeteer: 392,
          year: 0.2,
          resolution: 98,
          srs: 0
        },
        {
          name: 'Honeycomb',
          gazeteer: 408,
          year: 3.2,
          resolution: 87,
          srs: 6.5
        },
        {
          name: 'Donut',
          gazeteer: 452,
          year: 25.0,
          resolution: 51,
          srs: 4.9
        },
        {
          name: 'KitKat',
          gazeteer: 518,
          year: 26.0,
          resolution: 65,
          srs: 7
        }
      ]
    }
  }
}
</script>
