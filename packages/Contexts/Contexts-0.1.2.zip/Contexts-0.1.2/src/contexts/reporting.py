import abc
import datetime
import sys
import traceback
from io import StringIO


class Result(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def failed(self):
        return True

    def suite_started(self, suite):
        """Called at the beginning of a test run"""

    def suite_ended(self, suite):
        """Called at the end of a test run"""

    def context_started(self, context):
        """Called when a test context begins its run"""

    def context_ended(self, context):
        """Called when a test context completes its run"""

    def context_errored(self, context, exception):
        """Called when a test context (not an assertion) throws an exception"""

    def assertion_started(self, assertion):
        """Called when an assertion begins"""

    def assertion_passed(self, assertion):
        """Called when an assertion passes"""

    def assertion_errored(self, assertion, exception):
        """Called when an assertion throws an exception"""

    def assertion_failed(self, assertion, exception):
        """Called when an assertion throws an AssertionError"""


class SimpleResult(Result):
    def __init__(self):
        self.contexts = []
        self.assertions = []
        self.context_errors = []
        self.assertion_errors = []
        self.assertion_failures = []
        super().__init__()

    @property
    def failed(self):
        return self.context_errors or self.assertion_errors or self.assertion_failures

    def assertion_started(self, assertion):
        self.assertions.append(assertion)
        super().assertion_started(assertion)

    def assertion_failed(self, assertion, exception):
        self.assertion_failures.append((assertion, exception))
        exception.__traceback__ = None
        super().assertion_failed(assertion, exception)

    def assertion_errored(self, assertion, exception):
        self.assertion_errors.append((assertion, exception))
        exception.__traceback__ = None
        super().assertion_errored(assertion, exception)

    def context_started(self, context):
        self.contexts.append(context)
        super().context_started(context)

    def context_errored(self, context, exception):
        self.context_errors.append((context, exception))
        exception.__traceback__ = None
        super().context_errored(context, exception)


class StreamResult(SimpleResult):
    def __init__(self, stream=sys.stderr):
        self.stream = stream
        super().__init__()

    def _print(self, *args, sep=' ', end='\n', flush=True):
        print(*args, sep=sep, end=end, file=self.stream, flush=flush)


class DotsResult(StreamResult):
    def assertion_passed(self, *args, **kwargs):
        self._print('.', end='')
        super().assertion_passed(*args, **kwargs)

    def assertion_failed(self, *args, **kwargs):
        self._print('F', end='')
        super().assertion_failed(*args, **kwargs)

    def assertion_errored(self, *args, **kwargs):
        self._print('E', end='')
        super().assertion_errored(*args, **kwargs)

    def context_errored(self, *args, **kwargs):
        self._print('E', end='')
        super().context_errored(*args, **kwargs)


class SummarisingResult(StreamResult):
    dashes = '-' * 70
    equalses = '=' * 70

    def __init__(self, *args, **kwargs):
        self.summary = []
        super().__init__(*args, **kwargs)

    def suite_ended(self, suite):
        super().suite_ended(suite)
        self.summarise()

    def assertion_failed(self, assertion, exception):
        self.summary.extend(self.format_failure(assertion, exception, "FAIL"))
        super().assertion_failed(assertion, exception)

    def assertion_errored(self, assertion, exception):
        self.summary.extend(self.format_failure(assertion, exception, "ERROR"))
        super().assertion_errored(assertion, exception)

    def context_errored(self, context, exception):
        self.summary.extend(self.format_failure(context, exception, "ERROR"))
        super().context_errored(context, exception)

    def summarise(self):
        self._print('')
        if self.failed:
            self._print('\n'.join(self.summary))
        self._print(self.dashes)
        if self.failed:
            self._print('FAILED!')
            self._print(self.failure_numbers())
        else:
            self._print('PASSED!')
            self._print(self.success_numbers())

    def format_failure(self, assertion, exception, word):
        formatted = [
            self.equalses,
            "{}: {}".format(word, assertion.name),
            self.dashes
        ]
        formatted.extend(s[:-1] for s in traceback.format_exception(type(exception), exception, exception.__traceback__))
        return formatted

    def success_numbers(self):
        num_ctx = len(self.contexts)
        num_ass = len(self.assertions)
        msg = "{}, {}".format(pluralise("context", num_ctx), pluralise("assertion", num_ass))
        return msg

    def failure_numbers(self):
        num_ctx = len(self.contexts)
        num_ass = len(self.assertions)
        num_ctx_err = len(self.context_errors)
        num_fail = len(self.assertion_failures)
        num_err = len(self.assertion_errors)
        msg =  "{}, {}: {} failed, {}".format(pluralise("context", num_ctx),
           pluralise("assertion", num_ass),
           num_fail,
           pluralise("error", num_err + num_ctx_err))
        return msg


def pluralise(noun, num):
    string = str(num) + ' ' + noun
    if num != 1:
        string += 's'
    return string


class ContextViewModel(object):
    def __init__(self, context):
        self.name = context.name
        self.assertion_failures = []
        self.assertion_errors = []
        self._exception = None
        self.error_summary = None

    @property
    def exception(self):
        return self._exception
    @exception.setter
    def exception(self, value):
        self._exception = value
        self.error_summary = traceback.format_exception(type(value), value, value.__traceback__)

class AssertionViewModel(object):
    def __init__(self, assertion, exception):
        self.name = assertion.name
        self.error_summary = traceback.format_exception(type(exception), exception, exception.__traceback__)


class HierarchicalResult(StreamResult):
    dashes = '-' * 70

    def __init__(self, *args, **kwargs):
        self.summary = []
        self.view_models = []
        super().__init__(*args, **kwargs)

    def suite_ended(self, suite):
        super().suite_ended(suite)
        self.summarise()

    def context_started(self, context):
        self.view_models.append(ContextViewModel(context))
        super().context_started(context)

    def context_ended(self, context):
        super().context_ended(context)
        self.current_context = None

    def assertion_failed(self, assertion, exception):
        context_vm = self.view_models[-1]
        assertion_vm = AssertionViewModel(assertion, exception)
        context_vm.assertion_failures.append(assertion_vm)
        super().assertion_failed(assertion, exception)

    def assertion_errored(self, assertion, exception):
        context_vm = self.view_models[-1]
        assertion_vm = AssertionViewModel(assertion, exception)
        context_vm.assertion_errors.append(assertion_vm)
        super().assertion_errored(assertion, exception)

    def context_errored(self, context, exception):
        context_vm = self.view_models[-1]
        context_vm.exception = exception
        super().context_errored(context, exception)

    def summarise(self):
        for context_vm in self.view_models:
            if not context_vm.error_summary and not context_vm.assertion_errors and not context_vm.assertion_failures:
                continue
            self.summary.append(context_vm.name)
            for assertion_vm in context_vm.assertion_errors:
                formatted_exc = ''.join(assertion_vm.error_summary).split('\n')[:-1]
                self.summary.append('  ERROR: ' + assertion_vm.name)
                self.summary.extend('    ' + s for s in formatted_exc)
            for assertion_vm in context_vm.assertion_failures:
                formatted_exc = ''.join(assertion_vm.error_summary).split('\n')[:-1]
                self.summary.append('  FAIL: ' + assertion_vm.name)
                self.summary.extend('    ' + s for s in formatted_exc)
            if context_vm.error_summary:
                formatted_exc = ''.join(context_vm.error_summary).split('\n')[:-1]
                self.summary.extend('  ' + s for s in formatted_exc)

        self._print('')
        self._print(self.dashes)
        if self.failed:
            self._print('\n'.join(self.summary))
            self._print(self.dashes)
            self._print('FAILED!')
            self._print(self.failure_numbers())
        else:
            self._print('PASSED!')
            self._print(self.success_numbers())

    def success_numbers(self):
        num_ctx = len(self.contexts)
        num_ass = len(self.assertions)
        msg = "{}, {}".format(pluralise("context", num_ctx), pluralise("assertion", num_ass))
        return msg

    def failure_numbers(self):
        num_ctx = len(self.contexts)
        num_ass = len(self.assertions)
        num_ctx_err = len(self.context_errors)
        num_fail = len(self.assertion_failures)
        num_err = len(self.assertion_errors)
        msg =  "{}, {}: {} failed, {}".format(pluralise("context", num_ctx),
           pluralise("assertion", num_ass),
           num_fail,
           pluralise("error", num_err + num_ctx_err))
        return msg


class TimedResult(StreamResult):
    def suite_started(self, suite):
        super().suite_started(suite)
        self.start_time = datetime.datetime.now()

    def suite_ended(self, suite):
        self.end_time = datetime.datetime.now()
        super().suite_ended(suite)

        total_secs = (self.end_time - self.start_time).total_seconds()
        rounded = round(total_secs, 1)
        self._print("({} seconds)".format(rounded))


class CapturingResult(SummarisingResult):
    def context_started(self, context):
        super().context_started(context)
        self.real_stdout = sys.stdout
        self.buffer = StringIO()
        sys.stdout = self.buffer

    def context_ended(self, context):
        sys.stdout = self.real_stdout
        super().context_ended(context)

    def context_errored(self, context, exception):
        sys.stdout = self.real_stdout
        super().context_errored(context, exception)
        self.append_buffer_to_summary()

    def assertion_failed(self, assertion, exception):
        super().assertion_failed(assertion, exception)
        self.append_buffer_to_summary()

    def assertion_errored(self, assertion, exception):
        super().assertion_errored(assertion, exception)
        self.append_buffer_to_summary()

    def append_buffer_to_summary(self):
        if self.buffer.getvalue():
            self.summary.append("-------------------- >> begin captured stdout << ---------------------")
            self.summary.append(self.buffer.getvalue()[:-1])
            self.summary.append("--------------------- >> end captured stdout << ----------------------")


class NonCapturingCLIResult(DotsResult, TimedResult, SummarisingResult):
    pass


class CLIResult(CapturingResult, NonCapturingCLIResult):
    pass

class HierarchicalCLIResult(DotsResult, TimedResult, HierarchicalResult):
    pass
