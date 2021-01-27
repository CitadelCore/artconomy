import {Ratings} from './Ratings'

export interface User {
  portrait_paid_through: string | null,
  landscape_paid_through: string | null,
  telegram_link: string,
  watching: boolean,
  blocked: boolean,
  rating: Ratings,
  sfw_mode: boolean,
  username: string,
  id: number,
  guest: boolean,
  is_staff: boolean,
  is_superuser: boolean,
  avatar_url: string,
  email: string,
  guest_email: string,
  favorites_hidden: boolean,
  blacklist: string[],
  biography: string,
  taggable: boolean
  stars: number | null,
  rating_count: number,
  portrait: boolean,
  portrait_enabled: boolean,
  landscape: boolean,
  landscape_enabled: boolean,
  offered_mailchimp: boolean,
  artist_mode: boolean,
  hits: number,
  watches: number,
  birthday: string|null,
}
