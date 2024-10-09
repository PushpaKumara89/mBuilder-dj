def prepare_recipients(recipients):
    prepared_recipients = []
    for recipient in recipients:
        prepared_recipient = {
            'email': recipient.get('email')
        }

        if recipient.get('id'):
            prepared_recipient['id'] = recipient['id']

        if recipient.get('first_name'):
            prepared_recipient['first_name'] = recipient['first_name']

        if recipient.get('last_name'):
            prepared_recipient['last_name'] = recipient['last_name']

        if recipient.get('user'):
            prepared_recipient['user'] = recipient['user'].pk

        prepared_recipients.append(prepared_recipient)

    return prepared_recipients
