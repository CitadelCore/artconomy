<template>
  <ac-base-notification :asset-link="assetLink" :notification="notification">
        <span slot="title">
      <router-link :to="assetLink">
        A submission was shared with you
      </router-link>
    </span>
    <span slot="subtitle">
      <router-link :to="assetLink">"{{event.data.submission.title}}" was shared by {{event.data.user.username}}</router-link>
    </span>
  </ac-base-notification>
</template>

<script>
import Notification from '../mixins/notification'
import AcBaseNotification from '@/components/views/notifications/events/AcBaseNotification'

export default {
  name: 'ac-submission-shared',
  components: {AcBaseNotification},
  mixins: [Notification],
  data() {
    return {}
  },
  computed: {
    assetLink() {
      if (this.event.data.submission) {
        return {name: 'Submission', params: {submissionId: this.event.data.submission.id}}
      } else {
        return {}
      }
    },
  },
}
</script>

<style scoped>

</style>
