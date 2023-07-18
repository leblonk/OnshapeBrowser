from typing import Dict, Any

from .JsonObject import JsonObject


class Element(JsonObject):
    def __init__(self, _dict: Dict[str, Any]):
        self.name = None
    #     self.thumbnail = None
    # "thumbnailInfo" : {
    #     "sizes" : [ {
    #         "size" : "70x40",
    #         "href" : "https://cad.onshape.com/api/thumbnails/d/f62bc4c476956f030120d062/w/0e75ea7f66d8294c344e3ad8/s/70x40?t=1679599153183",
    #         "mediaType" : "image/png",
    #     } ],
        self.name = None
        self.id = None
        self.documentId = None
        self.workspaceId = None
        self.type = None
        self.thumbnailHref = None
        super().__init__(_dict)
