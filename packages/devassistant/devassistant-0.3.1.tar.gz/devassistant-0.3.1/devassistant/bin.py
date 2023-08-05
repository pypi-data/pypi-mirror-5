from devassistant import assistant_base
from devassistant import cli
from devassistant import yaml_assistant_loader

class ExecutableAssistant(assistant_base.AssistantBase):
    @classmethod
    def main(cls):
        cli.CliRunner.run_assistant(cls())

class CreatorAssistant(ExecutableAssistant):
    def get_subassistants(self):
        sa = yaml_assistant_loader.YamlAssistantLoader.get_top_level_assistants(roles=['creator'])
        return sa

    name = 'main'
    verbose_name = 'Main'
    description = 'Developer assistant will help you with creating projects in many different languages.\
                   See subassistants for list of currently available assistants.'

class ModifierAssistant(ExecutableAssistant):
    def get_subassistants(self):
        sa = yaml_assistant_loader.YamlAssistantLoader.get_top_level_assistants(roles=['modifier'])
        return sa

    name = 'main'
    verbose_name = 'Main'
    description = 'Developer assistant will help you work with existing projects.\
                   See subassistants for list of currently available assistants.'
