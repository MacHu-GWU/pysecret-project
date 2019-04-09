# -*- coding: utf-8 -*-

import os
from .helper import HOME, append_line_if_not_exists, set_env_var


class Env(object):
    """
    """

    pysecret_file = ".bashrc_pysecret"
    pysecret_script = os.path.join(HOME, pysecret_file)

    bashrc_script = os.path.join(HOME, ".bashrc")
    bash_profile_script = os.path.join(HOME, ".bash_profile")
    zshrc_script = os.path.join(HOME, ".zshrc")
    config_fish_script = os.path.join(HOME, ".config", "fish", "config.fish")

    def export_cmd_text(self, var, value):
        """create ``export VAR="VALUE"`` command text"""
        return 'export {var}="{value}"'.format(var=var, value=value)

    def set(self, var, value, temp=False):
        set_env_var(var, value)
        if temp is False:
            append_line_if_not_exists(
                self.pysecret_script, self.export_cmd_text(var, value))

    def get(self, var):
        return os.environ[var]

    #-- add ``source ~/<pysecret_file>`` to bash profile file
    @property
    def source_pysecret_command(self):
        return "source ~/{}".format(self.pysecret_file)

    def apply_source_pysecret_to_bashrc(self):
        append_line_if_not_exists(
            self.bashrc_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_bash_profile(self):
        append_line_if_not_exists(
            self.bash_profile_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_zshrc(self):
        append_line_if_not_exists(
            self.zshrc_script, self.source_pysecret_command
        )

    def apply_source_pysecret_to_config_fish(self):
        append_line_if_not_exists(
            self.config_fish_script, self.source_pysecret_command
        )
