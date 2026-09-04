
from __future__ import annotations

import re
from typing import Any, Callable
from dataclasses import dataclass, field, fields
import copy
from datetime import datetime, date
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

class QuestionValidationError(Exception):
    """Validation failed"""


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
    is_required: bool = True # should be translated to json schema
    QuestionInternalError = QuestionInternalError
    QuestionValidationError = QuestionValidationError

@dataclass
class QuestionModifier(ABC):
    @abstractmethod
    def as_json(self):
        raise NotImplementedError('Question object must be instantiated by specific class')
    @abstractmethod
    def validate(self, question: Question, data: dict) -> bool:
        raise NotImplementedError('Question object must be instantiated by specific class')

@dataclass
class QuestionModifierIsExclusive(QuestionModifier):
    data: list[Category] = field(default_factory=list)
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'cannotcombine': LocalizedText('{resp} cannot be combined with other responses'),
    })
    def as_json(self):
        return {
            "ExclusiveCategories": [ cat.name for cat in self.data ],
        }
    def validate(self,question: Question, data: Any) -> bool:
        def _err():
            raise QuestionValidationError(f'is_exclusive modifier can only be applied on single-punch and multi-punch quesitons')
        response: set = question.response if isinstance(question, QuestionTypeMultiPunch) else {question.response} if isinstance(question, QuestionTypeSinglePunch) else _err()
        selected_exclusive = set(cat for cat in response if cat.name in set(c.name for c in response) and cat.name in set(c.name for c in self.data))
        validation_failure = len(selected_exclusive) > 1
        if validation_failure:
            raise QuestionValidationError( str(self.error['cannotcombine']).format( resp = repr(next(iter(selected_exclusive)).label) ) )
        else:
            return True

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
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
    })
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
    @abstractmethod
    def validate(self, data) -> bool:
        ...
    @abstractmethod
    def assign(self, data) -> Question:
        ...
    def _assign_helper_fields(self, data):
        if hasattr(self, 'helper_fields') and self.helper_fields:
            for h_f_name, f in self.helper_fields.items():
                if h_f_name in data:
                    f.assign(data.get(h_f_name)) # "h"elper_"f"field_"name"
    def _validate_helper_fields(self, data) -> bool:
        if hasattr(self, 'helper_fields') and self.helper_fields:
            return all(f.validate(data.get(h_f_name)) for h_f_name, f in self.helper_fields.items())
        return True
    def update(self, other):
        for f in fields(other):
            if f.name=='response':
                pass
            else:
                setattr(self, f.name, copy.deepcopy(getattr(other, f.name)))

@dataclass
class QuestionTypePlain(Question):
    is_plain: bool = True

@dataclass
class QuestionTypeCompound(Question):
    is_plain: bool = False

@dataclass
class QuestionTypeBlock(QuestionTypeCompound):
    fields: list[Question] = field(default_factory=list)
    @property
    def response(self) -> list[Question]:
        return self.fields
    def get_type_str(self) -> str:
        return 'block'
    def validate(self, data) -> bool:
        return all(f.validate(data.get(f.name)) for f in self.fields) and self._validate_helper_fields(data.get('HelperFields', {}))
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        for f in self.fields:
            if f.name in data:
                f.assign(data.get(f.name))
        self._assign_helper_fields(data.get('HelperFields', {}))
        return self

@dataclass
class QuestionTypeLoop(QuestionTypeCompound):
    fields: list[Question] = field(default_factory=list)
    iterations: list[Category] = field(default_factory=list)
    response: dict[str, list[Question]] = field(default_factory=dict)
    def get_type_str(self) -> str:
        return 'loop'
    def validate(self, data) -> bool:
        return all(f.validate(data.get(f.name)) for f in self.fields) and self._validate_helper_fields(data.get('HelperFields', {}))
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        for cat_spec in self.iterations:
            if cat_spec.name in data:
                data_this_iteration = data.get(cat_spec.name)
                if cat_spec.name not in self.response:
                    self.response[cat_spec.name] = [copy.deepcopy(f) for f in self.fields]
                response_slice = self.response.get(cat_spec.name)
                for field_index,f_spec in enumerate(self.fields):
                    if f_spec.name in data_this_iteration:
                        f: Question = response_slice[field_index]
                        f.assign(data_this_iteration.get(f_spec.name))
        self._assign_helper_fields(data.get('HelperFields', {}))
        return self

