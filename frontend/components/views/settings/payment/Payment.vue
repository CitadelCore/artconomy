<template>
  <v-row no-gutters  >
    <v-col cols="12">
      <router-view></router-view>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {FormController} from '@/store/forms/form-controller'

@Component
export default class Payment extends mixins(Subjective) {
    public ccForm: FormController = null as unknown as FormController
    public created() {
      if (this.$route.name === 'Payment') {
        this.$router.replace({name: 'Purchase', params: {username: this.username}})
      }
    }
}
</script>

<style scoped>

</style>
