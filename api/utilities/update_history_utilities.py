from itertools import chain

from django.db.models import Q

from api.models import User, Recipient


def add_extra_recipients(recipients, project_pk):
    extra_recipients = User.objects.filter(
        Q(groups__in=[User.Group.COMPANY_ADMIN.value]) |
        Q(projectuser__is_notifications_enabled=True, projectuser__project=project_pk)
    ).all()

    for extra_recipient in extra_recipients:
        if extra_recipient.email not in recipients:
            recipients.append(extra_recipient.email)


def sync_recipients(update_entity, recipients):
    from api.http.serializers import RecipientSerializer

    existing_recipients_pks = [
        existing_recipient['id'] for existing_recipient in [
            recipient for recipient in recipients if recipient.get('id') is not None
        ]
    ]
    existing_recipients = Recipient.objects.filter(pk__in=existing_recipients_pks).all()

    non_existing_recipients_by_pk = [recipient for recipient in recipients if recipient.get('id') is None]
    non_existing_recipients_by_pk_emails = [
        non_existing_recipient.get('email') for non_existing_recipient in non_existing_recipients_by_pk
    ]

    existing_recipients_by_email = []
    existing_recipients_by_email_emails = []
    if len(non_existing_recipients_by_pk_emails) > 0:
        existing_recipients_by_email = Recipient.objects.filter(
            email__in=non_existing_recipients_by_pk_emails
        ).all()

        existing_recipients_by_email_emails = [
            non_existing_recipient.email for non_existing_recipient in existing_recipients_by_email
        ]

    non_existing_recipients = [
        recipient for recipient in recipients if
        recipient.get('id') not in existing_recipients_pks and
        recipient.get('email') not in existing_recipients_by_email_emails
    ]

    for recipient in non_existing_recipients:
        if 'user' in non_existing_recipients:
            recipient['user'] = recipient['user'].pk \
                if isinstance(recipient['user'], User) \
                else recipient['user']

    recipients_serializer = RecipientSerializer(data=non_existing_recipients, many=True)
    recipients_serializer.is_valid(raise_exception=True)
    new_recipients = RecipientSerializer(many=True).create(recipients_serializer.validated_data)

    update_entity.recipients.set(chain(existing_recipients, existing_recipients_by_email, new_recipients))
