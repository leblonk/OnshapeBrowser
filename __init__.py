def getMetaData():
    """
    Function called when Cura want to know the metadata for a plugin to populate the Marketplace interface.
    :return: A dict containing relevant meta data. Plugin.json data is always appended automatically.
    """
    return {}


def register(*_args, **_kwargs):
    """
    Main function called when Cura boots and want to load the plugin.
    :return: A dict containing the extension instance.
    """
    from .OnshapeBrowser.OnshapeBrowserExtension import OnshapeBrowserExtension
    return {
        "extension": OnshapeBrowserExtension()
    }
