import mockAxios from '@/specs/helpers/mock-axios'
import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)

describe('Profiles store', () => {
  let store: ArtStore
  let vue: Vue
  let localVue: VueConstructor
  beforeEach(() => {
    mockAxios.reset()
    localVue = createLocalVue()
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    store = createStore()
  })
  it('Sets the viewer username to a token value if the user is not logged in', async() => {
    expect((store.state as any).profiles.viewerRawUsername).toBe('_')
  })
})