@dataclass
class QuestionTypeText(QuestionTypePlain):
    response: str | None = None
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'typemismatch': LocalizedText('Expected response of type str'),
    })
    def get_type_str(self) -> str:
        return 'text'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, str):
                raise QuestionValidationError( str(self.error['typemismatch']))
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = data
        return self

@dataclass
class QuestionTypeInt(QuestionTypePlain):
    response: int | None = None
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'typemismatch': LocalizedText('Expected response of type integer'),
    })
    def get_type_str(self) -> str:
        return 'int'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, int):
                raise QuestionValidationError( str(self.error['typemismatch']))
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = data
        return self

@dataclass
class QuestionTypeFloat(QuestionTypePlain):
    response: float | None = None
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'typemismatch': LocalizedText('Expected response of type float (floating-point real number)'),
    })
    def get_type_str(self) -> str:
        return 'float'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, float):
                raise QuestionValidationError( str(self.error['typemismatch']))
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = data
        return self

@dataclass
class QuestionTypeBool(QuestionTypePlain):
    response: bool | None = None
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'typemismatch': LocalizedText('Expected response of type boolean'),
    })
    def get_type_str(self) -> str:
        return 'boolean'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, bool):
                raise QuestionValidationError( str(self.error['typemismatch']))
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = data
        return self

@dataclass
class QuestionTypeDatetime(QuestionTypePlain):
    response: datetime | None = None
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'typemismatch': LocalizedText('Expected response of type date/time'),
    })
    def get_type_str(self) -> str:
        return 'datetime'
    def validate(self, data) -> bool:
        def is_date(value) -> bool:
            if isinstance(value, date):
                return True
            if isinstance(value, str):
                try:
                    date.fromisoformat(value)
                    return True
                except ValueError:
                    return False
            return False
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not is_date(data):
                raise QuestionValidationError( str(self.error['typemismatch']))
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = data
        return self

@dataclass
class QuestionTypeSinglePunch(QuestionTypePlain):
    response: Category | None = None
    categories: set[Category] = field(default_factory=set)
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'notfromresplist': LocalizedText('{resp} is not a valid category'),
    })
    def get_type_str(self) -> str:
        return 'singlepunch'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, str) or data not in set(cat.name for cat in self.categories):
                raise QuestionValidationError( str(self.error['notfromresplist']).format(resp=repr(data)) )
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            self.response = next(iter(set(cat for cat in self.categories if cat.name==data)))
        return self

@dataclass
class QuestionTypeMultiPunch(QuestionTypePlain):
    response: set[Category] | None = None # field(default_factory=set)
    categories: set[Category] = field(default_factory=set)
    validation: Callable | None = None
    error: dict[str,LocalizedText] = field(default_factory=lambda: {
        'missing': LocalizedText('A response is required'),
        'notfromresplist': LocalizedText('{resp} is not a valid category'),
    })
    def get_type_str(self) -> str:
        return 'multipunch'
    def validate(self, data) -> bool:
        if self.is_required and data is None:
            raise QuestionValidationError( str(self.error['missing']))
        if data is not None:
            if not isinstance(data, list):
                raise QuestionValidationError( str(self.error['notfromresplist']).format(resp=repr(data)) )
            def find_cat(d):
                d = d.strip()
                matching = [ c for c in self.categories if c.name==d ]
                if len(matching) > 0:
                    return next(iter(matching))
                else:
                    raise QuestionValidationError(str(self.error['notfromresplist']).format(resp=repr(d)))
            data = [ find_cat(d) for d in data ]
            if self.validation is not None:
                if not self.validation(data):
                    raise QuestionValidationError('Validation failed')
        if not self._validate_helper_fields(data.get('HelperFields', {})):
            raise QuestionValidationError('Validation in helper fields failed')
        return True
    def assign(self, data) -> Question:
        if not self.validate(data):
            raise QuestionValidationError('Validation failed')
        if data is not None:
            def find_cat(d):
                d = d.strip()
                matching = [ c for c in self.categories if c.name==d ]
                if len(matching) > 0:
                    return next(iter(matching))
                else:
                    raise QuestionValidationError(str(self.error['notfromresplist']).format(resp=repr(d)))
            data = set( find_cat(d) for d in data )
            self.response = data
        return self


