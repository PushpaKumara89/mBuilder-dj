from mbuild.settings.common import ENV


WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
    'enable-local-file-access': True
}

if ENV == 'testing':
    WKHTMLTOPDF_CMD_OPTIONS['no-images'] = True
