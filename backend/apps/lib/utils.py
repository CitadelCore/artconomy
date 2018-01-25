from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import Q
from django.db.transaction import atomic
from django.utils import timezone
from pycountry import countries, subdivisions

from apps.lib.models import Subscription, Event, Notification


def countries_tweaked():
    """
    Tweaked listing of countries.
    """
    us = countries.get(alpha_2='US')
    yield (us.alpha_2, us.name)
    for a in countries:
        if a.alpha_2 == 'TW':
            yield (a.alpha_2, "Taiwan")
        elif a.alpha_2 in settings.COUNTRIES_NOT_SERVED:
            continue
        elif a.alpha_2 != 'US':
            yield (a.alpha_2, a.name)


def country_choices():
    return [country_choice for country_choice in countries_tweaked()]


# Force pycountry to fetch data.
subdivisions.get(country_code='US')

subdivision_map = {
    country.alpha_2:
        {subdivision.code[3:]: subdivision.name for subdivision in subdivisions.get(country_code=country.alpha_2)}
        if country.alpha_2 in subdivisions.indices['country_code']
        else {}
    for country in countries
}

country_map = {country.name.lower(): country for country in countries}

for code, name in ('AE', 'AA', 'AP'):
    subdivision_map['US'][code] = code


def recall_notification(event_type, target, data=None, unique_data=False):
    content_type = target and ContentType.objects.get_for_model(target)
    object_id = target and target.id
    events = get_matching_events(event_type, content_type, object_id, data, unique_data)
    events.update(recalled=True)


def update_event(event, data, subscriptions, mark_unread, time_override=None, transform=None):
    event.recalled = False
    if mark_unread or time_override:
        event.date = time_override or timezone.now()
    if transform:
        data = transform(event.data, data)
    event.data = data
    event.save()
    if mark_unread:
        subscribers = subscriptions.values_list('subscriber_id', flat=True)
        Notification.objects.filter(user__in=subscribers, event=event).update(read=False)


def target_params(object_id, content_type):
    query = Q(object_id__isnull=True, content_type__isnull=True)
    if content_type:
        query |= Q(object_id=object_id, content_type=content_type)
    return query


def get_matching_subscriptions(event_type, object_id, content_type):
    return Subscription.objects.filter(
        Q(type=event_type, removed=False) & target_params(object_id, content_type)
    )


def get_matching_events(event_type, content_type, object_id, data, unique_data=None):
    query = Q(type=event_type)
    query &= target_params(object_id, content_type)
    if unique_data:
        if unique_data is True:
            query &= Q(data=data)
        else:
            kwargs = {'data__' + key: value for key, value in unique_data.items()}
            query &= Q(**kwargs)
    return Event.objects.filter(query)


@atomic
def notify(
        event_type, target, data=None, unique=False, unique_data=None, mark_unread=False, time_override=None,
        transform=None
):
    if data is None:
        data = {}
    content_type = target and ContentType.objects.get_for_model(target)
    object_id = target and target.id
    subscriptions = get_matching_subscriptions(event_type, object_id, content_type)
    if not subscriptions.exists():
        return
    if unique or unique_data:
        events = get_matching_events(event_type, content_type, object_id, data, unique_data)
        if events.exists():
            update_event(
                events[0], data, subscriptions,
                mark_unread=mark_unread,
                time_override=time_override,
                transform=transform
            )
            return
    event = Event.objects.create(
        type=event_type, object_id=target and target.id, content_type=content_type, data=data
    )
    Notification.objects.bulk_create(
        (
            Notification(
                event_id=event.id, user_id=subscriber_id
            )
            for subscriber_id in subscriptions.values_list('subscriber_id', flat=True)
        ),
        batch_size=1000
    )


def add_check(instance, field_name, *args):
    args_length = len(args)
    max_length = getattr(instance, field_name + '__max')
    current_length = getattr(instance, field_name).all().count()
    proposed = args_length + current_length
    if proposed > max_length:
        raise ValidationError(
            'This would exceed the maximum number of entries for this relation. {} > {}'.format(proposed, max_length)
        )


def safe_add(instance, field_name, *args):
    add_check(instance, field_name, *args)
    getattr(instance, field_name).add(*args)


def ensure_tags(tag_list):
    if not tag_list:
        return
    with connection.cursor() as cursor:
        # Bulk get or create
        # Django's query prepper automatically wraps our arrays in parens, but we need to have them
        # act as individual values, so we have to custom build our placeholders here.
        statement = """
                    INSERT INTO lib_tag (name)
                    (
                             SELECT i.name
                             FROM (VALUES {}) AS i(name)
                             LEFT JOIN lib_tag as existing
                                     ON (existing.name = i.name)
                             WHERE existing.name IS NULL
                    )
                    """.format(('%s, ' * len(tag_list)).rsplit(',', 1)[0])
        cursor.execute(statement, [*tuple((tag,) for tag in tag_list)])