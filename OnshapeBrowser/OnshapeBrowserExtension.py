import os
from typing import cast, Optional, Callable, Any

from PyQt6.QtCore import QObject
from PyQt6.QtQuick import QQuickWindow  # type: ignore

from UM.Extension import Extension  # type: ignore
from UM.Logger import Logger  # type: ignore
from cura.CuraApplication import CuraApplication  # type: ignore

from .Settings import Settings
from .OnshapeBrowserService import OnshapeBrowserService


class OnshapeBrowserExtension(Extension):

    def __init__(self) -> None:
        super().__init__()

        self._service: OnshapeBrowserService = OnshapeBrowserService(self)

        # The UI objects.
        self._main_dialog: Optional[QQuickWindow] = None
        self._login_dialog: Optional[QQuickWindow] = None

        # Configure the 'extension' menu.
        self.setMenuName(Settings.DISPLAY_NAME)
        self.addMenuItem("Browse", self.showMainWindow)

        def _handleExit():
            self._onExit()
            CuraApplication.getInstance().triggerNextExitCheck()
        CuraApplication.getInstance().getOnExitCallbackManager().addCallback(_handleExit)

    def _onExit(self):
        self._service.saveState()

    def showMainWindow(self) -> None:
        """
        Show the main popup window.
        """
        if not self._main_dialog:
            Logger.info("new window")
            self._main_dialog = cast(QQuickWindow, self._createComponent("MainWindow.qml"))
            self._main_dialog.closing.connect(self._onClosingMainWindow)  # type: ignore
            self._service.onWindowOpened()
        if self._main_dialog and isinstance(self._main_dialog, QQuickWindow):
            Logger.info("existing window")
            self._main_dialog.hide()
            self._main_dialog.show()

    def hideMainWindow(self) -> None:
        """
        Close the main popup window.
        """
        if self._main_dialog and isinstance(self._main_dialog, QQuickWindow):
            Logger.info("hide existing window")
            self._main_dialog.hide()

    def _onClosingMainWindow(self) -> None:
        """
        Actions to run when main window is closing
        """
        if self._login_dialog:
            self._login_dialog.close()

    def showLoginWindow(self, on_finished: Optional[Callable[[],Any]] = None) -> None:
        """
        Show the login popup window.
        """
        if not self._login_dialog:
            self._login_dialog = cast(QQuickWindow, self._createComponent("LoginWindow.qml"))
        if self._login_dialog and isinstance(self._login_dialog, QQuickWindow):
            self._login_dialog.show()
            if on_finished:
                self._login_dialog.closing.connect(on_finished)

    def closeLoginWindow(self) -> None:
        """
        Hide the login popup window.
        """
        if self._login_dialog and isinstance(self._login_dialog, QQuickWindow):
            self._login_dialog.hide()

    def _createComponent(self, qml_file_path: str) -> Optional[QObject]:
        """
        Create a dialog window
        :return: The QML dialog object.
        """
        # Find the QML file in the plugin sources.
        plugin_path = CuraApplication.getInstance().getPluginRegistry().getPluginPath(self.getPluginId())
        if not plugin_path:
            return None
        path = os.path.join(plugin_path, "views", qml_file_path)
        Logger.info("path %s", path)
        # Create the dialog component from a QML file.
        dialog = CuraApplication.getInstance().createQmlComponent(path, {
            "OnshapeService": self._service,
        })
        if not dialog:
            raise Exception("Failed to create Onshape browser dialog")
        return dialog
