<template>
  <v-input v-bind="passedProps" class="ac-uppy-file">
    <v-col class="text-center mb-2" v-if="label" >
      <v-label :for="$attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
    </v-col>
    <ac-paginated :list="submissionList" class="submission-list-container" v-if="submissionList">
      <template v-slot:default>
        <v-col cols="6" sm="6" md="3" class="submission-container" v-for="submission in submissionList.list" :key="submission.x && derived(submission).id">
          <v-row no-gutters   v-if="submission.x">
            <v-col cols="12">
              <ac-gallery-preview class="pa-1"
                                  @click.native.capture.stop.prevent="select(derived(submission).id)"
                                  :key="derived(submission).id"
                                  :submission="derived(submission)" :show-footer="true"
              >
                <template v-slot:stats-append>
                  <v-spacer></v-spacer>
                  <v-col class="text-right"  slot="stats-append">
                    <v-progress-circular
                        :color="$vuetify.theme.currentTheme.secondary.base"
                        indeterminate
                        :size="24"
                        v-if="loading === derived(submission).id"
                    ></v-progress-circular>
                    <v-icon v-if="derived(submission).id === compare" color="green">check_circle</v-icon>
                  </v-col>
                </template>
              </ac-gallery-preview>
            </v-col>
            <v-col class="text-center" cols="12" v-if="removable" >
              <v-btn @click="$emit('remove', submission)" color="danger" class="remove-submission">Unlink Sample</v-btn>
            </v-col>
          </v-row>
        </v-col>
      </template>
    </ac-paginated>
  </v-input>
</template>

<style scoped lang="sass">

</style>

<script lang="ts">
import Vue from 'vue'
import Component, {mixins} from 'vue-class-component'
import AcAsset from '../AcAsset.vue'
import {ListController} from '@/store/lists/controller'
import {Prop, Watch} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Submission from '@/types/Submission'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import ExtendedInput from '@/components/fields/mixins/extended_input'
import {genId} from '@/lib/lib'
import {SingleController} from '@/store/singles/controller'
import {makeSpace, mount} from '@/specs/helpers'

  @Component({
    components: {AcGalleryPreview, AcPaginated, AcLoadSection, AcAsset},
  })
export default class AcSubmissionSelect extends mixins(ExtendedInput) {
    @Prop()
    public list!: ListController<Submission>

    @Prop({required: true})
    public value!: Submission|number|null

    @Prop()
    public saveComparison!: Submission|null

    @Prop()
    public queryEndpoint!: string

    @Prop({default: false})
    public related!: boolean

    @Prop({default: false})
    public removable!: boolean

    public submissionList: ListController<Submission> = null as unknown as ListController<Submission>
    public loading: number|false = false

    public select(id: number) {
      if (this.compare !== id) {
        this.loading = id
      }
      this.$emit('input', id)
    }

    @Watch('list')
    public updateSubmissionList(controller: ListController<Submission>) {
      /* istanbul ignore else */
      if (controller) {
        Vue.set(this, 'submissionList', controller)
        controller.firstRun()
      }
    }

    @Watch('compare')
    public stopProgress() {
      this.loading = false
    }

    public derived(item: SingleController<Submission>) {
      if (this.related) {
        const submission = item as any
        return submission.x && submission.x.submission
      }
      return item.x
    }

    public get compare() {
      if (this.saveComparison !== undefined) {
        return this.saveComparison && this.saveComparison.id
      }
      return this.value
    }

    public created() {
      if (this.queryEndpoint) {
        this.submissionList = this.$getList(genId(), {endpoint: this.queryEndpoint})
      } else {
        this.submissionList = this.list
      }
      if (this.submissionList) {
        this.submissionList.firstRun()
      }
    }
}
</script>
