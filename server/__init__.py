from ayon_server.actions import (
    ActionExecutor,
    ExecuteResponseModel,
    SimpleActionManifest,
)

from ayon_server.addons import BaseServerAddon


IDENTIFIER_PREFIX = "topaz.launch"


class MyAddonSettings(BaseServerAddon):
    # Set settings
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

        output.append(
            SimpleActionManifest(
                identifier=f"{IDENTIFIER_PREFIX}.show_dialog",
                label="Simple Action",
                icon=icon,
                order=100,
                entity_type="folder",
                entity_subtypes=None,
                allow_multiselection=False,
            )
        )
        output.append(
            SimpleActionManifest(
                identifier=f"{IDENTIFIER_PREFIX}.upscale_4k",
                label="Topaz: 4k Upscale",
                icon=icon,
                order=100,
                entity_type="version",
                entity_subtypes=None,
                allow_multiselection=False,
            )
        )
        output.append(
            SimpleActionManifest(
                identifier=f"{IDENTIFIER_PREFIX}.upscale_1080p",
                label="Topaz: 1080p Upscale",
                icon=icon,
                order=100,
                entity_type="version",
                entity_subtypes=None,
                allow_multiselection=False,
            )
        )

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

        if executor.identifier == f"{IDENTIFIER_PREFIX}.show_dialog":
            return await executor.get_launcher_action_response(
                args=[
                    "addon",
                    "topaz",
                    "show-selected-path",
                    "--project",
                    project_name,
                    "--entity-id",
                    entity_id,
                ]
            )

        elif executor.identifier == f"{IDENTIFIER_PREFIX}.upscale_4k":
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

        elif executor.identifier == f"{IDENTIFIER_PREFIX}.upscale_1080p":
            return await executor.get_launcher_action_response(
                args=[
                    "addon",
                    "topaz",
                    "upscale-1080p",
                    "--project",
                    project_name,
                    "--entity-id",
                    entity_id,
                ]
            )

        raise ValueError(f"Unknown action: {executor.identifier}")
