from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class WasgehtenginecontenttypesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import wasgehtengine.contenttypes
        xmlconfig.file(
            'configure.zcml',
            wasgehtengine.contenttypes,
            context=configurationContext
        )

        # Install products that use an old-style initialize() function
        #z2.installProduct(app, 'Products.PloneFormGen')

#    def tearDownZope(self, app):
#        # Uninstall products installed above
#        z2.uninstallProduct(app, 'Products.PloneFormGen')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'wasgehtengine.contenttypes:default')

WASGEHTENGINE_CONTENTTYPES_FIXTURE = WasgehtenginecontenttypesLayer()
WASGEHTENGINE_CONTENTTYPES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(WASGEHTENGINE_CONTENTTYPES_FIXTURE,),
    name="WasgehtenginecontenttypesLayer:Integration"
)
