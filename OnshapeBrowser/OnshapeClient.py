import base64
import json
from abc import ABC
from typing import List, Callable, Any, Optional

from PyQt6.QtCore import QByteArray, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest, QNetworkCookieJar, QNetworkCookie
from UM.Logger import Logger  # type: ignore

from .PreferencesHelper import PreferencesHelper
from .Settings import Settings
from .api.ApiHelper import ApiHelper
from .api.Document import Document
from .api.Element import Element
from .models.Auth import Auth
from .models.Result import Result


class OnshapeClient(ABC):
    # Re-usable network manager.
    _manager = QNetworkAccessManager()
    _manager.setCookieJar(QNetworkCookieJar())

    # Prevent auto-removing running callbacks by the Python garbage collector.
    _anti_gc_callbacks: List[Callable[[], None]] = []

    BASE_URL = "https://cad.onshape.com"

    def __init__(self) -> None:
        self._auth_state: Optional[str] = None
        PreferencesHelper.initSetting(Settings.DEFAULT_API_CLIENT_PREFERENCES_KEY)

    def callAuthenticate(self, username: str, password: str, on_finished: Callable[[Auth], Any],
                         on_failed: Callable[[str], Any]):
        # curl 'https://cad.onshape.com/api/users/session' \
        #   -H 'Content-Type: application/json' \
        #   -X POST \
        #   --data-raw '{"email":"xx@xx.org","password":"xxxxxxx"}' \
        self._manager.setCookieJar(QNetworkCookieJar())
        request = QNetworkRequest(QUrl(f"{self.BASE_URL}/api/users/session"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        data = json.dumps({"email": username, "password": password})
        reply = self._manager.post(request, QByteArray(data.encode('utf-8')))

        def _parseAuthResponse(reply: QNetworkReply) -> Result[Auth]:
            statusCode = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if statusCode == 200:
                on_cookie = None
                xsrf_cookie = None
                for cookie in reply.header(QNetworkRequest.KnownHeaders.SetCookieHeader):
                    cookie_name = bytes(cookie.name()).decode()
                    if cookie_name == 'on':
                        on_cookie = bytes(cookie.value()).decode()
                    if cookie_name == 'XSRF-TOKEN':
                        xsrf_cookie = bytes(cookie.value()).decode()
                if on_cookie and xsrf_cookie:
                    return Result.success(Auth(on_cookie, xsrf_cookie))
                else:
                    return Result.error(404, "Cookie named 'on' not found")
            else:
                return Result.error(statusCode, str(reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute)))

        self._addCallback(request,
                          reply,
                          on_finished=lambda auth: on_finished(auth),
                          on_failed=lambda status_code, reason: on_failed("{}:{}".format(status_code, reason)),
                          parser=_parseAuthResponse)

    def checkSession(self, on_authenticated: Callable[[Any], Any], on_not_authenticated: Callable[[Any], Any]):
        # curl 'https://cad.onshape.com/api/v5/users/sessioninfo' \
        #      -H "Cookie: on=+r/m45+cFIKP+k2qyx6F14UFnBod47yauMBKIF1s2xNeLVPeR9P4+I21M4D5BPDmafEVSn2908wqwQsIYynSszHZZDNjwnwI4cd+FH/IpYItNVyUGn6wdpGQqVvLBxp9fCCAx614T29+9Q8wSlgTVUzr5aHL+A4Jtb/e21gx1kyljkWgguVzo9ZyVjdSvXHLqlOtDVgl47bnVUGCrbXs0AP6zfBjZ4YXtpicGd6uIdD3zYpmHk9nfymPBv+r1tfivKXi+d3gkCF83tDB4gyR7MEQimZ0Z7kFUYK8hg=="
        request = QNetworkRequest(QUrl(f"{self.BASE_URL}/api/v5/users/sessioninfo"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        Logger.info("trying cookie: %s", PreferencesHelper.getSettingValue(Settings.ONSHAPE_BROWSER_ON_COOKIE_KEY))
        self._setAuth(request)
        reply = self._manager.get(request)

        def _parseResponse(reply: QNetworkReply) -> Result[None]:
            statusCode = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            Logger.info("calling %s: %d", request.url(), statusCode)
            if statusCode == 200:
                return Result.success(None)
            elif statusCode == 204:
                return Result.error(401, "no current session")
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda ignore: on_authenticated(),
                          on_failed=lambda statusCode, reason: on_not_authenticated(),
                          parser=_parseResponse)

    def getDocumentList(self, query: str, on_finished: Callable[[List[Document]], Any], on_failed: Callable[[str], Any]):
        # curl 'https://cad.onshape.com/api/documents' \
        #      -H "Cookie: on=+r/m45+cFIKP+k2qyx6F14UFnBod47yauMBKIF1s2xNeLVPeR9P4+I21M4D5BPDmafEVSn2908wqwQsIYynSszHZZDNjwnwI4cd+FH/IpYItNVyUGn6wdpGQqVvLBxp9fCCAx614T29+9Q8wSlgTVUzr5aHL+A4Jtb/e21gx1kyljkWgguVzo9ZyVjdSvXHLqlOtDVgl47bnVUGCrbXs0AP6zfBjZ4YXtpicGd6uIdD3zYpmHk9nfymPBv+r1tfivKXi+d3gkCF83tDB4gyR7MEQimZ0Z7kFUYK8hg=="
        Logger.info(f"documents with query '{query}'")
        query_param = f"&filter=0&q={query}" if len(query) > 0 else ""
        request = QNetworkRequest(QUrl(f"{self.BASE_URL}/api/documents?sortColumn=modifiedAt&sortOrder=desc&offset=0&limit=20{query_param}"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        self._setAuth(request)
        reply = self._manager.get(request)

        def _parseListResponse(reply: QNetworkReply) -> Result[List[Document]]:
            statusCode, list = ApiHelper.parseReplyAsJson(reply)
            if statusCode == 200:
                if not list or not isinstance(list, dict):
                    return Result.error(503, "Parsed string not a dict?")
                items = list.get("items", [])

                return Result.success([Document({
                    "name": item.get("name"),
                    "id": item.get("id"),
                    "resourceType": item.get("resourceType"),
                    "isContainer": item.get("isContainer"),
                    "modifiedAt": item.get("modifiedAt"),
                    "modifiedByName": item.get("modifiedBy").get("name"),
                    "workspaceId": item.get("defaultWorkspace").get("id"),
                    "thumbnailHref": self._getThumbnailHref(item.get("thumbnail"))
                }) for item in items])
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda list: on_finished(list),
                          on_failed=lambda statusCode, reason: on_failed("{}:{}".format(statusCode, reason)),
                          parser=_parseListResponse)

    def getElementList(self, documentId: str, workspaceId: str, on_finished: Callable[[List[Element]], Any], on_failed: Callable[[str], Any]):
        # curl 'https://cad.onshape.com/api/v5/documents/d/f62bc4c476956f030120d062/w/0e75ea7f66d8294c344e3ad8/elements?elementType=ASSEMBLY&withThumbnails=true' \
        #      -H "Cookie: on=+r/m45+cFIKP+k2qyx6F14UFnBod47yauMBKIF1s2xNeLVPeR9P4+I21M4D5BPDmafEVSn2908wqwQsIYynSszHZZDNjwnwI4cd+FH/IpYItNVyUGn6wdpGQqVvLBxp9fCCAx614T29+9Q8wSlgTVUzr5aHL+A4Jtb/e21gx1kyljkWgguVzo9ZyVjdSvXHLqlOtDVgl47bnVUGCrbXs0AP6zfBjZ4YXtpicGd6uIdD3zYpmHk9nfymPBv+r1tfivKXi+d3gkCF83tDB4gyR7MEQimZ0Z7kFUYK8hg=="
        request = QNetworkRequest(
            QUrl(f"{self.BASE_URL}/api/v5/documents/d/{documentId}/w/{workspaceId}/elements?withThumbnails=true"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        self._setAuth(request)
        Logger.info("Getting elements")
        reply = self._manager.get(request)

        def _parseListResponse(reply: QNetworkReply) -> Result[List[Document]]:
            statusCode, elements = ApiHelper.parseReplyAsJson(reply)
            if statusCode == 200:
                if not list or not isinstance(elements, list):
                    return Result.error(503, "Parsed string not a list?")

                return Result.success([Element({
                    "name": item.get("name"),
                    "id": item.get("id"),
                    "documentId": documentId,
                    "workspaceId": workspaceId,
                    "type": item.get("elementType"),
                    "thumbnailHref": self._getThumbnailHref(item.get("thumbnailInfo"))
                }) for item in elements])
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda list: on_finished(list),
                          on_failed=lambda statusCode, reason: on_failed("{}:{}".format(statusCode, reason)),
                          parser=_parseListResponse)

    def getElementParts(self, documentId: str, workspaceId: str, elementId: str, on_finished: Callable[[List[str]], Any], on_failed: Callable[[str], Any]):
        # curl 'https://cad.onshape.com/api/v5/assemblies/d/f62bc4c476956f030120d062/w/0e75ea7f66d8294c344e3ad8/e/0e75ea7f66d8294c344e3ad8' \
        #      -H "Cookie: on=+r/m45+cFIKP+k2qyx6F14UFnBod47yauMBKIF1s2xNeLVPeR9P4+I21M4D5BPDmafEVSn2908wqwQsIYynSszHZZDNjwnwI4cd+FH/IpYItNVyUGn6wdpGQqVvLBxp9fCCAx614T29+9Q8wSlgTVUzr5aHL+A4Jtb/e21gx1kyljkWgguVzo9ZyVjdSvXHLqlOtDVgl47bnVUGCrbXs0AP6zfBjZ4YXtpicGd6uIdD3zYpmHk9nfymPBv+r1tfivKXi+d3gkCF83tDB4gyR7MEQimZ0Z7kFUYK8hg=="
        request = QNetworkRequest(
            QUrl(f"{self.BASE_URL}/api/v5/assemblies/d/{documentId}/w/{workspaceId}/e/{elementId}"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        self._setAuth(request)
        reply = self._manager.get(request)

        def _parseElementResponse(reply: QNetworkReply) -> Result[List[str]]:
            statusCode, element = ApiHelper.parseReplyAsJson(reply)
            if statusCode == 200:
                if not list or not isinstance(element, dict):
                    return Result.error(503, f"Parsed {type(element)} not a dict?")

                return Result.success([part.get("partId") for part in element.get("parts")])
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda list: on_finished(list),
                          on_failed=lambda statusCode, reason: on_failed("{}:{}".format(statusCode, reason)),
                          parser=_parseElementResponse)

    def downloadPartStudioStl(self, document_id: str, workspace_id: str, element_id: str,
                              scale: str, units: str, angle: str, chord: str, max_facet: str, min_facet: str,
                              on_finished: Callable[[bytes], Any],
                              on_failed: Callable[[str], Any]):
        scale_str = f"&scale={scale}" if scale != "" else ""
        units_str = f"&units={units.lower()}" if units != "" else ""
        angle_str = f"&angleTolerance={angle}" if angle != "" else ""
        chord_str = f"&chordTolerance={chord}" if chord != "" else ""
        max_facet_str = f"&maxFacetWidth={max_facet}" if max_facet != "" else ""
        min_facet_str = f"&minFacetWidth{min_facet}" if min_facet != "" else ""
        request = QNetworkRequest(
            QUrl(
                f"{self.BASE_URL}/api/v5/partstudios/d/{document_id}/w/{workspace_id}/e/{element_id}/stl?a=a{scale_str}{units_str}{angle_str}{chord_str}{max_facet_str}{min_facet_str}"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        self._setAuth(request)
        reply = self._manager.get(request)

        def _parse_redirect_response(reply: QNetworkReply) -> Result[bytes]:
            statusCode = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if statusCode == 200:
                return Result.success(reply.readAll().data())
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda stl: on_finished(stl),
                          on_failed=lambda status_code, reason: on_failed("{}:{}".format(status_code, reason)),
                          parser=_parse_redirect_response)

    def downloadAssemblyStl(self, document_id: str, workspace_id: str, element_id: str,
                            scale: str, units: str, angle: str, chord: str, max_facet: str, min_facet: str,
                            on_finished: Callable[[bytes], Any],
                            on_failed: Callable[[str], Any]):
        scale_str = f"&scale={scale}" if scale != "" else ""
        units_str = f"&units={units.lower()}" if units != "" else ""
        angle_str = f"&angleTolerance={angle}" if angle != "" else ""
        chord_str = f"&chordTolerance={chord}" if chord != "" else ""
        max_facet_str = f"&maxFacetWidth={max_facet}" if max_facet != "" else ""
        min_facet_str = f"&minFacetWidth{min_facet}" if min_facet != "" else ""
        request = QNetworkRequest(QUrl(f"{self.BASE_URL}/api/documents/d/{document_id}/w/{workspace_id}/e/{element_id}/export?"
                                       f"format=STL&destinationName=export&mode=binary&triggerAutoDownload=true&storeInDocument=false&configuration=&resolution=custom&grouping=true"
                                       f"{scale_str}{units_str}{angle_str}{chord_str}{max_facet_str}{min_facet_str}"))
        request.setMaximumRedirectsAllowed(0)
        self._setAuth(request)
        reply = self._manager.get(request)

        def _parse_response(reply: QNetworkReply) -> Result[bytes]:
            for header in reply.request().rawHeaderList():
                Logger.info("header {}: {}", header.data().decode('ascii'), reply.request().rawHeader(header).data().decode('ascii'))
            statusCode = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if statusCode == 200:
                return Result.success(reply.readAll().data())
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda stl: on_finished(stl),
                          on_failed=lambda status_code, reason: on_failed("{}:{}".format(status_code, reason)),
                          parser=_parse_response)

    def loadImage(self, href: str, setter: Callable[[str], Any]):
        request = QNetworkRequest(QUrl(href))
        self._setAuth(request)
        reply = self._manager.get(request)

        def _readBase64(reply: QNetworkReply) -> Result[str]:
            statusCode = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
            if statusCode == 200:
                data = reply.readAll().data()
                return Result.success(base64.b64encode(data).decode('ascii'))
            elif statusCode == 204:
                return Result.error(401, "Could not load image")
            else:
                return Result.error(statusCode, reply.attribute(QNetworkRequest.Attribute.HttpReasonPhraseAttribute))

        self._addCallback(request,
                          reply,
                          on_finished=lambda str: setter(str),
                          on_failed=lambda statusCode, reason: Logger.info("Error %d reading image: %s".format(statusCode, reason)),
                          parser=_readBase64)

    def _addCallback(self,
                     request: QNetworkRequest,
                     reply: QNetworkReply,
                     on_finished: Callable[[Any], Any],
                     on_failed: Callable[[int, str], Any],
                     parser: Callable[[QNetworkReply], Result]) -> None:
        """
        Creates a callback function so that it includes the parsing of the response into the correct model.
        The callback is added to the 'finished' signal of the reply.
        :param reply: The reply that should be listened to.
        :param on_finished: The callback in case the request is successful.
        :param on_failed: The callback in case the request fails.
        :param parser: A custom parser for the response data, defaults to a JSON parser.
        """
        Logger.info("making request: {}", request.url().toDisplayString())
        for header in request.rawHeaderList():
            Logger.info("making request header: {}: {}", header.data().decode('ascii'), request.rawHeader(header).data().decode('ascii'))

        def parse() -> None:
            self._anti_gc_callbacks.remove(parse)
            result = parser(reply)
            Logger.info("reply status code: {}", result.status_code if result.isError() else 200)
            if result.isError():
                body = reply.readAll().data().decode()
                if not result.status_code or result.status_code >= 400:
                    Logger.warning("API {} returned with status {} and error {} body {}", reply.url().toDisplayString(), result.status_code,
                                   result.error_string, body)
                    if on_failed:
                        on_failed(result.status_code, result.error_string)
                elif result.status_code in [301, 302, 307]:
                    redirect_request = QNetworkRequest(QUrl(reply.header(QNetworkRequest.KnownHeaders.LocationHeader)))
                    Logger.info("Redirect request: {}", redirect_request.url().toDisplayString())
                    redirect_request.setRawHeader(QByteArray("Accept-Encoding".encode()), QByteArray("gzip, deflate, br".encode()))
                    self._setAuth(redirect_request)
                    redirect = self._manager.get(redirect_request)
                    self._addCallback(redirect_request, redirect, on_finished, on_failed, parser)
            else:
                on_finished(result.value)
            reply.deleteLater()

        self._anti_gc_callbacks.append(parse)
        reply.finished.connect(parse)  # type: ignore

    @staticmethod
    def _strToByteArray(data: str) -> QByteArray:
        """
        Creates a QByteArray object from string data.
        :param data: The string to convert.
        :return: The QByteArray.
        """
        bytes = str.encode(data)
        result = QByteArray()
        result.append(bytes)
        return result

    def _setAuth(self, request: QNetworkRequest):
        self._manager.setCookieJar(QNetworkCookieJar())
        on_cookie = PreferencesHelper.getSettingValue(Settings.ONSHAPE_BROWSER_ON_COOKIE_KEY)
        if on_cookie:
            new_cookie = QNetworkCookie(QByteArray("on".encode()), QByteArray(on_cookie.encode()))
            new_cookie.setPath("/")
            new_cookie.setDomain(".onshape.com")
            new_cookie.setSecure(True)
            self._manager.cookieJar().insertCookie(new_cookie)
        # xsrf_cookie = PreferencesHelper.getSettingValue(Settings.ONSHAPE_BROWSER_XSRF_COOKIE_KEY)
        # if xsrf_cookie:
        #     new_cookie = QNetworkCookie(QByteArray("XSRF-TOKEN".encode()), QByteArray(xsrf_cookie.encode()))
        #     new_cookie.setPath("/")
        #     new_cookie.setSecure(True)
        #     self._manager.cookieJar().insertCookie(new_cookie)
            # request.setRawHeader(QByteArray("X-XSRF-TOKEN".encode()), QByteArray(xsrf_cookie.encode()))

    def _getThumbnailHref(self, thumbnails) -> str:
        # "thumbnail" : {
        #     "sizes" : [ {
        #         "size" : "70x40",
        #         "href" : "https://cad.onshape.com/api/thumbnails/d/f62bc4c476956f030120d062/w/0e75ea7f66d8294c344e3ad8/s/70x40?t=1679599153183",
        #         "mediaType" : "image/png",
        #     } ],
        smallestHeight = 10000
        smallestHref = None
        for thumbnail in thumbnails.get("sizes"):
            size = thumbnail.get("size")
            parts = size.split("x")
            height = int(parts[1])
            if height < smallestHeight:
                smallestHeight = height
                smallestHref = thumbnail.get("href")
        return smallestHref
