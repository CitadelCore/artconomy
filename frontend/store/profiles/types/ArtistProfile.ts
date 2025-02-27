import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'

export interface ArtistProfile {
  dwolla_configured: boolean,
  commissions_closed: boolean,
  max_load: number,
  public_queue: boolean,
  has_products: boolean,
  commission_info: string,
  auto_withdraw: boolean,
  escrow_disabled: boolean,
  lgbt: boolean,
  artist_of_color: boolean,
  bank_account_status: BANK_STATUSES,
}
