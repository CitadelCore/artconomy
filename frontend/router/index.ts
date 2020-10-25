import Router, {Route, RouteConfig} from 'vue-router'
import {clearMetaTag, paramsKey, saneNav, setCookie, setMetaContent} from '@/lib/lib'
import {ArtStore} from '@/store'
import {VueRouter} from 'vue-router/types/router'
import deepEqual from 'fast-deep-equal'
import RevisionDetail from '@/components/views/order/deliverable/RevisionDetail.vue'
import ReferenceDetail from '@/components/views/order/deliverable/ReferenceDetail.vue'
import DeliverableRevisions from '@/components/views/order/deliverable/DeliverableRevisions.vue'
import DeliverableOverview from '@/components/views/order/deliverable/DeliverableOverview.vue'
import DeliverablePayment from '@/components/views/order/deliverable/DeliverablePayment.vue'
import DeliverableReferences from '@/components/views/order/deliverable/DeliverableReferences.vue'
import DeliverableListing from '@/components/views/order/OrderDetail.vue'
import Reload from '@/components/views/Reload.vue'
import Login from '@/components/views/Login.vue'
import CommissionAgreement from '@/components/views/legal/CommissionAgreement.vue'
import RefundPolicy from '@/components/views/legal/RefundPolicy.vue'
import TermsOfService from '@/components/views/legal/TermsOfService.vue'
import PrivacyPolicy from '@/components/views/legal/PrivacyPolicy.vue'
import Notifications from '@/components/views/notifications/Notifications.vue'
import Profile from '@/components/views/profile/Profile.vue'
import Policies from '@/components/views/legal/Policies.vue'
import Contact from '@/components/views/Contact.vue'
import Store from '@/components/views/store/Store.vue'
import Reports from '@/components/views/Reports.vue'
import Journal from '@/components/views/Journal.vue'
import ProductDetail from '@/components/views/product/ProductDetail.vue'
import FAQ from '@/components/views/faq/FAQ.vue'
import Settings from '@/components/views/settings/Settings.vue'
import Options from '@/components/views/settings/Options.vue'
import Artist from '@/components/views/settings/Artist.vue'
import Credentials from '@/components/views/settings/Credentials.vue'
import Avatar from '@/components/views/settings/Avatar.vue'
import Payment from '@/components/views/settings/payment/Payment.vue'
import Submission from '@/components/views/submission/SubmissionDetail.vue'
import Search from '@/components/views/search/Search.vue'
import CharacterGallery from '@/components/views/character/CharacterGallery.vue'
import NotFound from '@/components/views/NotFound.vue'
import ConversationDetail from '@/components/views/ConversationDetail.vue'
import PasswordReset from '@/components/views/PasswordReset.vue'
import Purchase from '@/components/views/settings/payment/Purchase.vue'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'
import Payout from '@/components/views/settings/payment/Payout.vue'
import NotificationsList from '@/components/views/notifications/NotificationsList.vue'
import About from '@/components/views/faq/About.vue'
import BuyAndSell from '@/components/views/faq/BuyAndSell.vue'
import Other from '@/components/views/faq/Other.vue'
import ConversationsList from '@/components/views/ConversationsList.vue'
import AboutUser from '@/components/views/profile/AboutUser.vue'
import Products from '@/components/views/profile/Products.vue'
import Characters from '@/components/views/profile/Characters.vue'
import Gallery from '@/components/views/profile/Gallery.vue'
import Watchlists from '@/components/views/profile/Watchlists.vue'
import CharacterDetail from '@/components/views/character/CharacterDetail.vue'
import SubmissionList from '@/components/views/profile/SubmissionList.vue'
import SearchProducts from '@/components/views/search/SearchProducts.vue'
import SearchCharacters from '@/components/views/search/SearchCharacters.vue'
import SearchProfiles from '@/components/views/search/SearchProfiles.vue'
import SearchSubmissions from '@/components/views/search/SearchSubmissions.vue'
import ProductHints from '@/components/views/search/hints/ProductHints.vue'
import SubmissionHints from '@/components/views/search/hints/SubmissionHints.vue'
import CharacterHints from '@/components/views/search/hints/CharacterHints.vue'
import ProfileHints from '@/components/views/search/hints/ProfileHints.vue'
import Home from '@/components/views/Home.vue'
import ProductExtra from '@/components/views/search/extra/ProductExtra.vue'
import NewOrder from '@/components/views/product/NewOrder.vue'
import DeliverableDetail from '@/components/views/order/DeliverableDetail.vue'
import OrderList from '@/components/views/orders/OrderList.vue'
import Orders from '@/components/views/orders/Orders.vue'
import SessionSettings from '@/components/views/SessionSettings.vue'
import Ratings from '@/components/views/Ratings.vue'
import SubmissionExtra from '@/components/views/search/extra/SubmissionExtra.vue'
import ReferralsAndTools from '@/components/views/referrals/ReferralsAndTools.vue'
import LinksAndStats from '@/components/views/referrals/LinksAndStats.vue'
import Tools from '@/components/views/referrals/Tools.vue'
import Upgrade from '@/components/views/Upgrade.vue'
import WatchList from '@/components/views/profile/WatchList.vue'
import ClaimOrder from '@/components/views/ClaimOrder.vue'
import Premium from '@/components/views/settings/Premium.vue'
import Redirect from '@/components/views/Redirect.vue'
import ShieldCommissioner from '@/components/views/landing/ShieldCommissioner.vue'
import AlwaysOpen from '@/components/views/landing/AlwaysOpen.vue'
import ShieldArtist from '@/components/views/landing/ShieldArtist.vue'
import RedirectToViewer from '@/components/views/RedirectToViewer.vue'
import ArtistTools from '@/components/views/landing/ArtistTools.vue'

