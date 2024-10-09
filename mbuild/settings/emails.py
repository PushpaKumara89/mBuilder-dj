from mbuild.settings.common import env


EMAIL_BACKEND = env.str('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

EMAIL_HOST = env.str('EMAIL_HOST', 'smtp.mailtrap.io')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', '')
EMAIL_PORT = env.int('EMAIL_PORT', 2525)

EMAIL_SUPPORT_EMAIL = env.str('EMAIL_SUPPORT_EMAIL', 'some_email@email.com')
EMAIL_SUPPORT_NAME = env.str('EMAIL_SUPPORT_NAME', 'MBuild Support')
EMAIL_COMPLETIONS_EMAIL = env.str('EMAIL_COMPLETIONS_EMAIL', 'some_completions_email@email.com')

GLOBAL_ADMIN_EMAIL_NAME = env.str('GLOBAL_ADMIN_EMAIL_NAME', 'MBuild Admin')
GLOBAL_ADMIN_EMAIL = env.str('GLOBAL_ADMIN_EMAIL', 'admin@mbuild.global')
