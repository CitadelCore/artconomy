<template>
  <v-container fluid class="pa-0 ma-0">
    <v-row no-gutters v-if="commentList.moreAvailable || showHistory">
      <v-col v-if="commentList.moreAvailable">
        <v-btn block @click="commentList.next">
          <v-icon left>expand_more</v-icon>Load More<v-icon right>expand_more</v-icon>
        </v-btn>
      </v-col>
      <v-col class="text-center" v-if="showHistory">
        <v-btn @click="historyToggle = !historyToggle" class="comment-history-button">
          <v-icon left v-if="historyToggle">visibility</v-icon>
          <v-icon left v-else>visibility_off</v-icon>
          Toggle History
        </v-btn>
      </v-col>
    </v-row>
    <ac-load-section min-height="10rem" :controller="commentList">
      <template v-slot:default>
        <template v-for="(comment, index) in commentList.list">
          <ac-comment
              :comment="comment"
              :username="comment.x.user && comment.x.user.username"
              :commentList="commentList"
              :key="comment.x.id"
              :nesting="nesting"
              :toplevel="true"
              :locked="locked"
              :alternate="!(index % 2)"
              :show-history="historyToggle"
              :in-history="inHistory"
          >
          </ac-comment>
          <v-divider v-if="index + 1 !== commentList.length" :key="'divider-' + index"></v-divider>
        </template>
      </template>
    </ac-load-section>
    <ac-loading-spinner v-if="commentList.fetching" min-height="10rem"></ac-loading-spinner>
    <slot v-if="commentList.ready && !commentList.list.length" name="empty"></slot>
    <ac-new-comment ref="newComment" v-if="commentList.ready && !locked && !inHistory" :commentList="commentList" :alternate="!(commentList.list.length % 2)" :guest-ok="guestOk" :extra-data="extraData"/>
    <v-row no-gutters v-if="locked && commentList.ready &&!inHistory"  >
      <v-col cols="12" class="col-12 text-section text-center">Comments have been locked.</v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import {Prop, Watch} from 'vue-property-decorator'
import Comment from '@/types/Comment'
import {SingleController} from '@/store/singles/controller'
import {ListController} from '@/store/lists/controller'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import AcNewComment from '@/components/comments/AcNewComment.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {QueryParams} from '@/store/helpers/QueryParams'
import {RawData} from '@/store/forms/types/RawData'

  @Component({
    components: {AcLoadSection, AcNewComment, AcLoadingSpinner},
  })
export default class AcCommentSection extends mixins(Viewer) {
    @Prop({default: false})
    public nesting!: boolean

    @Prop()
    public parent!: SingleController<Comment>

    @Prop({default: false})
    public locked!: boolean

    @Prop({default: false})
    public guestOk!: boolean

    @Prop({default: false})
    public showHistory!: boolean

    @Prop({default: false})
    public inHistory!: boolean

    @Prop({default: false})
    public hardFail!: boolean

    @Prop({default: () => ({})})
    public extraData!: RawData

    @Prop({required: true})
    public commentList!: ListController<Comment>

    public historyToggle = false

    public beforeCreate() {
      // Avoid circular definition loop.
      // @ts-ignore
      this.$options.components.AcComment = require('@/components/comments/AcComment.vue').default
    }

    public adjustParams() {
      if (this.historyToggle) {
        /* istanbul ignore next */
        this.commentList.params = {...this.commentList.params || {} as QueryParams, ...{history: '1'}}
      } else {
        /* istanbul ignore next */
        const params = {...this.commentList.params || {} as QueryParams}
        delete params.history
        this.commentList.params = params
      }
      if ((this.commentList.ready || this.commentList.failed || this.commentList.fetching)) {
        this.commentList.reset()
      }
    }

    @Watch('historyToggle')
    public updateHistory(newVal: boolean, oldVal: boolean|undefined) {
      this.adjustParams()
    }

    public created() {
      this.adjustParams()
      const runPromise = this.commentList.firstRun()
      /* istanbul ignore if */
      if (this.hardFail) {
        runPromise.catch(this.setError)
      }
      if (!this.commentList.state.reverse) {
        throw Error('Comment lists should always be reversed!')
      }
    }
}
</script>
