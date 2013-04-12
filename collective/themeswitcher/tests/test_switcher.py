import unittest2 as unittest
from collective.themeswitcher.tests import base, fake
from collective.themeswitcher.switcher import RegistryThemeSwitcher,\
    PloneThemeSwitcher, MobileThemeSwitcher


class UnitTestRegistryThemeSwitcher(base.UnitTestCase):
    def setUp(self):
        super(UnitTestRegistryThemeSwitcher, self).setUp()
        self.switcher = RegistryThemeSwitcher(self.portal, self.request)
        self.switcher.portal_registry = fake.FakeRegistry()
        self.switcher.switcher = fake.FakeSwitcher()

    def test_getDefaultSkin(self):

        default_skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(default_skin, 'defaultskin')

        self.switcher.switcher.useOld = True
        default_skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(default_skin, 'old default skin')

    def test_getSettings(self):

        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'settings')

        self.switcher.switcher.useOld = True
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')


class IntegrationTestRegistryThemeSwitcher(base.IntegrationTestCase):
    def setUp(self):
        super(IntegrationTestRegistryThemeSwitcher, self).setUp()
        self.switcher = RegistryThemeSwitcher(self.portal, self.request)

    def test_update(self):
        self.assertIsNone(self.switcher.portal_registry)
        self.assertIsNone(self.switcher.switcher)
        self.switcher.update()
        self.assertIsNotNone(self.switcher.portal_registry)
        self.assertIsNotNone(self.switcher.switcher)

    def test_getDefaultSkin(self):
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'old default skin')

        #try throw the monkey patch
        self.assertEqual(self.portal.portal_skins.getDefaultSkin(),
                         'Sunburst Theme')

    def test_getSettings(self):
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')

        #TODO but don't know how: try throw the monkey patch


class UnitTestPloneThemeSwitcher(base.UnitTestCase):

    def setUp(self):
        super(UnitTestPloneThemeSwitcher, self).setUp()
        self.switcher = PloneThemeSwitcher(self.portal, self.request)
        self.switcher.portal_registry = fake.FakeRegistry()
        self.switcher.available_skins = ['Sunburst Theme', 'Plone Classic Theme']
        self.switcher.available_themes = ['plonetheme.mobile']

    def test_getDefaultSkin(self):
        #self.switcher.theme = None
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'old default skin')

        self.switcher.theme = 'not existing theme'
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'old default skin')

        self.switcher.theme = 'Plone Classic Theme'
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'Plone Classic Theme')

    def test_getSettings(self):
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')

        self.switcher.theme = 'not existing'
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')

        self.switcher.theme = 'plonetheme.mobile'
        self.switcher.diazo_settings = 'fake diazo settings'
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'fake diazo settings')


class IntegrationTestPloneThemeSwitcher(base.IntegrationTestCase):
    def setUp(self):
        super(IntegrationTestPloneThemeSwitcher, self).setUp()
        self.switcher = PloneThemeSwitcher(self.portal, self.request)

    def test_update(self):
        self.assertIsNone(self.switcher.portal_registry)
        self.assertIsNone(self.switcher.available_themes)
        self.assertIsNone(self.switcher.available_skins)
        self.switcher.update()
        self.assertIsNotNone(self.switcher.portal_registry)
        self.assertIsNotNone(self.switcher.available_themes)
        self.assertIsNotNone(self.switcher.available_skins)
        self.assertIn('Plone Default', self.switcher.available_skins)
        self.assertIn('Sunburst Theme', self.switcher.available_skins)

    def test_getDefaultSkin(self):
        #self.switcher.theme = None
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'old default skin')

        self.switcher.theme = 'not existing theme'
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'old default skin')

        self.switcher.theme = 'Plone Default'
        skin = self.switcher.getDefaultSkin(self._old_getDefaultSkin)
        self.assertEqual(skin, 'Plone Default')

    def test_getSettings(self):
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')

        self.switcher.theme = 'not existing'
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings, 'old settings')

        self.switcher.theme = 'example'
        #setup the settings and check the reuslts
        self.portal.portal_registry['collective.themeswitcher.currentTheme'] = u'example'
        self.portal.portal_registry['collective.themeswitcher.enabled'] = True
        settings = self.switcher.getSettings(self._old_settings)
        self.assertEqual(settings.currentTheme, 'example')
        attrs = ('rules', 'absolutePrefix',
                 'currentTheme', 'doctype', 'enabled', 'readNetwork',
                 'parameterExpressions', 'hostnameBlacklist')
        for attr in attrs:
            self.assertTrue(hasattr(settings, attr))


class UnitTestMobileThemeSwitcher(base.UnitTestCase):

    def setUp(self):
        super(UnitTestMobileThemeSwitcher, self).setUp()
        self.switcher = MobileThemeSwitcher(self.portal, self.request)

    def test_update(self):
        self.assertIsNone(self.switcher._is_mobile)
        self.switcher.portal_registry = fake.FakeRegistry()
        self.switcher.available_skins = ['Sunburst Theme', 'Plone Classic Theme']
        self.switcher.available_themes = ['plonetheme.mobile']
        self.switcher.portal_registry.registry["collective.themeswitcher.theme.mobile"] = "plonetheme.mobile"
        self.switcher.update()
        self.assertNotEqual(self.switcher.theme, "plonetheme.mobile")
        #reset cache
        self.switcher._is_mobile = None
        self.request["HTTP_USER_AGENT"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3"
        self.switcher.update()
        self.assertEqual(self.switcher.theme, "plonetheme.mobile")

    def test_isMobile(self):
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
