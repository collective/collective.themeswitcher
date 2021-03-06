import re
import logging
from zope import component
from zope import interface
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from plone.app.theming.utils import getAvailableThemes
from Products.CMFCore.utils import getToolByName
from plone.app.theming.interfaces import IThemeSettings

logger = logging.getLogger("collective.themeswitcher")
THEME_KEY = "themeswitcher"


class IThemeSwitcher(interface.Interface):
    """theme switcher"""

    def getDefaultSkin(original):
        """return the skin to use from portal_skins.
        original argument is the original getDefaultSkin method
        """

    def getSettings(original):
        """return settings for plone.app.theming (diazo)
        original argument is the original getSettings method
        """


class RegistryThemeSwitcher(BrowserView):
    """This is the global theme switcher used by default is take a switcher
    from the portal_registry"""
    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.portal_registry = None
        self.switcher = None

    def __call__(self):
        pass

    def update(self):
        if self.portal_registry is None:
            self.portal_registry = component.queryUtility(IRegistry)
        if self.switcher is None:
            name = u"themeswitcher_default"
            if self.portal_registry is not None:
                KEY = "collective.themeswitcher.switcher"
                name = self.portal_registry.get(KEY, name)
            context = (self.context, self.request)
            self.switcher = component.getMultiAdapter(context, name=name)
            logger.debug("switcher is now %s" % name)

    def getDefaultSkin(self, old):
        self.update()
        if self.switcher is None:
            logger.debug("no switcher")
            return old()
        return self.switcher.getDefaultSkin(old)

    def getSettings(self, old):
        self.update()
        if self.switcher is None:
            logger.debug("no switcher")
            return old()
        return self.switcher.getSettings(old)


class PloneThemeSwitcher(BrowserView):
    """The default theme manager"""

    def __call__(self):
        pass

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_registry = None
        self.theme = None  # the theme to switch to
        self.available_themes = None
        self.available_skins = None
        self.diazo_settings = None

    def update(self):
        if self.portal_registry is None:
            self.portal_registry = component.queryUtility(IRegistry)
        if self.available_themes is None:
            self.available_themes = [t.__name__ for t in getAvailableThemes()]
        if self.available_skins is None:
            portal_skins = getToolByName(self.context, 'portal_skins')
            self.available_skins = portal_skins.getSkinSelections()

    def getDefaultSkin(self, old):
        self.update()
        if self.theme is None:
            value = old()
            msg = "getDefaultSkin: no theme defined by the switcher -> %s "
            logger.debug(msg % value)
            return value
        if self.theme not in self.available_skins:
            value = old()
            msg = "theme not in available skins %s. -> %s"
            logger.debug(msg % (self.theme, value))
            return value
        logger.debug("getDefaultSkin -> %s" % self.theme)
        return self.theme

    def getSettings(self, old):
        self.update()
        if self.theme is None:
            logger.debug("no theme defined by the switcher")
            return old()
        if self.theme not in self.available_themes:
            logger.debug("theme not in available themes %s" % self.theme)
            return old()
        if self.diazo_settings is None:
            prefix = "collective.themeswitcher"
            forInterface = self.portal_registry.forInterface
            self.diazo_settings = forInterface(IThemeSettings,
                                               check=False,
                                               prefix=prefix)
        logger.debug("getSettings -> custom diazo settings %s" % self.theme)
        return self.diazo_settings


class MobileThemeSwitcher(PloneThemeSwitcher):

    #last update: 9 septembre 2013
    #to add tablet support add this to reg_b |android|ipad|playbook|silk
    #useless because tablets today are powerfull and used in wifi
    reg_b = re.compile(
        r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|"
        r"compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |"
        r"maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|"
        r"phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|"
        r"up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino",
        re.I | re.M
    )
    reg_v = re.compile(
        r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)"
        r"|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|a"
        r"ttw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w"
        r"|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp"
        r"|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-"
        r"d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly("
        r"\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit"
        r"|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|"
        r"s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig0"
        r"1|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |"
        r"\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-"
        r"[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-c"
        r"r|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt"
        r"(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1"
        r")|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran"
        r"|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|"
        r"pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2"
        r"-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|"
        r"ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-"
        r"|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(0"
        r"1|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|t"
        r"dg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up("
        r"\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|v"
        r"oda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi("
        r"g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-",
        re.I | re.M
    )

    def __init__(self, context, request):
        PloneThemeSwitcher.__init__(self, context, request)
        self._is_mobile = None

    def update(self):
        PloneThemeSwitcher.update(self)
        if self.theme is None and self.isMobile():
            KEY = "collective.themeswitcher.theme.mobile"
            self.theme = self.portal_registry.get(KEY, None)
            logger.debug('switch to %s' % self.theme)

    def isMobile(self):
        if self._is_mobile is None:
            user_agent = self.request.get('HTTP_USER_AGENT', None)
            if user_agent is not None:
                b = self.reg_b.search(user_agent)
                v = self.reg_v.search(user_agent[0:4])
                self._is_mobile = bool(b or v)
            else:
                self._is_mobile = False
        logger.debug("is mobile -> %s" % self._is_mobile)
        return self._is_mobile


class CookieThemeSwitcher(PloneThemeSwitcher):

    def __call__(self):
        self.update()
        self.request.response.redirect(self.context.absolute_url())

    def update(self):
        PloneThemeSwitcher.update(self)
        if self.theme is None:
            # note that themearg == themecookie if themecookie
            themearg = self.request.get(THEME_KEY, None)
            themecookie = self.request.cookies.get(THEME_KEY, None)
#            if themearg != themecookie:
#                logger.info('themearg=%s' % themearg)
#                logger.info('themecookie=%s' % themecookie)
            if themearg and themecookie and themearg == themecookie:
                self.theme = themecookie
            elif themearg and themecookie and themearg != themecookie:
                self.theme = themearg
                themecookie = themearg
                self.setCookie(themearg)
            elif themearg and not themecookie:
                self.setCookie(themearg)
                self.theme = themearg

    def setCookie(self, value):
        logger.debug("set the cookie to %s" % value)
        #change it for future call
        self.request.cookies[THEME_KEY] = value
        self.request.response.setCookie(THEME_KEY, value, path='/')


class MobileAndCookieThemeSwitcher(CookieThemeSwitcher, MobileThemeSwitcher):
    def update(self):
        CookieThemeSwitcher.update(self)
        MobileThemeSwitcher.update(self)
