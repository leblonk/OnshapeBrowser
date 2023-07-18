# Copyright (c) 2020.
# OnshapeBrowser plugin is released under the terms of the LGPLv3 or higher.
from typing import Dict, Any

from PyQt6.QtCore import QObject


class JsonObject(QObject):
    """ Simple class that converts a JSON object to a Python model. """
    def __init__(self, _dict: Dict[str, Any]):
        self.type = self.__class__.__name__
        if _dict:
            vars(self).update(_dict)
        super().__init__()

    def toStruct(self) -> Dict[str, Any]:
        """
        Get a dict representation of the object.
        :return: The dict.
        """
        return self.__dict__
