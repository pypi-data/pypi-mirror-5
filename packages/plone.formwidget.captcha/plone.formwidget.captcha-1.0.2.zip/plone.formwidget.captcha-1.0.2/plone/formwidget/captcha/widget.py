import zope.component
import zope.interface
import zope.schema.interfaces

from Acquisition import aq_inner
from z3c.form import interfaces
from z3c.form import widget
from z3c.form import converter
from z3c.form.browser import text
from interfaces import ICaptchaWidget


class CaptchaWidget(text.TextWidget):
    maxlength = 7
    size = 8

    zope.interface.implementsOnly(ICaptchaWidget)

    def captchaImage(self):
        self.captcha = zope.component.getMultiAdapter((aq_inner(self.context), 
                                                       self.request), 
                                                       name='captcha')
        return self.captcha.image_tag()

    def captchaAudio(self):
        self.captcha = zope.component.getMultiAdapter((aq_inner(self.context), 
                                                       self.request), 
                                                       name='captcha')
        return self.captcha.audio_url()

def CaptchaFieldWidget(field, request):
    """IFieldWidget factory for CaptchaWidget."""
    return widget.FieldWidget(field, CaptchaWidget(request))