function orderViews() {
  const orderRoutes: RouteConfig[] = []
  for (const baseName of ['Order', 'Sale', 'Case']) {
    const props = (route: Route) => {
      return {...route.params, baseName}
    }
    const category = baseName.toLowerCase()
    orderRoutes.push({
      name: baseName,
      path: `/${category}s/:username/${category}/:orderId/`,
      component: DeliverableListing,
      props,
      children: [{
        name: `${baseName}Deliverable`,
        path: 'deliverables/:deliverableId',
        props,
        component: DeliverableDetail,
        children: [{
          name: `${baseName}DeliverableOverview`,
          path: 'overview',
          props,
          component: DeliverableOverview,
        }, {
          name: `${baseName}DeliverableReferences`,
          path: 'references',
          props,
          component: DeliverableReferences,
          children: [{
            name: `${baseName}DeliverableReference`,
            path: ':referenceId/',
            props,
            component: ReferenceDetail,
          }],
        }, {
          name: `${baseName}DeliverableRevisions`,
          path: 'revisions',
          props,
          component: DeliverableRevisions,
          children: [{
            name: `${baseName}DeliverableRevision`,
            path: ':revisionId/',
            props,
            component: RevisionDetail,
          }],
        }, {
          name: `${baseName}DeliverablePayment`,
          path: 'payment',
          props,
          component: DeliverablePayment,
        }],
      }],
    })
  }
  return orderRoutes
}

function orderLists() {
  const orderRoutes: RouteConfig[] = []
  for (const baseName of ['Orders', 'Sales', 'Cases']) {
    const children: RouteConfig[] = []
    let categories = ['current', 'archived', 'waiting', 'cancelled']
    if (baseName === 'Cases') {
      categories = ['current', 'archived']
    }
    const type = baseName.toLowerCase()
    for (const category of categories) {
      const routeName = category[0].toUpperCase() + category.slice(1) + baseName
      children.push({
        name: routeName,
        path: category,
        component: OrderList,
        props(route: Route) {
          return {
            username: route.params.username,
            category,
            type,
          }
        },
      })
    }
    orderRoutes.push({
      path: `/${type}/:username/`,
      name: baseName,
      component: Orders,
      children,
      props(route: Route) {
        return {
          username: route.params.username,
          baseName,
        }
      },
    })
  }
  return orderRoutes
}

