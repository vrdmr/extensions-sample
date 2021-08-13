import json
import enum
from typing import Dict, List
from logging import Logger

from azure.functions import FuncExtensionBase, Context
from azure.functions.http import HttpRequest

class QueryparamType(enum.Enum):
    String = 1
    Int = 2

    @classmethod
    def validate(cls, type_: 'QueryparamType', input_) -> bool:
        if type_ == cls.String:
            return cls._is_string(input_)
        if type_ == cls.Int:
            return cls._is_int(input_)
        return False

    @classmethod
    def _is_string(cls, input_) -> bool:
        return isinstance(input_, str)

    @classmethod
    def _is_int(cls, input_) -> bool:
        return isinstance(input_, str) and input_.isnumeric()

class PythonExtensionValidator(FuncExtensionBase):
    """A Python worker extension to record elapsed time in a function invocation
    """
    def __init__(self, file_path: str, validate: Dict[str, QueryparamType]):
        super().__init__(file_path)
        self._validator = validate

    def pre_invocation(self, logger: Logger, context: Context, func_args: Dict[str, object], *args, **kwargs) -> None:
        http_args: List[HttpRequest] = [obj for obj in func_args.values() if isinstance(obj, HttpRequest)]
        if not http_args:
            logger.warning(f'No HttpTrigger argument in {self._trigger_name}')

        error_messages = []
        setattr(context, 'is_valid', True)
        for key, qp_type in self._validator.items():
            setattr(context, key, None)
            value = http_args[0].params.get(key)

            if not value:
                logger.warning(f"'{key}' is not found in the query param")
                error_messages.append(f"'{key}' is not found in the query param")

                setattr(context, 'is_valid', False)
                continue

            if not QueryparamType.validate(qp_type, value):
                logger.warning(f"'{key}' expects to be {qp_type} in the query param, but it does not match!")
                error_messages.append(f"'{key}' expects to be {qp_type} in the query param, but it does not match!")

                setattr(context, 'is_valid', False)
                continue

            if qp_type is QueryparamType.String:
                setattr(context, key, str(value))
            elif qp_type is QueryparamType.Int:
                setattr(context, key, int(value))

        setattr(context, 'error_messages', json.dumps(error_messages))
