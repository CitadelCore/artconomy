<template>
  <v-container>
    <ac-profile-header :username="username"></ac-profile-header>
    <ac-paginated :list="list">
      <template v-slot:default>
        <v-container fluid class="pa-0">
          <v-row>
            <v-col cols="12" class="text-right">
              <v-btn color="green" :to="{name: 'Products', params: {username}}"><v-icon left>add</v-icon>Place an order!</v-btn>
            </v-col>
          </v-row>
          <v-row no-gutters>
            <v-col cols="12" sm="6" md="4" lg="2" v-for="order in list.list" :key="order.x.id">
              <ac-order-preview :order="order" type="sale" :username="username" />
            </v-col>
          </v-row>
        </v-container>
      </template>
      <template v-slot:empty>
        <v-row>
          <v-col cols="12" class="text-center">
            This artist has no commissions in progress.
          </v-col>
          <v-col cols="12" class="text-center">
            <v-btn color="green" :to="{name: 'Products', params: {username}}"><v-icon left>add</v-icon>Place an order!</v-btn>
          </v-col>
        </v-row>
      </template>
    </ac-paginated>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcProfileHeader from '@/components/views/profile/AcProfileHeader.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcOrderPreview from '@/components/AcOrderPreview.vue'
import {ListController} from '@/store/lists/controller'
import Order from '@/types/Order'
@Component({
  components: {AcOrderPreview, AcPaginated, AcProfileHeader, AcLoadSection},
})
export default class Queue extends mixins(Subjective) {
  public list: ListController<Order> = null as unknown as ListController<Order>

  public created() {
    this.list = this.$getList(`${this.username}__queue`, {
      endpoint: `/api/sales/v1/account/${this.username}/queue/`,
    })
    this.list.get().catch(this.setError)
  }
}
</script>
