from django.conf import settings

# The URL that users get sent back to after visiting spreedly
SPREEDLY_RETURN_URL = getattr(settings, 'SPREEDLY_RETURN_URL', '/thanks/')

# The base URL for all spreedly related pages
SPREEDLY_URL = getattr(settings, 'SPREEDLY_URL', '/subscriptions/')

# lock out your entire site (except for spreedly URLs and the paths below) to non-subscribed users?
SPREEDLY_USERS_ONLY = getattr(settings, 'SPREEDLY_USERS_ONLY', False)

# Paths that a user can visit without a subscription 
SPREEDLY_ALLOWED_PATHS = getattr(settings, 'SPREEDLY_ALLOWED_PATHS', [])

# Should anonymous users be sent to the login screen or the subscription screen?
SPREEDLY_ANONYMOUS_SHOULD_LOGIN = getattr(settings, 'SPREEDLY_ANONYMOUS_SHOULD_LOGIN', True)

# the template to use for the confirmation email
SPREEDLY_CONFIRM_EMAIL = getattr(settings, 'SPREEDLY_CONFIRM_EMAIL', 'confirm_email.txt')

# the subject for the confirmation email
# No db calls in setting - this is removed

# the template to use for the confirmation email
SPREEDLY_GIFT_EMAIL = getattr(settings, 'SPREEDLY_GIFT_EMAIL', 'gift_email.txt')

# the subject for the confirmation email

# This template will be used after a user has signed up on your site and a confirm email has been sent to them
SPREEDLY_EMAIL_SENT_TEMPLATE = getattr(settings, 'SPREEDLY_EMAIL_SENT_TEMPLATE', 'email_sent.html')

# the url that will be used to return users from spreedly to your site.
# No db calls in setting - this is removed

SPREEDLY_GIFT_REGISTER_TEMPLATE = getattr(settings, 'SPREEDLY_GIFT_REGISTER_TEMPLATE', 'log_in.html')
SPREEDLY_ADMIN_GIFT_TEMPLATE = getattr(settings, 'SPREEDLY_ADMIN_GIFT_TEMPLATE', 'admin_gift.html')

SPREEDLY_SAVE_ON_FAIL = getattr(settings, 'SPREEDLY_SAVE_ON_FAIL', False)
