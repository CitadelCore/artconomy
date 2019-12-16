import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import AcAudioPlayer from '@/components/AcAudioPlayer.vue'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('AcAudioPlayer.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
    mockError.mockClear()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads and types an audio file', async() => {
    const submission = genSubmission()
    submission.file = {full: 'https://example.com/thing.mp3'}
    wrapper = mount(AcAudioPlayer, {localVue, propsData: {asset: submission}})
    const vm = wrapper.vm as any
    expect(vm.type).toBe('audio/mp3')
  })
})
