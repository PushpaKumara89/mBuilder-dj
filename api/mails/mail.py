from typing import List

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template


class File:
    def __init__(self, name, content, mimetype):
        self.name = name
        self.content = content
        self.mimetype = mimetype


class Mail:
    to = []
    from_email = ''
    from_name = None
    subject = ''
    template_name = ''
    context = {}
    reply_to = []
    files: List[File] = []

    def set_to(self, to):
        self.to = to if type(to) is list else [to]
        return self

    def set_subject(self, subject):
        self.subject = subject.replace('\n', '').replace('\r', '')
        return self

    def set_from_email(self, from_email):
        self.from_email = from_email
        return self

    def set_from_name(self, from_name):
        self.from_name = from_name
        return self

    def set_context(self, context):
        if self.context:
            self.context.update(context)
        else:
            self.context = context

        return self

    def set_reply_to(self, reply_to):
        self.reply_to = reply_to if type(reply_to) is list else [reply_to]
        return self

    def set_files(self, files):
        self.files = files if type(files) is list else [files]
        return self

    def send(self):
        body = get_template(self.template_name).render(self.context)
        from_name = self.from_name if self.from_name else settings.EMAIL_SUPPORT_NAME
        send_from = f'{from_name} <{self.from_email}>' if from_name else self.from_email
        subject = '[STG] ' + self.subject if settings.ENV == 'staging' else self.subject
        message = EmailMessage(subject, body, to=self.to, from_email=send_from, reply_to=self.reply_to)
        message.content_subtype = 'html'

        for file in self.files:
            message.attach(file.name, file.content, file.mimetype)

        return message.send()
