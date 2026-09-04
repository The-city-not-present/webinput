from dataclasses import dataclass, field

from .question_types import (
    Question,
    Category,
    QuestionInternalError,
    QuestionTypeBlock,
    QuestionTypeLoop,
)
# from collections.abc import Iterable
import copy


def validate_names(fields):
    if not all(f._validate_name() for f in fields):
        raise QuestionInternalError('name validation failed')
    names = [f.name for f in fields]
    if len(names) != len(set(names)):
        raise QuestionInternalError('name validation failed')
    return True


def json_schema_items_ordered(fields: dict) -> dict:
    return {
        f_name: {
            **f_obj,
            "x-ui": {
                **f_obj.get("x-ui",{}),
                "order": i,
            },
        } for i, (f_name, f_obj) in enumerate(fields.items())
    }


def make_validation_rules(question):
    return None # TODO:





def question_to_schema(question_instance: Question) -> dict:
    def transform_helperfield_name(question_instance):
        question = copy.copy(question_instance)
        question.name = f'helperfields.{question.name}'
        return question
    @dataclass
    class CategoryElementClass(Question):
        category: Category = field(kw_only=True)
        fields: list[Question] = field(kw_only=True)
        def get_type_str(self) -> str:
            return 'iteration'

    question = copy.copy(question_instance) # for safety, to not occasionally modify

    if hasattr(question, 'fields') and question.fields:
        validate_names(question.fields)
    if hasattr(question, 'helper_fields') and question.helper_fields:
        validate_names(question.helper_fields)

    if isinstance(question, CategoryElementClass):
        result = {
            "type": "object",
            "title": question.category.label,
            "properties": {
                f.name: question_to_schema(f) for f in question.fields
            },
            "x-ui": {
                **{key: value for mod in question.modifiers for key, value in mod.as_json().items()},
            },
            "x-properties": question.properties,
        }
        result = json_schema_items_ordered(result)
        return result

    # make up the fields
    question_fields = []
    if isinstance(question, QuestionTypeBlock):
        # if block
        question_fields = question.fields
    elif isinstance(question, QuestionTypeLoop):
        # if loop
        question_fields = [
            CategoryElementClass(
                name = cat.name,
                label = cat.label,
                properties = cat.properties,
                modifiers = cat.modifiers,
                widget = None,
                helper_fields = {},
                category = cat,
                fields = question.fields,
            ) for cat in question.iterations
        ]
    elif hasattr(question, 'fields') and question.fields:
        # if other - hmm, I don't have anything other in design
        raise QuestionInternalError('Unrecognized question type: has "fields" attr but is not block or loop')

    if hasattr(question, 'helper_fields') and question.helper_fields:
        question_fields.extend([transform_helperfield_name(f) for f in question.helper_fields])

    result = {
        "type": "object" if not question.is_plain else question.get_type_str(),
        "title": question.label,
        "properties": {
            f.name: question_to_schema(f) for f in question_fields
        },
        "x-validation-rules": make_validation_rules(question),
        "x-widget": question.widget,
        "x-ui": {
            **{ key: value for mod in question.modifiers for key, value in mod.as_json().items() },
        },
        "x-properties": question.properties,
    }
    result = json_schema_items_ordered(result)
    return result