export const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    props: true,
  },
  {
    path: '/Reload/:path',
    name: 'Reload',
    component: Reload,
  },
  {
    path: '/auth/:tabName?/',
    name: 'Login',
    component: Login,
  },
  {
    path: '/set-password/:username/:resetToken/',
    props: true,
    component: PasswordReset,
  },
  {
    path: '/legal-and-policies/',
    name: 'Policies',
    component: Policies,
  },
  {
    path: '/legal-and-policies/commission-agreement/',
    name: 'CommissionAgreement',
    component: CommissionAgreement,
  },
  {
    path: '/legal-and-policies/refund-policy/',
    name: 'RefundPolicy',
    component: RefundPolicy,
  },
  {
    path: '/legal-and-policies/terms-of-service/',
    name: 'TermsOfService',
    component: TermsOfService,
  },
  {
    path: '/legal-and-policies/privacy-policy/',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy,
  },
  {
    path: '/contact/',
    name: 'Contact',
    component: Contact,
  },
  {
    path: '/notifications/:tabName?/',
    name: 'Notifications',
    component: Notifications,
    props: true,
    children: [
      {
        name: 'CommunityNotifications',
        path: 'community',
        component: NotificationsList,
        props(route: VueRouter) {
          return {subset: 'community', autoRead: true}
        },
      },
      {
        name: 'SalesNotifications',
        path: 'sales',
        component: NotificationsList,
        props(route: VueRouter) {
          return {subset: 'sales', autoRead: false}
        },
      },
    ],
  },
  {
    path: '/store/:username/',
    name: 'Store',
    component: Store,
    props(route: Route) {
      return {
        username: route.params.username,
      }
    },
    children: [
      {
        name: 'Product',
        path: 'product/:productId/',
        component: ProductDetail,
        props: true,
        children: [
          {
            name: 'NewOrder',
            path: 'order',
            component: NewOrder,
            props: true,
          },
        ],
      },
    ],
  },
  {
    path: '/store/:username/iframe/',
    name: 'StoreiFrame',
    component: Store,
    props(route: Route) {
      return {
        username: route.params.username,
        endpoint: `/api/sales/v1/account/${route.params.username}/products/`,
        iFrame: true,
      }
    },
  },
  {
    path: '/upgrade/',
    name: 'Upgrade',
    component: Upgrade,
    props: true,
  },
  {
    path: '/faq/',
    name: 'FAQ',
    component: FAQ,
    children: [
      {
        name: 'About',
        path: 'about/:question?/',
        component: About,
        props: true,
      },
      {
        name: 'BuyAndSell',
        path: 'buying-and-selling/:question?/',
        component: BuyAndSell,
        props: true,
      },
      {
        name: 'Other',
        path: 'other/:question?/',
        component: Other,
        props: true,
      },
    ],
  },
  {
    path: '/my/:viewName/',
    name: 'MyView',
    component: RedirectToViewer,
    props: true,
  },
  {
    path: '/profile/:username/settings/',
    name: 'Settings',
    component: Settings,
    props: true,
    children: [
      {
        name: 'Login Details',
        path: 'credentials',
        component: Credentials,
        props: true,
      },
      {
        name: 'Premium',
        path: 'premium',
        component: Premium,
        props: true,
      },
      {
        name: 'Avatar',
        path: 'avatar',
        component: Avatar,
        props: true,
      },
      {
        name: 'Payment',
        path: 'payment',
        component: Payment,
        props: true,
        children: [
          {
            name: 'Purchase',
            path: 'purchase',
            component: Purchase,
            props: true,
          },
          {
            name: 'Payout',
            path: 'payout',
            component: Payout,
            props: true,
          },
          {
            name: 'TransactionHistory',
            path: 'transactions',
            component: TransactionHistory,
            props: true,
          },
        ],
      },
      {
        name: 'Artist',
        path: 'artist',
        component: Artist,
        props: true,
      },
      {
        name: 'Options',
        path: 'options',
        component: Options,
        props: true,
      },
    ],
  },
  {
    path: '/profile/:username/ratings/',
    name: 'Ratings',
    component: Ratings,
    props: true,
  },
  {
    path: '/profile/:username/referrals/',
    name: 'ReferralsAndTools',
    component: ReferralsAndTools,
    props: true,
    children: [{
      name: 'LinksAndStats',
      path: 'links-and-stats/',
      component: LinksAndStats,
      props: true,
    }, {
      name: 'Tools',
      path: 'tools/',
      component: Tools,
      props: true,
    }],
  },
  {
    path: '/profile/:username/journals/:journalId/',
    name: 'Journal',
    component: Journal,
    props: true,
  },
  {
    path: '/profile/:username/characters/:characterName/',
    name: 'Character',
    component: CharacterDetail,
    props: true,
  },
  {
    path: '/profile/:username/characters/:characterName/gallery/',
    name: 'CharacterGallery',
    component: CharacterGallery,
    props: true,
  },
  {
    path: '/profile/:username/',
    name: 'Profile',
    component: Profile,
    props: true,
    children: [
      {
        path: 'about',
        name: 'AboutUser',
        component: AboutUser,
        props: true,
      },
      {
        path: 'products',
        name: 'Products',
        component: Products,
        props: true,
      },
      {
        path: 'characters',
        name: 'Characters',
        component: Characters,
        props: true,
      },
      {
        path: 'gallery',
        name: 'Gallery',
        component: Gallery,
        props: true,
        children: [{
          path: 'art',
          name: 'Art',
          component: SubmissionList,
          props(route: Route) {
            return {
              ...route.params,
              listName: 'art',
              endpoint: `/api/profiles/v1/account/${route.params.username}/submissions/art/`,
              trackPages: true,
            }
          },
        }, {
          path: 'collection',
          name: 'Collection',
          component: SubmissionList,
          props(route: Route) {
            return {
              ...route.params,
              listName: 'collection',
              endpoint: `/api/profiles/v1/account/${route.params.username}/submissions/collection/`,
              trackPages: true,
            }
          },
        }],
      },
      {
        path: 'favorites',
        name: 'Favorites',
        component: SubmissionList,
        props(route: Route) {
          return {
            ...route.params,
            listName: 'favorites',
            endpoint: `/api/profiles/v1/account/${route.params.username}/favorites/`,
            okStatuses: [403],
            failureMessage: "This user's favorites are hidden.",
          }
        },
      },
      {
        path: 'watchlists',
        name: 'Watchlists',
        component: Watchlists,
        props: true,
        children: [{
          name: 'Watching',
          path: 'watching',
          component: WatchList,
          props(route: Route) {
            return {
              ...route.params,
              nameSpace: 'watching',
              endpoint: `/api/profiles/v1/account/${route.params.username}/watching/`,
            }
          },
        }, {
          name: 'Watchers',
          path: 'watchers',
          component: WatchList,
          props(route: Route) {
            return {
              ...route.params,
              nameSpace: 'watchers',
              endpoint: `/api/profiles/v1/account/${route.params.username}/watchers/`,
            }
          },
        }],
      },
    ],
  },
  {
    path: '/submissions/:submissionId/',
    name: 'Submission',
    component: Submission,
    props: true,
  },
  ...orderViews(),
  ...orderLists(),
  {
    path: '/claim-order/:orderId/:token/:deliverableId?',
    name: 'ClaimOrder',
    component: ClaimOrder,
    props: true,
  },
  {
    path: '/search/',
    name: 'Search',
    component: Search,
    props: true,
    children: [{
      path: 'products',
      name: 'SearchProducts',
      components: {
        default: SearchProducts,
        hints: ProductHints,
        extra: ProductExtra,
      },
      props: true,
    } as RouteConfig, {
      path: 'submissions',
      name: 'SearchSubmissions',
      components: {
        default: SearchSubmissions,
        hints: SubmissionHints,
        extra: SubmissionExtra,
      },
      props: true,
    } as RouteConfig, {
      path: 'characters',
      name: 'SearchCharacters',
      components: {
        default: SearchCharacters,
        hints: CharacterHints,
      },
      props: true,
    } as RouteConfig, {
      path: 'profiles',
      name: 'SearchProfiles',
      components: {
        default: SearchProfiles,
        hints: ProfileHints,
      },
      props: true,
    } as RouteConfig],
  },
  {
    path: '/session/settings/',
    name: 'SessionSettings',
    component: SessionSettings,
  },
  {
    path: '/messages/:username/',
    name: 'Conversations',
    component: ConversationsList,
    props: true,
  },
  {
    path: '/messages/:username/:conversationId/',
    name: 'Conversation',
    component: ConversationDetail,
    props: true,
  },
  {
    path: '/reports/',
    name: 'Reports',
    component: Reports,
  },
  {
    path: '/landing/commission-safely-with-artconomy-shield/',
    name: 'LandingShieldCommissioner',
    component: ShieldCommissioner,
  },
  {
    path: '/landing/payment-guaranteed-with-artconomy-shield/',
    name: 'LandingShieldArtist',
    component: ShieldArtist,
  },
  {
    path: '/landing/always-open-for-commissions/',
    name: 'LandingAlwaysOpen',
    component: AlwaysOpen,
  },
  {
    path: '/landing/artist-tools/',
    name: 'LandingArtistTools',
    component: ArtistTools,
  },
  {
    path: '/who-is-open/',
    name: 'WhoIsOpenRedirect',
    component: Redirect,
    props: {endpoint: '/search/products/'},
  },
  {
    path: '/recent-art/',
    name: 'RecentArtRedirect',
    component: Redirect,
    props: {endpoint: '/search/submissions/'},
  },
  {
    path: '*',
    name: 'NotFound',
    component: NotFound,
  },
]

