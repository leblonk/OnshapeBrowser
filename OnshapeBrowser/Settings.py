# Copyright (c) 2020.
# OnshapeBrowser plugin is released under the terms of the LGPLv3 or higher.
import json
import os


PLUGIN_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "plugin.json")


class Settings:

    # The plugin version
    with open(PLUGIN_JSON_PATH, "r") as file:
        VERSION = json.load(file).get("version", "0.0.0")

    # Plugin name displayed in several location.
    DISPLAY_NAME = "OnshapeBrowser"

    # OnshapeBrowser API options
    ONSHAPE_BROWSER_USER_NAME_PREFERENCES_KEY = "user_name"
    ONSHAPE_BROWSER_ON_COOKIE_KEY = "api_on_cookie"
    ONSHAPE_BROWSER_XSRF_COOKIE_KEY = "api_xsrf_cookie"

    ONSHAPE_LAST_DOCUMENT_NAME_KEY = "last_document_name"
    ONSHAPE_LAST_DOCUMENT_ID_KEY = "last_document_id"
    ONSHAPE_LAST_WORKSPACE_ID_KEY = "last_workspace_id"

    ONSHAPE_EXPORT_SCALE = "export_scale"
    ONSHAPE_EXPORT_UNITS = "export_units"
    ONSHAPE_EXPORT_ANGLE = "export_angle"
    ONSHAPE_EXPORT_CHORD = "export_chord"
    ONSHAPE_EXPORT_MAX_FACET = "export_max_facet"
    ONSHAPE_EXPORT_MIN_FACET = "export_min_facet"

    # Plugin settings preference keys
    PREFERENCE_KEY_BASE = "onshapebrowser"
    DEFAULT_API_CLIENT_PREFERENCES_KEY = "default_api_client"
