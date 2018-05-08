import subprocess

from os.path import splitext

from push_notifications.apns import (
    APNSDataOverflow,
    APNSError,
    APNSServerError
)
from push_notifications.models import APNSDevice


def resize_image(image_path, width, height):
    cmd = "mogrify %s -resize %sx%s %s" % (image_path, width, height, image_path)

    subprocess.Popen(cmd, shell=True)

def optimize_image(path):
    run_string = {
        ".jpeg": u"jpegoptim -f --strip-all '%(file)s'",
        ".jpg": u"jpegoptim -f --strip-all '%(file)s'",
        ".png": u"optipng -force -o7 '%(file)s' && advpng -z4 '%(file)s' \
                && pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP \
                -rem sRGB -rem time '%(file)s' '%(file)s.bak' && mv '%(file)s.bak' '%(file)s'"
    }

    ext = splitext(path)[1].lower()

    if ext in run_string:
        cmd = run_string[ext] % {'file': path}

        subprocess.Popen(cmd, shell=True)

def send_push_notification(user, notification, type, obj_id, badge_count=0):
    """
    Utility function to send Push Notifications to the APNS using the
    `django-push-notifications` package.
    """

    try:
        device = APNSDevice.objects.get(user=user)
        notif_type_id_key = "thread_id" if type == "message" else "notification_id"

        try:
            # Badge if notification is about an offer
            if type == "notification":
                device.send_message(notification,
                                    badge=badge_count,
                                    extra={"type": type, notif_type_id_key: obj_id})
            else:
                device.send_message(notification, extra={"type": type, notif_type_id_key: obj_id})
        except (APNSDataOverflow, APNSError, APNSServerError):
            pass
    except APNSDevice.DoesNotExist:
        pass
