# Copyright (c) 2020.
# Onshape Browser plugin is released under the terms of the LGPLv3 or higher.
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class Result(Generic[T]):

    def __init__(self, value: Optional[T], status_code: Optional[int], error_string: Optional[str]):
        self._value = value
        self._status_code = status_code
        self._error_string = error_string

    @classmethod
    def success(cls, value: T):
        return cls(value, None, None)

    @classmethod
    def error(cls, status_code: int, error_string: str):
        return cls(None, status_code, error_string)

    @property
    def value(self) -> T:
        if self.isError():
            raise Exception(f"no value in result, error {self._status_code} instead")
        return self._value

    @property
    def status_code(self) -> int:
        if not self.isError():
            raise Exception(f"no error in result, value {self._value} instead")
        return self._status_code

    @property
    def error_string(self) -> str:
        if not self.isError():
            raise Exception(f"no error in result, value {self._value} instead")
        return self._error_string

    def hasValue(self) -> bool:
        return self._status_code is None

    def isError(self) -> bool:
        return self._status_code is not None
