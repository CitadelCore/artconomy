import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import AcTabNav from '@/components/navigation/AcTabNav.vue'
import {VueRouter} from 'vue-router/types/router'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let wrapper: Wrapper<Vue>
let router: VueRouter
let vuetify: Vuetify

describe('AcTabNav.vue', () => {
  beforeEach(() => {
    router = new Router({
      mode: 'history',
      routes: [{
        path: '/characters/:username/',
        component: Empty,
        name: 'Characters',
      }, {
        path: '/gallery/:username/',
        component: Empty,
        name: 'Gallery',
      }, {
        path: '/profile/:username/',
        component: Empty,
        name: 'Profile',
      }],
    })
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Renders tabs', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {
      router,
      localVue,
      vuetify,
      propsData: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
        }],
        label: 'Stuff',
      },
      attachTo: docTarget(),
    })
    expect(wrapper.find('.v-tab').text().replace(/\s\s+/g, ' ')).toBe(
      'people Characters (2)',
    )
  })
  it('Navigates via tab', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {
      router,
      localVue,
      vuetify,
      propsData: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
        }],
        label: 'Stuff',
      },
      attachTo: docTarget(),
    })
    expect(wrapper.vm.$route.name).toBe('Profile')
    wrapper.find('.v-tab').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Characters')
  })
  it('Navigates via dropdown', async() => {
    router.replace('/profile/Fox/')
    wrapper = mount(AcTabNav, {
      router,
      localVue,
      vuetify,
      propsData: {
        items: [{
          value: {name: 'Characters', params: {username: 'Fox'}}, icon: 'people', text: 'Characters', count: 2,
        }, {
          value: {name: 'Gallery', params: {username: 'Fox'}}, icon: 'image', text: 'Gallery',
        }],
        label: 'Stuff',
      },
      attachTo: docTarget(),
    })
    expect(wrapper.vm.$route.name).toBe('Profile')
    wrapper.find('.v-select__selections').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.v-list-item__title').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Characters')
  })
})
