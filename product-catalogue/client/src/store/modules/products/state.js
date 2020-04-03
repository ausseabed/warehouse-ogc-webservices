export default function () {
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
    ],
    data: [
      {
        id: 'Frozen Yogurts',
        gazeteerName: 159,
        year: 6.0,
        resolution: 24,
        srs: 4.0
      }
    ]
  }
}
