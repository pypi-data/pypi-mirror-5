from mock import Mock

from sprinter.testtools import create_mock_environment
from sprinter.formulas.command import CommandFormula

source_config = """
[update]
formula = sprinter.formulas.command
update = echo 'this is old...'

[remove]
formula = sprinter.formulas.command
remove = echo 'destroy up...'

[deactivate]
formula = sprinter.formulas.command
deactivate = echo 'deactivating...'

[activate]
formula = sprinter.formulas.command
activate = echo 'activating...'
"""

target_config = """
[install]
formula = sprinter.formulas.command
install = echo 'setting up...'
update = echo 'updating...'

[update]
formula = sprinter.formulas.command
update = echo 'update up...'
"""


class TestCommandFormula(object):
    """
    Tests for the command formula.
    """
    def setup(self):
        self.environment = create_mock_environment(
            source_config=source_config,
            target_config=target_config
        )
        self.environment.lib = Mock(spec=self.environment.lib)
        self.lib = self.environment.lib

    def teardown(self):
        del(self.environment)

    def test_install(self):
        self.environment.install_feature("install")
        self.lib.call.assert_called_once_with("echo 'setting up...'")

    def test_update(self):
        self.environment.update_feature("update")
        self.lib.call.assert_called_once_with("echo 'update up...'")

    def test_remove(self):
        self.environment.remove_feature("remove")
        self.lib.call.assert_called_once_with("echo 'destroy up...'")

    def test_deactivate(self):
        self.environment.deactivate_feature("deactivate")
        self.lib.call.assert_called_once_with("echo 'deactivating...'")

    def test_activate(self):
        self.environment.activate_feature("activate")
        self.lib.call.assert_called_once_with("echo 'activating...'")





