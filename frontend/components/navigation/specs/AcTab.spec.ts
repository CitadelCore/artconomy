import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import AcTabs from '@/components/navigation/AcTabs.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcTabNav.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Renders tabs', async() => {
    wrapper = mount(AcTabs, {
      localVue,
      vuetify,
      propsData: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
        }],
        value: 0,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.v-tab').text().replace(/\s\s+/g, ' ')).toBe(
      'people Characters (2)'
    )
  })
  it('Navigates via dropdown', async() => {
    wrapper = mount(AcTabs, {
      localVue,
      vuetify,
      propsData: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
        }],
        value: 0,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.v-select__selections').exists())
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-tab').text().replace(/\s\s+/g, ' ')).toBe(
      'people Characters (2)'
    )
  })
})
