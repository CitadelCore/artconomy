<template>
  <v-container class="faq">
    <ac-tab-nav :items="items" label="Category" />
    <router-view />
  </v-container>
</template>
<script lang="ts">
import {setMetaContent, updateTitle} from '@/lib/lib'
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {SingleController} from '@/store/singles/controller'
import Pricing from '@/types/Pricing'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {Watch} from 'vue-property-decorator'
import StripeCountryList from '@/types/StripeCountryList'
@Component({
  components: {AcTabNav},
})
export default class FAQ extends mixins(Viewer) {
  public pricing: SingleController<Pricing> = null as unknown as SingleController<Pricing>
  public stripeCountries: SingleController<StripeCountryList> = null as unknown as SingleController<StripeCountryList>
  public get items() {
    return [
      {
        value: {name: 'About'}, text: 'About',
      },
      {
        value: {name: 'BuyAndSell'}, text: 'Buying/Selling',
      },
      {
        value: {name: 'Other'}, text: 'Other/Misc',
      },
    ]
  }

  @Watch('$route')
  public updateTracker() {
    /* istanbul ignore if */
    if (!this.$route.params.question) {
      return
    }
    window._paq.push(['trackPageView'])
  }

  public created() {
    this.pricing = this.$getSingle('pricing', {endpoint: '/api/sales/v1/pricing-info/'})
    this.stripeCountries = this.$getSingle('stripeCountries', {endpoint: '/api/sales/v1/stripe-countries/', persist: true, x: {countries: []}})
    this.stripeCountries.get()
    updateTitle('Frequently Asked Questions -- Artconomy')
    setMetaContent(
      'description',
      'Learn how Artconomy works, how to buy art safely online, and how to make money selling your art!',
    )
    if (this.$route.name === 'FAQ') {
      this.$router.replace({name: 'About'})
    }
  }
}
</script>
