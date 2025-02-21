from typing import Type
from ayon_server.actions import (
    ActionExecutor,
    ExecuteResponseModel,
    SimpleActionManifest,
)

from ayon_server.addons import BaseServerAddon

from .settings import TopazSettings, DEFAULT_VALUES

from nxtools import logging

IDENTIFIER_PREFIX = "topaz.launch"


class TopazAddon(BaseServerAddon):
    # Settings
    settings_model: Type[TopazSettings] = TopazSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_VALUES)

    # Webactions
    async def get_simple_actions(
        self,
        project_name: str | None = None,
        variant: str = "production",
    ) -> list[SimpleActionManifest]:
        """Return a list of simple actions provided by the addon"""
        output = []

        # Add a web actions to folders.
        icon = {
            "type": "material-symbols",
            "name": "switch_access_2",
        }

        # logging.info(self.get_project_settings(project_name, variant))
        project_settings = await self.get_project_settings(
            project_name, variant
        )
        for preset in project_settings.presets:
            logging.info(preset.dict())
            preset = preset.dict()
            name = preset.get("name")
            output.append(
                SimpleActionManifest(
                    identifier=f"{IDENTIFIER_PREFIX}.upscale_{name}",
                    label=name,
                    icon=icon,
                    order=100,
                    entity_type="folder",
                    entity_subtypes=None,
                    allow_multiselection=False,
                )
            )

        # output.append(
        #     SimpleActionManifest(
        #         identifier=f"{IDENTIFIER_PREFIX}.upscale_4k",
        #         label="Topaz: 4k Upscale",
        #         icon=icon,
        #         order=100,
        #         entity_type="version",
        #         entity_subtypes=None,
        #         allow_multiselection=False,
        #     )
        # )
        # output.append(
        #     SimpleActionManifest(
        #         identifier=f"{IDENTIFIER_PREFIX}.upscale_1080p",
        #         label="Topaz: 1080p Upscale",
        #         icon=icon,
        #         order=100,
        #         entity_type="version",
        #         entity_subtypes=None,
        #         allow_multiselection=False,
        #     )
        # )

        return output

    async def execute_action(
        self,
        executor: "ActionExecutor",
    ) -> "ExecuteResponseModel":
        """Execute an action provided by the addon.

        Note:
            Executes CLI actions defined in the addon's client code or other addons.

        """

        project_name = executor.context.project_name
        entity_id = executor.context.entity_ids[0]

        import re

        if re.search("upscale", executor.identifier):
            return await executor.get_launcher_action_response(
                args=[
                    "addon",
                    "topaz",
                    "upscale-4k",
                    "--project",
                    project_name,
                    "--entity-id",
                    entity_id,
                ]
            )

        raise ValueError(f"Unknown action: {executor.identifier}")
