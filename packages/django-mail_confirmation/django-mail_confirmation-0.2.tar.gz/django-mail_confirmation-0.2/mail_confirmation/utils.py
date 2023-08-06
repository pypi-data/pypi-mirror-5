from .models import MailConfirmation
from django.core.mail import send_mail

from django.utils.translation import ugettext as _
from django.template.loader import render_to_string
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def generate_confirmation(toconfirm, 
                          success_template='', 
                          success_url=''):
    """
    Generates a confirmation email object
    """
    try:
        confirm = MailConfirmation(toconfirm_object=toconfirm,
                                   confirm_success_url=success_url, 
                                   confirm_success_template=success_template)
        
        confirm.save()
        return confirm
    except Exception, e:
        logger.error('Could not generate confirmation for mail_confirmation: '+str(e))
        return False


def send_confirmation(confirm, template=None,
                      subject=_('Confirmation mail'),
                      sender=None,
                      to=[],
                      confirmurlname='mail_confirmation:url'):
    """
    Send a confirmation mail 
    """

    if sender is None:
        sender = settings.DEFAULT_FROM_EMAIL
    try:
        from django.contrib.sites.models import Site
        domain = Site.objects.get_current().domain
    except: 
        domain = settings.SITE_URL or ""

    url = reverse(confirmurlname, 
                  kwargs={'confirmationid':confirm.confirmationid})
    template = template or confirm.toconfirm_object._meta.app_label+'/mail_request.html'
    message = render_to_string(template, {'url': url,
                                          'SITE_URL': domain})
    return send_mail(subject, message, sender,
              to, fail_silently=False)


def generate_and_send(toconfirm,
                      template,    
                      success_template='', success_url='',
                      *args,
                      **kwargs):
    """
    Do both actions above 
    """
    confirm = generate_confirmation(toconfirm, success_template, success_url)
    if confirm:
        return send_confirmation(confirm, template, *args, **kwargs)
    return confirm


def clear_stale():
    """
    Clears stale requests not confirmed
    """
    last_month = datetime.today() - timedelta(days=30)
    MailConfirmation.objects.filter(date_created__lte=last_month).delete()
