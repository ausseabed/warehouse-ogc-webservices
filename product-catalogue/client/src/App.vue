<template>
  <q-layout
    view="hHh Lpr lFf"
    id="q-app"
  >
    <!--
    <q-header>
      <toolbar></toolbar>
    </q-header>
    -->
    <q-page-container>
      <router-view></router-view>
    </q-page-container>
  </q-layout>
</template>

<script>

export default {
  name: 'App'
}
</script>
