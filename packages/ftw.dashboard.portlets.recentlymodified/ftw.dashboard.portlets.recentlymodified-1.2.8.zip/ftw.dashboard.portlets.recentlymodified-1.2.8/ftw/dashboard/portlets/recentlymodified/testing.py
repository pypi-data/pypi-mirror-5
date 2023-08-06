from ftw.builder.testing import BUILDER_LAYER
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import setRoles, TEST_USER_ID, TEST_USER_NAME, login
from zope.configuration import xmlconfig


class FtwRecentlymodifiedLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import ftw.dashboard.portlets.recentlymodified

        xmlconfig.file(
            'configure.zcml', ftw.dashboard.portlets.recentlymodified,
            context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'ftw.dashboard.portlets.recentlymodified:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)


FTW_RECENTLYMODIFIED_FIXTURE = FtwRecentlymodifiedLayer()
FTW_RECENTLYMODIFIED_INTEGRATION_TESTING = IntegrationTesting(
    bases=(FTW_RECENTLYMODIFIED_FIXTURE, ),
    name="FtwRecentlymodified:Integration")
