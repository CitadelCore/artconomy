import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {Vuetify} from 'vuetify/types'
import {ArtStore, createStore} from '@/store'
import {cleanUp, confirmAction, createVuetify, flushPromises, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {commentSet} from './fixtures'
import AcComment from '@/components/comments/AcComment.vue'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import {goToNameSpace} from '@/plugins/shortcuts'

const localVue = vueSetup()
localVue.use(Router)
jest.useFakeTimers()
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('AcComment.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({mode: 'history',
      routes: [{
        path: '/',
        name: 'Home',
        component: Empty,
      }, {
        path: '/:username/',
        name: 'Profile',
        component: Empty,
        children: [
          {path: 'products', name: 'Products', component: Empty},
        ],
      },
      ]})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Handles a comment', async() => {
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.alternate').exists()).toBe(false)
    expect(wrapper.find('.subcomments').exists()).toBe(false)
  })
  it('Handles a comment with children', async() => {
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[1],
        username: commentList.list[1].x.user.username,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.subcomments').exists()).toBe(true)
  })
  it('Scrolls to the comment if it is to be highlighted', async() => {
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const mockScrollTo = jest.spyOn(goToNameSpace, 'goTo')
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    router.replace({name: 'Home', query: {commentId: '17'}})
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
      },
      sync: false,
      attachToDocument: true,
    })
    await wrapper.vm.$nextTick()
    expect(mockScrollTo).toHaveBeenCalledWith('#comment-17')
  })
  it('Sets an alternate coloration', async() => {
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[1],
        username: commentList.list[1].x.user.username,
        alternate: true,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.alternate').exists()).toBe(true)
  })
  it('Allows for a reply', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: true,
      },
      sync: false,
      attachToDocument: true,
    })
    const replyButton = wrapper.find('.reply-button')
    expect(replyButton.exists()).toBe(true)
    replyButton.trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.new-comment textarea').setValue('Response comment!')
    wrapper.find('.new-comment .cancel-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.new-comment textarea').exists()).toBe(false)
  })
  it('Allows for a reply by another user', async() => {
    const user = genUser()
    user.id = 234
    user.username = 'Vulpes'
    user.is_staff = false
    user.is_superuser = false
    setViewer(store, user)
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    const comments = {...commentSet, ...{results: [commentSet.results[0]]}}
    commentList.response = {...comments}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: 'Fox',
        nesting: true,
      },
      sync: false,
      attachToDocument: true,
    })
    const replyButton = wrapper.find('.reply-button')
    expect(replyButton.exists()).toBe(true)
    replyButton.trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.new-comment textarea').setValue('Response comment!')
    wrapper.find('.new-comment .cancel-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.new-comment textarea').exists()).toBe(false)
  })
  it('Does not allow for a reply when nesting is disabled', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: false,
      },
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.reply-button').exists()).toBe(false)
  })
  it('Edits a comment', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[0],
        username: commentList.list[0].x.user.username,
        nesting: false,
      },
      sync: false,
      attachToDocument: true,
    })
    wrapper.find('.more-button').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('.edit-button').trigger('click')
    await wrapper.vm.$nextTick()
    wrapper.find('textarea').setValue('Edited message')
    await wrapper.vm.$nextTick()
    wrapper.find('.save-button').trigger('click')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    expect(mockAxios.patch).toHaveBeenCalledWith(
      ...rq('/api/comments/17/', 'patch', {text: 'Edited message'}, {cancelToken: {}}),
    )
    mockAxios.mockResponse(rs({
      id: 17,
      text: 'Edited message',
      created_on: '2019-06-26T05:38:35.922476-05:00',
      edited_on: '2019-06-26T05:38:35.922499-05:00',
      user: {
        id: 3,
        username: 'Fox',
        avatar_url: 'https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80',
        stars: '4.25',
        is_staff: true,
        is_superuser: true,
        guest: false,
        artist_mode: null,
      },
      comments: [],
      comment_count: 0,
      edited: true,
      deleted: false,
      subscribed: true,
      system: false,
    }))
  })
  it('Deletes a comment', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
      },
      sync: false,
      attachToDocument: true,
    })
    expect((wrapper.vm as any).comment.x).toBeTruthy()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    await wrapper.vm.$nextTick()
    expect(mockAxios.delete).toHaveBeenCalledWith(
      ...rq('/api/comments/13/', 'delete'),
    )
    mockAxios.mockResponse(rs(null))
    await flushPromises()
    expect((wrapper.vm as any).comment.x).toBe(false)
  })
  it('Deletes a thread', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
      },
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(false)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBe(false)
  })
  it('Does not delete a thread in history mode', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        showHistory: true,
      },
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(false)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
  })
  it('Does not delete a thread when displaying actual history', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        inHistory: true,
      },
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    expect(vm.comment.x).toBeTruthy()
    vm.comment.updateX({deleted: true})
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
    for (const comment of vm.subCommentList.list) {
      comment.setX(false)
    }
    await vm.$nextTick()
    expect(vm.comment.x).toBeTruthy()
  })
  it('Renders historical comments', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, {localVue, store, router, sync: false})
    const commentList = empty.vm.$getList('commentList', {endpoint: '/api/comments/'})
    commentList.response = {...commentSet}
    commentList.setList(commentSet.results)
    wrapper = mount(AcComment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {
        commentList,
        comment: commentList.list[2],
        username: null,
        nesting: false,
        showHistory: true,
      },
      sync: false,
      attachToDocument: true,
    })
    mockAxios.reset()
    const vm = wrapper.vm as any
    wrapper.find('.more-button').trigger('click')
    await vm.$nextTick()
    wrapper.find('.history-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockAxios.lastReqGet().url).toBe('/api/lib/v1/comments/lib.Comment/13/history/')
    vm.historyList.response = {...commentSet}
    vm.historyList.setList(commentSet.results)
    vm.historyList.fetching = false
    vm.historyList.ready = true
    await vm.$nextTick()
    expect(wrapper.find('.v-dialog .comment').exists()).toBe(true)
  })
})
