import Vue from 'vue'
import Router from 'vue-router'
import {cleanUp, confirmAction, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {genUser} from '@/specs/helpers/fixtures'
import ConversationDetail from '@/components/views/ConversationDetail.vue'
import {genConversation} from '@/components/views/specs/fixtures'
import mockAxios from '@/__mocks__/axios'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('ConversationDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Profile',
        path: '/profiles/:username/',
        component: Empty,
        props: true,
      }, {
        name: 'AboutUser',
        path: '/profiles/:username/products/',
        component: Empty,
        props: true,
      }, {
        name: 'BuyAndSell',
        path: '/faq/buy-and-sell',
        component: Empty,
        props: true,
      }, {
        name: 'Conversations',
        path: '/messages/:username/',
        component: Empty,
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads a lock toggle for an outside user', async() => {
    const user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox', conversationId: 23},
      attachTo: docTarget(),

    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.lock-toggle').exists()).toBe(true)
  })
  it('Does not load a lock toggle for an inside user', async() => {
    const user = genUser()
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox', conversationId: 23},
      attachTo: docTarget(),

    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.lock-toggle').exists()).toBe(false)
  })
  it('Leaves a conversation', async() => {
    const user = genUser()
    setViewer(store, user)
    const wrapper = mount(ConversationDetail, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox', conversationId: 23},
      attachTo: docTarget(),

    })
    const vm = wrapper.vm as any
    vm.conversation.setX(genConversation())
    vm.conversation.fetching = false
    vm.conversation.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.delete-button'])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await vm.$nextTick()
    expect(router.currentRoute.name).toBe('Conversations')
  })
})
