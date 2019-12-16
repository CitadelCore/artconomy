import Vue from 'vue'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import {genProduct, genUser} from '@/specs/helpers/fixtures'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {Vuetify} from 'vuetify'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('AcProductPreview.ts', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', () => {
    setViewer(store, genUser())
    wrapper = mount(
      AcProductPreview, {
        localVue,
        store,
        vuetify,
        stubs: ['router-link'],
        propsData: {product: genProduct()},
        sync: false,
        attachToDocument: true,
      })
  })
})
