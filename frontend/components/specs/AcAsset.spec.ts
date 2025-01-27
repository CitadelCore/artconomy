import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, setViewer, vueSetup, mount} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import AcAsset from '@/components/AcAsset.vue'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcAsset.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads and previews an asset', async() => {
    setViewer(store, genUser())
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link'],
      propsData: {asset: genSubmission(), thumbName: 'full'},

    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe('https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png')
  })
  it('Does not load an asset if the viewer is nerfed.', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.sfw_mode = true
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link'],

      propsData: {asset: submission, thumbName: 'full'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer).toBe(undefined)
    expect(vm.nerfed).toBe(true)
    expect(wrapper.find('.nerfed-message').exists()).toBe(true)
  })
  it('Does not load an asset if the maximum rating is under the asset rating.', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'full'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer).toBe(undefined)
    expect(vm.nerfed).toBe(false)
    expect(wrapper.find('.rating-info').exists()).toBe(true)
  })
  it('Uses a sensible default aspect ratio if the image cannot be displayed and none is specified.',
    async(
    ) => {
      const viewer = genUser()
      const submission = genSubmission()
      submission.rating = 2
      viewer.rating = 1
      setViewer(store, viewer)
      wrapper = mount(AcAsset, {
        store,
        localVue,
        vuetify,

        stubs: ['router-link'],
        propsData: {asset: submission, thumbName: 'full', aspectRatio: null},
      },
      )
      await wrapper.vm.$nextTick()
      const vm = wrapper.vm as any
      expect(vm.ratio).toBe(1)
    })
  it('Handles a null asset', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: null, thumbName: 'full'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe('/static/images/default-avatar.png')
    // Since the output will be an image, we consider this true.
    expect(vm.isImage).toBe(true)
    expect(vm.blacklisted).toEqual([])
    expect(vm.displayComponent).toBe(null)
  })
  it('Handles a null asset with a custom fallback URL', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: null, thumbName: 'full', fallbackImage: 'boop.jpg'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe('boop.jpg')
    // Since the output will be an image, we consider this true.
    expect(vm.isImage).toBe(true)
    expect(vm.blacklisted).toEqual([])
    expect(vm.displayComponent).toBe(null)
    expect(vm.fullUrl).toBe('boop.jpg')
    expect(vm.assetRating).toBe(0)
  })
  it('Determines an asset rating', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'full', aspectRatio: null},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.assetRating).toBe(2)
  })
  it('Handles an anonymous user', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.rating = 2
    viewer.rating = 1
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: null, thumbName: 'full'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe('/static/images/default-avatar.png')
    expect(vm.isImage).toBe(true)
    expect(vm.blacklisted).toEqual([])
  })
  it('Handles alternative file types', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp4', __type__: 'data:swf'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link'],

      propsData: {asset: submission, thumbName: 'full'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer).toBe(undefined)
    expect(vm.displayComponent).toBe('ac-video-player')
  })
  it('Displays a thumbnail', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe(
      'https://artconomy.vulpinity.com/media/art/2019/07/26/kairef-color.png.300x300_q85_crop-,0.png',
    )
  })
  it('Displays a preview', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.preview = {thumbnail: 'https://example.com/thing.jpg'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe(
      'https://example.com/thing.jpg',
    )
  })
  it('Handles a non-previewable file type', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.doc', __type__: 'data:word'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe(
      'http://localhost/static/icons/DOC.png',
    )
  })
  it('Handles the special case of an SVG', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.svg', __type__: 'data:image'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe(
      'https://example.com/thing.svg',
    )
  })
  it('Handles the special case of a GIF', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {
      full: 'https://example.com/thing.gif',
      gallery: 'https://example.com/thumb.gif',
      __type__: 'data:image',
    }
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,

      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'gallery'},
    },
    )
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.$refs.imgContainer.src).toBe(
      'https://example.com/thing.gif',
    )
  })
  it('Fetches asset tags', async() => {
    const viewer = genUser()
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.svg', __type__: 'data:svg'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},

    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    expect(vm.tags).toEqual([
      'red_panda', 'wah', 'cool', 'nosings', 'awesome', 'stuff', 'floofy',
      'feets', 'female', 'notable', 'fuzzy', 'fuckable', 'soft_paws',
    ])
    wrapper.setProps({asset: null, thumbName: 'thumbnail'})
    await vm.$nextTick()
    expect(vm.tags).toEqual([])
  })
  it('Hides the asset if item has a blacklisted tag', async() => {
    const viewer = genUser()
    viewer.blacklist.push('fuckable', 'bork')
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.svg', __type__: 'data:svg'}
    setViewer(store, viewer)
    wrapper = mount(AcAsset, {
      store,
      localVue,
      vuetify,
      stubs: ['router-link'],
      propsData: {asset: submission, thumbName: 'thumbnail'},

    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.blacklisted).toEqual(['fuckable'])
    expect(vm.canDisplay).toBe(false)
    expect(wrapper.find('.blacklist-info').exists()).toBe(true)
    expect(wrapper.find('.asset-image').exists()).toBe(false)
  })
})
