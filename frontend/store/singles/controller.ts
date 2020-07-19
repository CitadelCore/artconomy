import Component from 'vue-class-component'
import {SingleModuleOpts} from './types/SingleModuleOpts'
import {SingleState} from './types/SingleState'
import {SingleModule} from './index'
import {BaseController} from '@/store/controller-base'
import {singleRegistry} from '@/store/singles/registry'
import {RawData} from '@/store/forms/types/RawData'
import {SinglePatchers} from '@/store/singles/types/SinglePatchers'
import {Patch} from '@/store/singles/patcher'

@Component
export class SingleController<T extends {}> extends BaseController<SingleModuleOpts<T>, SingleState<T>> {
  public baseClass = SingleModule
  public forceRecomputeCounter = 0

  // @ts-ignore
  public registry = singleRegistry

  public baseModuleName = 'singles'

  // eslint-disable-next-line camelcase
  public single_controller__ = true

  public created() {
    this.register()
  }

  public get() {
    return this.dispatch('get')
  }

  public patch(data: Partial<T>) {
    return this.dispatch('patch', data)
  }

  public delete() {
    return this.dispatch('delete')
  }

  public put(data?: any) {
    return this.dispatch('put', data)
  }

  public setX(x: T | null | false) {
    // Also available as a setter.
    if (this.x && !x) {
      this.forceRecomputeCounter += 1
    }
    this.commit('setX', x)
  }

  public getModel() {
    const self = this
    const patchers = self.patchers
    type KeyType = keyof T
    return new Proxy({}, {
      get(target, propName: KeyType) {
        return patchers[propName].model
      },
      set(target, propName: KeyType, value: T[KeyType]): any {
        patchers[propName].model = value
        return true
      },
    })
  }

  public getPatcher() {
    const self = this
    return new Proxy({cached: {} as SinglePatchers<T>}, {
      get(target, propName: keyof T): Patch {
        if (target.cached[propName] === undefined) {
          target.cached[propName] = self.$makePatcher({modelProp: '', attrName: propName as string, silent: true})
        }
        return target.cached[propName]
      },
    })
  }

  public updateX(x: Partial<T>) {
    this.commit('updateX', x)
  }

  public retryGet() {
    return this.dispatch('retryGet')
  }

  public get x(): T | null | false {
    return this.attr('x')
  }

  public set x(x: T | null | false) {
    this.setX(x)
  }

  public get endpoint(): string {
    return this.attr('endpoint')
  }

  public set endpoint(val: string) {
    this.commit('setEndpoint', val)
  }

  public get fetching(): boolean {
    return this.attr('fetching')
  }

  public set fetching(val: boolean) {
    this.commit('setFetching', val)
  }

  public get ready(): boolean {
    return this.attr('ready')
  }

  public set ready(val: boolean) {
    this.commit('setReady', val)
  }

  public set params(val: RawData|null) {
    this.commit('setParams', val)
  }

  public get params() {
    return this.attr('params')
  }

  public get failed(): boolean {
    return this.attr('failed')
  }

  public refresh() {
    this.ready = false
    return this.get()
  }

  public makeReady(val: T) {
    // For tests or preloading. Sets X and clears status flags.
    this.setX(val)
    this.ready = true
    this.fetching = false
  }

  public get model(): T {
    // eslint-disable-next-line no-unused-expressions
    this.forceRecomputeCounter
    return this.getModel() as unknown as T
  }

  public get patchers(): SinglePatchers<T> {
    // eslint-disable-next-line no-unused-expressions
    this.forceRecomputeCounter
    return this.getPatcher() as unknown as SinglePatchers<T>
  }
}
