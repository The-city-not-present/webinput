
from __future__ import annotations

import re
from functools import reduce
from typing import Any
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

from .py_translatable_text_class import LocalizedText

# # validation
# type
# required
# minLength
# maxLength
# pattern
# minimum
# maximum
# multipleOf
# enum
# const
# items
# uniqueItems
# properties
# additionalProperties
# oneOf
# anyOf
# allOf
# if / then / else
# ...

class QuestionInternalError(Exception):
    """Something is off please check cause you re not using it correctly, so my advice is to close this project and focus on something else"""


def validate_name(s):
    if not isinstance(s, str):
        raise QuestionInternalError(f'name "{s}" is not str')
    if not s or s.strip() == '':
        raise QuestionInternalError(f'name "{s}" is not str')
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', s):
        raise QuestionInternalError(f'name "{s}" is not str')
    if re.match(r'^\s*\b(?:Add|All|Alter|And|As|Asc|Base|By|Case|Const|Create|Default|Delete|Desc|Dim|Distinct|Do|Drop|Each|Else|ElseIf|End|Error|Exec|Exit|Explicit|FALSE|For|From|Function|GlobalVariables|GoTo|Having|HelperFields|If|Implicit|In|Into|Is|Like|Loop|Mod|Next|Not|Null|On|Option|Or|Paper|Ran|Resume|Rev|Rot|Rotate|Section|Select|Set|Step|Sub|Then|To|TRUE|Truncate|Until|Update|Values|Where|While|With|Xor)\b\s$',s,flags=re.I):
        raise QuestionInternalError(f'name "{s}" is not str')
    return True


class QuestionTypeAbs(ABC):
    is_plain: bool # indicates type "type" - compound or plain
    is_hidden: bool = False # absolutely unnecessary, just capturing this for future
    is_system: bool = False # absolutely unnecessary, just capturing this for future
    is_derived: bool = False # absolutely unnecessary, just capturing this for future
    required: bool = True # should be translated to json schema

class QuestionModifier(ABC):
    @abstractmethod
    def as_json(self):
        raise NotImplementedError('Question object must be instantiated by specific class')
    pass

@dataclass
class Category():
    name: str
    label: LocalizedText
    properties: dict[str, Any] = field(default_factory=dict)
    modifiers: set[QuestionModifier] = field(default_factory=set)
    def _validate_name(self):
        return validate_name(self.name)
    def __eq__(self, other):
        if not isinstance(other, Category):
            return NotImplemented
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)

@dataclass
class Question(QuestionTypeAbs):
    name: str
    label: LocalizedText
    properties: dict[str, Any] = field(default_factory=dict)
    modifiers: set[QuestionModifier] = field(default_factory=set)
    widget: Any | None = None
    helper_fields: dict[str, Question] = field(default_factory=dict)
    def _validate_name(self):
        return validate_name(self.name)
    def __eq__(self, other):
        if not isinstance(other, Question):
            return NotImplemented
        return self.name == other.name
    def __hash__(self):
        return hash(self.name)
    @abstractmethod
    def get_type_str(self) -> str:
        ...

class QuestionTypePlain(Question):
    is_plain: bool = True
    response: Any

class QuestionTypeCompound(Question):
    is_plain: bool = False

class QuestionTypeBlock(QuestionTypeCompound):
    fields: list[Question]
    def get_type_str(self) -> str:
        return 'block'

class QuestionTypeLoop(QuestionTypeCompound):
    fields: list[Question]
    iterations: list[Category]
    def get_type_str(self) -> str:
        return 'loop'

class QuestionTypeText(QuestionTypePlain):
    response: str
    validation: Any
    def get_type_str(self) -> str:
        return 'text'

class QuestionTypeInt(QuestionTypePlain):
    response: int
    validation: Any
    def get_type_str(self) -> str:
        return 'int'

class QuestionTypeFloat(QuestionTypePlain):
    response: float
    validation: Any
    def get_type_str(self) -> str:
        return 'float'

class QuestionTypeBool(QuestionTypePlain):
    response: bool
    validation: Any
    def get_type_str(self) -> str:
        return 'boolean'

class QuestionTypeDatetime(QuestionTypePlain):
    response: datetime
    validation: Any
    def get_type_str(self) -> str:
        return 'datetime'

class QuestionTypeSinglePunch(QuestionTypePlain):
    response: Category
    categories: set[Category]
    validation: Any
    def get_type_str(self) -> str:
        return 'singlepunch'

class QuestionTypeMultiPunch(QuestionTypePlain):
    response: set[Category]
    categories: set[Category]
    validation: Any
    def get_type_str(self) -> str:
        return 'multipunch'


