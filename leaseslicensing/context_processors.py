from confy import env
from django.conf import settings
import json
import os
#from ledger.payments.helpers import is_payment_admin

from leaseslicensing.settings import (
        KMI_SERVER_URL, 
        template_group, 
        template_title,
        BUILD_TAG,
        )

vite_manifest = None
#import ipdb; ipdb.set_trace()
with open(os.path.join(settings.BASE_DIR, 'staticfiles_ll/leaseslicensing_vue/manifest.json'), mode='r', encoding='utf-8') as manifest_file:
    vite_manifest = json.loads(manifest_file.read())

vite_static_root = os.path.join('leaseslicensing_vue', 'assets')

print(vite_manifest)
#vite_vendor = str(os.path.join(vite_static_root, vite_manifest.get("src/main.js").get("imports")[0][1:]))
#vite_css = str(os.path.join(vite_static_root, vite_manifest.get("src/main.js").get("css")[0].replace('assets/','')))
#vite_file = str(os.path.join(vite_static_root, vite_manifest.get("src/main.js").get("file").replace('assets/','')))

#vite_vendor = str(os.path.join(vite_static_root, vite_manifest.get("index.html").get("imports")[0][1:]))
vite_css = str(os.path.join(vite_static_root, vite_manifest.get("index.html").get("css")[0].replace('assets/','')))
vite_file = str(os.path.join(vite_static_root, vite_manifest.get("index.html").get("file").replace('assets/','')))

#vite_vendor_tag = '{% static "' + vite_vendor + '" %}'
#vite_css_tag = '{% static "' + vite_css + '" %}'
#vite_file_tag = '{% static "' + vite_file + '" %}'
#
#print(vite_vendor_tag)
#print(vite_css_tag)
#print(vite_file_tag)

def leaseslicensing_url(request):
    #if settings.DOMAIN_DETECTED == 'apiary':
    #    PUBLIC_URL = 'https://apiary.dbca.wa.gov.au/'
    #    displayed_system_name = settings.APIARY_SYSTEM_NAME
    #    support_email = settings.APIARY_SUPPORT_EMAIL
    #else:
    #    PUBLIC_URL = 'https://das.dbca.wa.gov.au'
    #    displayed_system_name = settings.SYSTEM_NAME
    #    support_email = settings.SUPPORT_EMAIL

    #is_payment_officer = is_payment_admin(request.user)

    return {
        #'DOMAIN_DETECTED': settings.DOMAIN_DETECTED,
        #'DEBUG': settings.DEBUG,
        #'DEV_STATIC': settings.DEV_STATIC,
        #'DEV_STATIC_URL': settings.DEV_STATIC_URL,
        #'TEMPLATE_GROUP': settings.DOMAIN_DETECTED,
        #'SYSTEM_NAME': settings.SYSTEM_NAME,
        #'PUBLIC_URL': PUBLIC_URL,
        #'APPLICATION_GROUP': settings.DOMAIN_DETECTED,
        #'DISPLAYED_SYSTEM_NAME': displayed_system_name,
        #'SUPPORT_EMAIL': support_email,
        #'is_payment_admin': is_payment_officer,
        #'build_tag': settings.BUILD_TAG,
        'KMI_SERVER_URL': KMI_SERVER_URL,
        'template_group': template_group,
        'template_title': template_title,
        'build_tag': BUILD_TAG,
        #'vite_vendor': vite_vendor,
        'vite_css': vite_css,
        'vite_file': vite_file,
    }
