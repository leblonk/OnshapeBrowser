import os
import tempfile
from enum import Enum
from typing import List, TYPE_CHECKING, Any, Callable

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot, QUrl  # type: ignore
from PyQt6.QtWidgets import QMessageBox
from UM.Logger import Logger  # type: ignore
from cura.CuraApplication import CuraApplication  # type: ignore

from .OnshapeClient import OnshapeClient
from .PreferencesHelper import PreferencesHelper
from .Settings import Settings
from .api.Document import Document
from .api.Element import Element
from .models.Auth import Auth

if TYPE_CHECKING:
    from .OnshapeBrowserExtension import OnshapeBrowserExtension


class CurrentView(Enum):
    NONE = 1
    DOCUMENTS = 2
    ELEMENTS = 3


class OnshapeBrowserService(QObject):

    # Signal triggered when the authentication token changed.
    authenticationChanged = pyqtSignal()

    # Signal triggered when the list of documents changes.
    documentsChanged = pyqtSignal()

    # Signal triggered when the current document changes.
    currentDocumentChanged = pyqtSignal()

    # Signal triggered when the list of elements changes.
    elementsChanged = pyqtSignal()

    # Signal triggered when the visibility of items changes.
    currentViewChanged = pyqtSignal()

    scaleChanged = pyqtSignal()
    unitsChanged = pyqtSignal()
    angleChanged = pyqtSignal()
    chordChanged = pyqtSignal()
    maxFacetChanged = pyqtSignal()
    minFacetChanged = pyqtSignal()

    def __init__(self, extension: "OnshapeBrowserExtension", parent=None):
        super().__init__(parent)

        self._extension: "OnshapeBrowserExtension" = extension

        self.onshapeClient: OnshapeClient = OnshapeClient()

        # Hold the things found in query results.
        self._query: str = ""

        self._documents: List[Document] = []
        self._elements: List[Element] = []

        PreferencesHelper.initSetting(Settings.ONSHAPE_LAST_DOCUMENT_NAME_KEY, "")
        PreferencesHelper.initSetting(Settings.ONSHAPE_LAST_DOCUMENT_ID_KEY, "")
        PreferencesHelper.initSetting(Settings.ONSHAPE_LAST_WORKSPACE_ID_KEY, "")
        self._currentDocumentName = PreferencesHelper.getSettingValue(Settings.ONSHAPE_LAST_DOCUMENT_NAME_KEY)
        self._currentDocumentId = PreferencesHelper.getSettingValue(Settings.ONSHAPE_LAST_DOCUMENT_ID_KEY)
        self._currentWorkspaceId = PreferencesHelper.getSettingValue(Settings.ONSHAPE_LAST_WORKSPACE_ID_KEY)

        self._password = ""
        try:
            with open(os.path.expanduser("~") + "/.ssh/onshape_password", "r") as f:
                self._password = f.readline().strip()
        except FileNotFoundError:
            pass

        PreferencesHelper.initSetting(Settings.ONSHAPE_BROWSER_USER_NAME_PREFERENCES_KEY, "")
        PreferencesHelper.initSetting(Settings.ONSHAPE_BROWSER_ON_COOKIE_KEY, "")
        PreferencesHelper.initSetting(Settings.ONSHAPE_BROWSER_XSRF_COOKIE_KEY, "")

        self.authenticationChanged.connect(self.getDocumentList)
        self.currentDocumentChanged.connect(self.getElements)

        self._currentView = CurrentView.NONE

        self._scale = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_SCALE, "")
        self._units = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_UNITS, "")
        self._angle = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_ANGLE, "")
        self._chord = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_CHORD, "")
        self._maxFacet = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_MAX_FACET, "")
        self._minFacet = PreferencesHelper.initSetting(Settings.ONSHAPE_EXPORT_MIN_FACET, "")

    def onWindowOpened(self):
        if self._currentDocumentId and self._currentWorkspaceId:
            self._setCurrentView(CurrentView.ELEMENTS)
        else:
            self._setCurrentView(CurrentView.DOCUMENTS)
        self.getInitialList()

    @pyqtSlot(name="openLoginWindow")
    def openLoginWindow(self) -> None:
        """ Open the settings window. """
        if not self._extension:
            return
        self._extension.showLoginWindow()

    @pyqtProperty(str)
    def getUsername(self) -> str:
        """
        Get the last remembered username.
        """
        return PreferencesHelper.getSettingValue(Settings.ONSHAPE_BROWSER_USER_NAME_PREFERENCES_KEY)

    @pyqtProperty(str)
    def getPassword(self) -> str:
        """
        Get the last remembered username.
        """
        return self._password

    @pyqtSlot(str, str, name="authenticate")
    def authenticate(self, username: str, password: str) -> None:
        """ Open the settings window. """
        if not self._extension:
            return

        def _onSuccess():
            previousName = PreferencesHelper.getSettingValue(Settings.ONSHAPE_BROWSER_USER_NAME_PREFERENCES_KEY)
            if previousName != username:
                PreferencesHelper.setSetting(Settings.ONSHAPE_BROWSER_USER_NAME_PREFERENCES_KEY, username)
            self._extension.closeLoginWindow()

        self._callAuthenticate(username,
                               password,
                               on_finished=_onSuccess)

    @pyqtProperty(str, notify=currentDocumentChanged)
    def currentDocumentId(self) -> str:
        """
        Return the key of the active driver
        :return: The active driver key
        """
        return self._currentDocumentId

    @pyqtProperty(str, notify=currentDocumentChanged)
    def currentWorkspaceId(self) -> str:
        """
        Return the key of the active driver
        :return: The active driver key
        """
        return self._currentWorkspaceId

    class HrefItem(QObject):
        image_loaded = pyqtSignal()

        def __init__(self, service, href):
            super().__init__()
            self._service = service
            self._href = href
            self._loadedHref = None
            service.onshapeClient.loadImage(href, self.set)

        @pyqtProperty(QUrl, notify=image_loaded)
        def href(self):
            return QUrl(self._loadedHref)

        def set(self, imageData):
            if imageData:
                self._loadedHref = "data:image/png;base64," + imageData
            self.image_loaded.emit()

    @pyqtProperty("QVariantList", notify=documentsChanged)
    def documents(self) -> list[dict[str, Any]]:
        """
        Get the current active documents.
        """
        docStruct = [docs.toStruct() for docs in self._documents]
        for doc in docStruct:
            doc["thumbnailHref"] = self.HrefItem(self, doc["thumbnailHref"])
        return docStruct

    @pyqtProperty("QVariantList", notify=elementsChanged)
    def elements(self) -> list[dict[str, Any]]:
        """
        Get the current active documents.
        """
        elementStruct = [docs.toStruct() for docs in self._elements]
        for element in elementStruct:
            element["thumbnailHref"] = element["thumbnailHref"] if isinstance(element["thumbnailHref"], self.HrefItem) else self.HrefItem(self, element[
                "thumbnailHref"])
        return elementStruct

    @pyqtSlot(str, name="search")
    def search(self, search_term: str) -> None:
        """
        Search for things by search term.
        :param search_term: What to search for.
        """
        Logger.info(f"search {search_term}")
        self._query = search_term
        self.getDocumentList()

    @pyqtSlot(str, str, str, name="showElements")
    def showElements(self, documentName: str, documentId: str, workspaceId: str) -> None:
        """
        Show the elements for a document by ID.
        """
        if self._currentDocumentId != documentId:
            self._setElements([])
        self._currentDocumentName = documentName
        self._currentDocumentId = documentId
        self._currentWorkspaceId = workspaceId
        self.currentDocumentChanged.emit()
        self._currentView = CurrentView.ELEMENTS
        self.currentViewChanged.emit()

    @pyqtSlot(str, str, str, str, str, name="addElementToBuildPlate")
    def addElementToBuildPlate(self, elementId: str, documentId: str, workspaceId: str, elementType: str, elementName: str) -> None:
        if elementType == "PARTSTUDIO":
            self.onshapeClient.downloadPartStudioStl(documentId, workspaceId, elementId,
                                                     self._scale, self._units, self._angle, self._chord, self._maxFacet, self._minFacet,
                                                     on_finished=lambda fileBytes: self._onDownloadStlFinished(fileBytes, elementName + ".stl"),
                                                     on_failed=lambda error: self._showError(error))
        else:
            self.onshapeClient.downloadAssemblyStl(documentId, workspaceId, elementId,
                                                     self._scale, self._units, self._angle, self._chord, self._maxFacet, self._minFacet,
                                                     on_finished=lambda fileBytes: self._onDownloadStlFinished(fileBytes, elementName + ".stl"),
                                                     on_failed=lambda error: self._showError(error))

    @pyqtProperty(bool, notify=currentViewChanged)
    def elementsVisible(self) -> bool:
        return self._currentView == CurrentView.ELEMENTS

    @pyqtProperty(bool, notify=currentViewChanged)
    def documentsVisible(self) -> bool:
        return self._currentView == CurrentView.DOCUMENTS

    @pyqtProperty(str, notify=currentDocumentChanged)
    def currentDocumentName(self) -> str:
        return self._currentDocumentName

    @pyqtSlot(name="hideElements")
    def hideElements(self) -> None:
        self._setCurrentView(CurrentView.DOCUMENTS)
        self._currentDocumentId = ""
        self._currentWorkspaceId = ""
        self._setElements( [])
        if len(self._documents) == 0:
            self.getDocumentList()
        self.currentDocumentChanged.emit()

    @pyqtProperty(str, notify=scaleChanged)
    def scale(self) -> str:
        return self._scale

    @pyqtSlot(str, name="setScale")
    def setScale(self, scale: str) -> None:
        Logger.info(f"setting scale to {scale}")
        if self._scale != scale:
            self._scale = scale
            self.scaleChanged.emit()

    @pyqtProperty(str, notify=unitsChanged)
    def units(self) -> str:
        return self._units

    @pyqtSlot(str, name="setUnits")
    def setUnits(self, units: str) -> None:
        if units == "Default":
            units = ""
        Logger.info(f"setting units to {units}")
        if self._units != units:
            self._units = units
            self.unitsChanged.emit()

    @pyqtProperty(str, notify=angleChanged)
    def angle(self) -> str:
        return self._angle

    @pyqtSlot(str, name="setAngle")
    def setAngle(self, angle: str) -> None:
        Logger.info(f"setting angle to {angle}")
        if self._angle != angle:
            self._angle = angle
            self.angleChanged.emit()

    @pyqtProperty(str, notify=chordChanged)
    def chord(self) -> str:
        return self._chord

    @pyqtSlot(str, name="setChord")
    def setChord(self, chord: str) -> None:
        Logger.info(f"setting chord to {chord}")
        if self._chord != chord:
            self._chord = chord
            self.chordChanged.emit()

    @pyqtProperty(str, notify=maxFacetChanged)
    def maxFacet(self) -> str:
        return self._maxFacet

    @pyqtSlot(str, name="setMaxFacet")
    def setMaxFacet(self, maxFacet: str) -> None:
        Logger.info(f"setting max facet to {maxFacet}")
        if self._maxFacet != maxFacet:
            self._maxFacet = maxFacet
            self.maxFacetChanged.emit()

    @pyqtProperty(str, notify=minFacetChanged)
    def minFacet(self) -> str:
        return self._minFacet

    @pyqtSlot(str, name="setMinFacet")
    def setMinFacet(self, minFacet: str) -> None:
        Logger.info(f"setting min facet to {minFacet}")
        if self._minFacet != minFacet:
            self._minFacet = minFacet
            self.minFacetChanged.emit()

    def saveState(self):
        Logger.info("saving settings")
        # make sure to save the current state in preferences
        PreferencesHelper.setSetting(Settings.ONSHAPE_LAST_DOCUMENT_NAME_KEY, self._currentDocumentName)
        PreferencesHelper.setSetting(Settings.ONSHAPE_LAST_DOCUMENT_ID_KEY, self._currentDocumentId)
        PreferencesHelper.setSetting(Settings.ONSHAPE_LAST_WORKSPACE_ID_KEY, self._currentWorkspaceId)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_SCALE, self._scale)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_UNITS, self._units)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_ANGLE, self._angle)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_CHORD, self._chord)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_MAX_FACET, self._maxFacet)
        PreferencesHelper.setSetting(Settings.ONSHAPE_EXPORT_MIN_FACET, self._minFacet)

    def getInitialList(self):
        self._checkInitialAuth(on_success=self.getDocumentList if self._currentView == CurrentView.DOCUMENTS else self.getElements)

    def getDocumentList(self):
        def _setDocs(list: List[Document]) -> None:
            self._documents = list
            self.documentsChanged.emit()

        self.onshapeClient.getDocumentList(self._query,
                                           on_finished=_setDocs,
                                           on_failed=lambda error: self._showError(error))

    def _setElements(self, elements: List[Element]) -> None:
        self._elements = elements
        self.elementsChanged.emit()

    def getElements(self):
        if self._currentDocumentId and self._currentWorkspaceId:
            self.onshapeClient.getElementList(self._currentDocumentId, self._currentWorkspaceId,
                                              on_finished=self._setElements,
                                              on_failed=lambda error: self._showError(error))

    def _setCurrentView(self, new_visibility_state: CurrentView):
        old_state = self._currentView
        if old_state != new_visibility_state:
            self._currentView = new_visibility_state
            self.currentViewChanged.emit()

    def _checkInitialAuth(self, on_success: Callable[[], Any]):
        self.onshapeClient.checkSession(on_authenticated=on_success,
                                        on_not_authenticated=lambda: self._extension.showLoginWindow())

    def _onDownloadStlFinished(self, file_bytes: bytes, file_name: str) -> None:
        """
        Callback to receive the downloaded file on and import it onto the build plate.
        Note that we do not use any context clauses here. Even though that would be cleaner,
        CuraApplication.getInstance() switches contexts and makes temporary dirs and files be removed by their context.
        :param file_bytes: The file as bytes.
        :param file_name: The file name.
        """
        file_path = os.path.join(tempfile.mkdtemp(), file_name)
        tmp_file = open(file_path, "wb")
        tmp_file.write(file_bytes)
        tmp_file.close()
        CuraApplication.getInstance().readLocalFile(QUrl().fromLocalFile(tmp_file.name))
        self._extension.hideMainWindow()

    @staticmethod
    def _showError(error: str) -> None:
        """
        Show a popup with the API error that was received.
        :param error: The API error.
        """
        mb = QMessageBox()
        mb.setIcon(QMessageBox.Icon.Critical)
        mb.setWindowTitle("Oh no!")
        error_message = error
        mb.setText("Error: {}.".format(error_message))
        mb.exec()

    def _callAuthenticate(self, username: str, password: str, on_finished: Callable[[], Any]) -> str:
        def _setCookie(auth: Auth) -> None:
            PreferencesHelper.setSetting(Settings.ONSHAPE_BROWSER_ON_COOKIE_KEY, auth.on_cookie)
            PreferencesHelper.setSetting(Settings.ONSHAPE_BROWSER_XSRF_COOKIE_KEY, auth.xsrf_cookie)
            on_finished()
            self.authenticationChanged.emit()

        self.onshapeClient.callAuthenticate(username, password,
                                            on_finished=lambda auth: _setCookie(auth),
                                            on_failed=lambda error: self._showError(error))
