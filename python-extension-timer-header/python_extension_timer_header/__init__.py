import typing
from logging import Logger
from time import time
from tracemalloc import start, take_snapshot, Snapshot

from azure.functions import AppExtensionBase, Context, HttpResponse

class PythonExtensionTimerHeader(AppExtensionBase):
    """A Python worker extension to record elapsed time in a function invocation
    """

    @classmethod
    def init(cls):
        # This records the starttime of each function
        cls.start_timestamps: typing.Dict[str, float] = {}
        cls.start_snapshots: typing.Dict[str, Snapshot] = {}
        cls.append_to_http_response = False
        start()

    @classmethod
    def configure(cls, *args, append_to_http_response:bool=False, **kwargs):
        # Customer can use TimerExtension.configure(append_to_http_response=)
        # to decide whether the elaspsed time should be shown in HTTP response
        cls.append_to_http_response = append_to_http_response

    @classmethod
    def pre_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        *args, **kwargs
    ) -> None:
        logger.info(f'Recording start time of {context.function_name}')
        cls.start_timestamps[context.invocation_id] = time()
        cls.start_snapshots[context.invocation_id] = take_snapshot()

    @classmethod
    def post_invocation_app_level(
        cls, logger: Logger, context: Context,
        func_args: typing.Dict[str, object],
        func_ret: typing.Optional[object],
        *args, **kwargs
    ) -> None:
        if context.invocation_id not in cls.start_timestamps:
            raise RuntimeError(f'invocation_id {context.invocation_id} is not found in timestamps')

        if context.invocation_id not in cls.start_snapshots:
            raise RuntimeError(f'invocation_id {context.invocation_id} is not found in snapshots')

        # Get the start_snapshot of the invocation
        start_snapshots: Snapshot = cls.start_snapshots.pop(context.invocation_id)
        end_snapshot: Snapshot = take_snapshot()

        # Get the start_time of the invocation
        start_time: float = cls.start_timestamps.pop(context.invocation_id)
        end_time: float = time()

        # Calculate the elaspsed time
        elapsed_time = end_time - start_time
        logger.info(f'Time taken to execute {context.function_name} is {elapsed_time} sec')

        # Append the elaspsed time to the end of HTTP response
        # if the append_to_http_response is set to True
        top_stats = end_snapshot.compare_to(start_snapshots, 'filename')

        if cls.append_to_http_response and isinstance(func_ret, HttpResponse):
            func_ret._HttpResponse__body += f'\n(TimeElapsed: {elapsed_time} sec)'.encode()
            for index, stat in enumerate(top_stats[:5]):
                func_ret._HttpResponse__body += f'\n(Top Memory Usage[{index+1}]: {stat}'.encode()
