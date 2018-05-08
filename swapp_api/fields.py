import logging
from django.db.models import ImageField
from easy_thumbnails.fields import ThumbnailerImageField
from swapp_api.utils import resize_image, optimize_image


logger = logging.getLogger(__name__)


class AutoResizeImageField(ThumbnailerImageField):
    """
    This class subclasses the djang.db.modelsImageField and uses
    imagemagick to downsize images using the convert command and not
    providing the excalamatory mark (!) to maintain aspect ratio of
    image when resizing. This results in image having resized when
    it exceeds the provided width or height limit.
    """

    def __init__(self, verbose_name=None, name=None, width_field=None,
            height_field=None, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        super(AutoResizeImageField, self).__init__(verbose_name, \
                                                    name, \
                                                    width_field, \
                                                    height_field, \
                                                    **kwargs)
    def pre_save(self, model_instance, add):
        "Returns field's value just before saving."
        file = super(AutoResizeImageField, self).pre_save(model_instance, add)

        if file:
            # resize
            if self.max_width or self.max_height:
                width = self.max_width or self.max_height
                height = self.max_height or self.max_width
                try:
                    if file.width > self.max_width or file.height > self.max_height:
                        resize_image(file.path, width, height)
                except Exception as e:
                    error = str(e)
                    logger.error(error)

            # optimize
            optimize_image(file.path)

        return file

    def south_field_triple(self):
        "Returns a suitable description of this field for South."
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = self.__class__.__module__ + "." + self.__class__.__name__
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)