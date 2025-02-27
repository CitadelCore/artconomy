<template>
  <v-row no-gutters  >
    <v-col cols="12" v-if="subject.artist_mode">
      <ac-bound-field
          :field="transactionFilter.fields.account"
          field-type="v-select"
          :items="[{text: 'Purchases', value: 300}, {text: 'Escrow', value: 302}, {text: 'Holdings', value: 303}]"
          label="Account"
      />
    </v-col>
    <v-col cols="12">
      <ac-paginated :list="transactions">
        <template v-slot:default>
          <v-row>
            <v-col cols="12">

            </v-col>
            <v-list three-line>
              <template v-for="transaction, index in transactions.list">
                <ac-transaction :transaction="transaction.x" :username="username" :key="transaction.x.id" :current-account="transactionFilter.fields.account.value" />
                <v-divider v-if="index + 1 < transactions.list.length" :key="index"/>
              </template>
            </v-list>
          </v-row>
        </template>
      </ac-paginated>
    </v-col>
    <v-col cols="12" v-if="!purchaseList">
      <ac-load-section :controller="summary">
        <template v-slot:default>
          <strong>Working Balance:</strong> ${{summary.x.available.toFixed(2)}}<br />
          <span v-if="!escrowList"><strong>Pending Changes:</strong> ${{summary.x.pending.toFixed(2)}}</span>
        </template>
      </ac-load-section>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {ListController} from '@/store/lists/controller'
import Transaction from '@/types/Transaction'
import {Watch} from 'vue-property-decorator'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcTransaction from '@/components/views/settings/payment/AcTransaction.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller'
import {Balance} from '@/types/Balance'
import {RawData} from '@/store/forms/types/RawData'
import {flatten} from '@/lib/lib'

  @Component({
    components: {AcLoadSection, AcTransaction, AcPaginated, AcBoundField},
  })
export default class TransactionHistory extends mixins(Subjective) {
    public summary: SingleController<Balance> = null as unknown as SingleController<Balance>
    public transactionFilter: FormController = null as unknown as FormController
    public transactions: ListController<Transaction> = null as unknown as ListController<Transaction>

    @Watch('transactionFilter.rawData')
    public newQuery(data: RawData) {
      this.transactions.params = data
      this.transactions.reset()
      this.summary.ready = false
      this.summary.fetching = false
      this.summary.setX(null)
      this.summary.params = data
      this.summary.get()
    }

    public get purchaseList() {
      return this.transactionFilter.fields.account.value === 300
    }

    public get escrowList() {
      return this.transactionFilter.fields.account.value === 302
    }

    public created() {
      this.transactionFilter = this.$getForm(`transactions_form__${flatten(this.username)}`, {
        endpoint: '', fields: {account: {value: 300}},
      })
      this.transactions = this.$getList(`transactions__${flatten(this.username)}`, {
        endpoint: `/api/sales/v1/account/${this.username}/transactions/`,
        params: this.transactionFilter.rawData,
      })
      this.transactions.firstRun()
      this.summary = this.$getSingle(flatten(`account_summary__${this.username}`), {
        endpoint: `/api/sales/v1/account/${this.username}/account-status/`, params: this.transactionFilter.rawData,
      })
      this.summary.get()
    }
}
</script>
