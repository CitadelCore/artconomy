import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {createVuetify, docTarget, setViewer, vueSetup, vuetifySetup, mount} from '@/specs/helpers'
import mockAxios from '@/__mocks__/axios'
import AcProductSelect from '@/components/fields/AcProductSelect.vue'
import {genUser} from '@/specs/helpers/fixtures'
import {ArtStore, createStore} from '@/store'

const localVue = vueSetup()
jest.useFakeTimers()
let wrapper: Wrapper<Vue>
let store: ArtStore
let vuetify: Vuetify

describe('AcProductSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
      mockAxios.reset()
      jest.clearAllTimers()
    }
  })
  it('Calls a custom display handler', () => {
    setViewer(store, genUser())
    wrapper = mount(
      AcProductSelect, {
        localVue,
        store,
        vuetify,

        attachTo: docTarget(),
        propsData: {
          value: 1,
          multiple: false,
          username: 'Fox',
          initItems: [{name: 'Test', id: 1, starting_price: 2.50}, {username: 'Test2', id: 2, starting_price: 2.50}],
        },
      },
    )
  })
})
