from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField,
)

DEFAULT_VALUES = {}


class PresetModel(BaseSettingsModel):
    enabled: bool = SettingsField(True, title="Enabled")
    name: str = SettingsField("", title="Name")
    command: str = SettingsField("", title="Command", widget="textarea")


class TopazSettings(BaseSettingsModel):
    presets: list[PresetModel] = SettingsField(
        default_factory=list,
        title="Presets",
    )