// @ts-ignore
Router.prototype.push = saneNav(Router.prototype.push)
// @ts-ignore
Router.prototype.replace = saneNav(Router.prototype.replace)

export const router = new Router({
  mode: 'history',
  routes,
  scrollBehavior(to: Route, from: Route): void|{x: number, y: number} {
    if (!from || !to) {
      return
    }
    if ((from.name === to.name) || (from.matched[0].name === to.matched[0].name)) {
      // Need to find cases of different IDs or usernames and blep them out.
      if (paramsKey(from.params) === paramsKey(to.params)) {
        return
      }
    }
    return {x: 0, y: 0}
  },
})

declare global {
  interface Window {
    _paq: Array<any[]>
  }
}

window._paq = window._paq || []

export function configureHooks(vueRouter: Router, store: ArtStore): void {
  vueRouter.beforeEach((to, from, next) => {
    clearMetaTag('prerender-status-code')
    store.commit('errors/setError', {response: {status: 0}})
    if ((to.name + '').indexOf('iFrame') !== -1) {
      store.commit('setiFrame', true)
    }
    next()
  })
  vueRouter.beforeEach((to, from, next) => {
    if (from.name !== to.name) {
      document.title = 'Artconomy-- The easy and safe way to commission art!'
      setMetaContent(
        'description',
        'Artconomy helps you find artists to draw your OCs. Get a commission of your character today!',
      )
    }
    if (to.query.referred_by) {
      setCookie('referredBy', to.query.referred_by)
    }
    next()
  })
  vueRouter.afterEach((to, from) => {
    if (deepEqual(to, from)) {
      return
    }
    window._paq.push(['setCustomUrl', to.fullPath])
    window._paq.push(['setDocumentTitle', document.title])
    window._paq.push(['setReferrerUrl', from.fullPath])
    window._paq.push(['trackPageView'])
  })
}
