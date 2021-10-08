# -*- coding: utf-8 -*-

import os
from .helper import HOME
from .env_helper import append_line_if_not_exists, load_var_value_from_shell_script


class EnvSecret(object):
    """
    Allow to load secret information from environment variable.
    """
    pysecret_file = ".bashrc_pysecret"
    pysecret_script = os.path.join(HOME, pysecret_file)

    bashrc_script = os.path.join(HOME, ".bashrc")
    bash_profile_script = os.path.join(HOME, ".bash_profile")
    zshrc_script = os.path.join(HOME, ".zshrc")
    config_fish_script = os.path.join(HOME, ".config", "fish", "config.fish")

    def export_cmd_text(self, var, value):
        """
        create ``export VAR="VALUE"`` command text
        """
        return 'export {var}="{value}"'.format(var=var, value=value)

    def set(self, var, value, temp=False):
        """
        Set value.

        :type var: str
        :param var:

        :type value: str
        :param value:

        :type temp: bool
        :param temp: if True, then will not write ``export var="value"`` to pysecret file.

        :return: None
        """
        os.environ[var] = str(value)
        if temp is False:
            append_line_if_not_exists(
                self.pysecret_script, self.export_cmd_text(var, value))

    @property
    def environ(self):
        return os.environ

    def get(self, var):
        """
        Get value.

        :type var: str
        :param var:

        :rtype: str
        :return:
        """
        return self.environ[var]

    def unset(self, var):  # pragma: no cover
        raise NotImplementedError("not implemented yet!")

    # -- add ``source ~/<pysecret_file>`` to bash profile file
    @property
    def source_pysecret_command(self):
        return "source ~/{}".format(self.pysecret_file)

    def apply_source_pysecret_to_bashrc(self):  # pragma: no cover
        append_line_if_not_exists(
            self.bashrc_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_bash_profile(self):  # pragma: no cover
        append_line_if_not_exists(
            self.bash_profile_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_zshrc(self):  # pragma: no cover
        append_line_if_not_exists(
            self.zshrc_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_config_fish(self):  # pragma: no cover
        append_line_if_not_exists(
            self.config_fish_script, self.source_pysecret_command
        )

    def load_pysecret_script(self):
        environ = load_var_value_from_shell_script(self.pysecret_script)
        for key, value in environ.items():
            os.environ[key] = value
