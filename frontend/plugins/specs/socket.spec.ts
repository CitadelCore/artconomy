import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {socketNameSpace, VueSocket} from '@/plugins/socket'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {VueConstructor} from 'vue'
import WS from 'jest-websocket-mock'
import Mock = jest.Mock
import flushPromises from 'flush-promises'

let localVue: VueConstructor
let server: WS
let empty: Wrapper<Vue>
jest.useRealTimers()

socketNameSpace.socketClass = WebSocket

const initialize = () => {
  localVue = createLocalVue()
  server = new WS('ws://test:1234', {jsonProtocol: true})
  localVue.use(VueSocket, {endpoint: 'ws://test:1234'})
  empty = mount(Empty, {localVue: localVue})
}

describe('socket.ts message handlers', () => {
  beforeEach(() => {
    initialize()
  })
  afterEach(() => {
    WS.clean()
  })
  it('Uses a registered handler', async() => {
    const used = jest.fn()
    const fails = jest.fn()
    const unused = jest.fn()
    const mockError = jest.spyOn(console, 'error')
    mockError.mockImplementationOnce(() => undefined)
    fails.mockImplementation(() => {
      throw Error('I broke!')
    })
    empty.vm.$sock.addListener('used', fails)
    empty.vm.$sock.addListener('used', used)
    empty.vm.$sock.addListener('unused', used)
    empty.vm.$sock.open()
    await server.connected
    server.send({name: 'used', payload: {test: 'stuff'}})
    expect(unused).not.toHaveBeenCalled()
    expect(used).toHaveBeenCalledWith({test: 'stuff'})
    expect(fails).toHaveBeenCalledWith({test: 'stuff'})
    expect(mockError).toHaveBeenCalledWith(Error('I broke!'))
    server.close()
    await server.closed
  })
  it('Handles an undefined command', async() => {
    // The command name key is 'name', not 'command'.
    empty.vm.$sock.open()
    await server.connected
    const message = {command: 'test', payload: {wat: 'do'}}
    expect(() => server.send(message)).toThrow(
      Error(`Received undefined command! Message data was: ${JSON.stringify(message)}`),
    )
  })
  it('Handles a valid command without a listener', async() => {
    // The command name key is 'name', not 'command'.
    empty.vm.$sock.open()
    await server.connected
    server.send({name: 'test', payload: {wat: 'do'}})
  })
  it('Sends a message to the server', async() => {
    empty.vm.$sock.open()
    await server.connected
    empty.vm.$sock.send('example',{test: 'data'})
    await expect(server).toReceiveMessage({name: 'example', payload: {test: 'data'}})
  })
})

describe('socket.ts connection handlers', () => {
  let connected: Mock
  let disconnected: Mock
  beforeEach(() => {
    initialize()
    connected = jest.fn()
    disconnected = jest.fn()
    empty.vm.$sock.connectListeners.push(connected)
    empty.vm.$sock.disconnectListeners.push(disconnected)
    empty.vm.$sock.open()
  })
  afterEach(() => {
    WS.clean()
  })
  it('Handles a connection', async() => {
    await server.connected
    expect(connected).toHaveBeenCalled()
    expect(disconnected).not.toHaveBeenCalled()
  })
  it('Handles disconnection', async() => {
    await server.connected
    server.close()
    expect(disconnected).toHaveBeenCalled()
  })
  it('Handles forced disconnection', async() => {
    await server.connected
    server.error()
    expect(disconnected).toHaveBeenCalled()
  })
})
