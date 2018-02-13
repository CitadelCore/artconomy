// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import VueFormGenerator from 'vue-form-generator'
import 'vue-form-generator/dist/vfg.css'  // optional full css additions
import 'vuetify/dist/vuetify.min.css'
import { $, jQuery } from 'jquery'
import Vuetify from 'vuetify'
import BootstrapVue from 'bootstrap-vue'
import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App'
import NavBar from './components/NavBar'
import fieldCharacterSearch from './components/fieldCharacterSearch'
import fieldUserSearch from './components/fieldUserSearch'
import fieldTagSearch from './components/fieldTagSearch'
import fieldRecaptcha from './components/fieldRecaptcha'
import { md } from './lib'
import {ErrorHandler} from './plugins/error'
import {router} from './router'
import { UserHandler } from './plugins/user'
import { Timer } from './plugins/timer'
import { Shortcuts } from './plugins/shortcuts'

// export for others scripts to use
window.$ = $
window.jQuery = jQuery

Vue.use(VueRouter)
Vue.use(UserHandler)
Vue.use(BootstrapVue)
Vue.use(VueFormGenerator)
Vue.use(ErrorHandler)
Vue.use(Timer)
Vue.use(Shortcuts)
Vue.use(Vuetify)
Vue.config.productionTip = false
Vue.component('fieldCharacterSearch', fieldCharacterSearch)
Vue.component('fieldUserSearch', fieldUserSearch)
Vue.component('fieldTagSearch', fieldTagSearch)
Vue.component('fieldRecaptcha', fieldRecaptcha)

/* eslint-disable no-new */
window.artconomy = new Vue({
  el: '#app',
  router,
  template: '<App :user="user"/>',
  components: {App, NavBar},
  data: {
    userCache: {},
    md: md,
    $unread: 0,
    errorCode: null,
    fetchStarted: false
  },
  created () {
    this.$loadUser()
  },
  methods: {
    log (data) {
      // eslint-disable-next-line
      console.log(data)
      return data
    }
  }
})
