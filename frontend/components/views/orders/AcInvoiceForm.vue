<template>
  <v-row class="ac-invoice-form">
    <v-col cols="12" sm="6" >
      <ac-bound-field
        :field="newInvoice.fields.product"
        field-type="ac-product-select"
        :multiple="false"
        :username="username"
        label="Product"
        hint="Optional: Specify which of your product this invoice is for. This can help with organization.
                  If no product is specified, this will be considered a custom order."
        :persistent-hint="true"
      ></ac-bound-field>
    </v-col>
    <slot name="second">
    </slot>
    <v-col cols="12" sm="6">
      <ac-price-preview  :lineItems="lineItems" :escrow="!escrowDisabled" :username="username" />
    </v-col>
    <v-col cols="12" sm="6" >
      <ac-bound-field
        :field="newInvoice.fields.price"
        field-type="ac-price-field"
        label="Total Price"
      ></ac-bound-field>
    </v-col>
    <v-col cols="12" sm="6" v-if="showBuyer">
      <ac-bound-field
        label="Customer username/email"
        :field="newInvoice.fields.buyer"
        field-type="ac-user-select"
        item-value="username"
        :multiple="false"
        :allow-raw="true"
        hint="Enter the username or the email address of the customer this commission is for.
                  This can be left blank if you only want to use this order for tracking purposes."
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field field-type="ac-checkbox"
                      label="Paid"
                      :field="newInvoice.fields.paid"
                      hint="If the commissioner has already paid, and you just want to track this order,
                                please check this box."
                      :persistent-hint="true"
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field field-type="ac-checkbox"
                      label="Already Complete"
                      :field="newInvoice.fields.completed"
                      hint="If you have already completed the commission you're invoicing, please check this box."
                      :persistent-hint="true"
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field field-type="ac-checkbox"
                      label="Hold for Edit"
                      :disabled="newInvoice.fields.paid.model"
                      :field="newInvoice.fields.hold"
                      hint="If you want to edit the line items on this invoice before sending it for payment, check this box."
                      :persistent-hint="true"
      />
    </v-col>
    <v-col cols="12">
      <ac-bound-field
        field-type="ac-rating-field"
        :field="newInvoice.fields.rating"
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field
        label="Slots taken"
        :field="newInvoice.fields.task_weight"
        :persistent-hint="true"
        :disabled="newInvoice.fields.completed.value"
        hint="How many of your slots this commission will take up."
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field
        label="Revisions included"
        :field="newInvoice.fields.revisions"
        :persistent-hint="true"
        :disabled="newInvoice.fields.completed.value"
        hint="The total number of times the buyer will be able to ask for revisions.
                  This does not include the final, so if there are no revisions, set this to zero."
      />
    </v-col>
    <v-col cols="12" sm="4" >
      <ac-bound-field
        label="Expected turnaround (days)"
        :field="newInvoice.fields.expected_turnaround"
        :persistent-hint="true"
        :disabled="newInvoice.fields.completed.value"
        hint="The total number of business days you expect this task will take."
      />
    </v-col>
    <v-col cols="12">
      <ac-bound-field
        label="description"
        :field="newInvoice.fields.details"
        field-type="ac-editor"
        :save-indicator="false"
        hint="Enter any information you need to remember in order to complete this commission.
                  NOTE: This information will be visible to the buyer."
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import Subjective from '@/mixins/subjective'
import AcPricePreview from '../../price_preview/AcPricePreview.vue'
import LineItem from '@/types/LineItem'

@Component({
  components: {AcPricePreview, AcBoundField},
})
export default class AcInvoiceForm extends mixins(Subjective) {
  @Prop({required: true})
  public newInvoice!: FormController

  @Prop({required: true})
  public escrowDisabled!: boolean

  @Prop({required: true})
  public lineItems!: LineItem[]

  @Prop({default: true})
  public showBuyer!: boolean
}
</script>
