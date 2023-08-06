import abc
import datetime
import sys
import traceback
from io import StringIO


class Result(object):
    @property
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


class ContextViewModel(object):
    def __init__(self, context):
        self.name = context.name
        self.assertions = []
        self._exception = None
        self.error_summary = None

    @property
    def exception(self):
        return self._exception
    @exception.setter
    def exception(self, value):
        self._exception = value
        self.error_summary = format_exception(value)

    @property
    def assertion_failures(self):
        return [a for a in self.assertions if a.status == "failed"]
    @property
    def assertion_errors(self):
        return [a for a in self.assertions if a.status == "errored"]


class AssertionViewModel(object):
    def __init__(self, assertion, status="passed", exception=None):
        self.name = assertion.name
        self.status = status
        self.error_summary = None
        if exception is not None:
            self.error_summary = format_exception(exception)


class SimpleResult(Result):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.view_models = []

    @property
    def failed(self):
        return self.context_errors or self.assertion_errors or self.assertion_failures
    @property
    def assertions(self):
        return [a for vm in self.view_models for a in vm.assertions]
    @property
    def assertion_failures(self):
        return [a for a in self.assertions if a.status == "failed"]
    @property
    def assertion_errors(self):
        return [a for a in self.assertions if a.status == "errored"]
    @property
    def contexts(self):
        return self.view_models
    @property
    def context_errors(self):
        return [vm for vm in self.view_models if vm.error_summary is not None]

    def context_started(self, context):
        super().context_started(context)
        self.view_models.append(ContextViewModel(context))

    def context_errored(self, context, exception):
        context_vm = self.view_models[-1]
        context_vm.exception = exception
        super().context_errored(context, exception)

    def assertion_passed(self, assertion):
        context_vm = self.view_models[-1]
        assertion_vm = AssertionViewModel(assertion)
        context_vm.assertions.append(assertion_vm)
        super().assertion_passed(assertion)

    def assertion_failed(self, assertion, exception):
        context_vm = self.view_models[-1]
        assertion_vm = AssertionViewModel(assertion, "failed", exception)
        context_vm.assertions.append(assertion_vm)
        super().assertion_failed(assertion, exception)

    def assertion_errored(self, assertion, exception):
        context_vm = self.view_models[-1]
        assertion_vm = AssertionViewModel(assertion, "errored", exception)
        context_vm.assertions.append(assertion_vm)
        super().assertion_errored(assertion, exception)


class StreamResult(Result):
    def __init__(self, stream=sys.stderr):
        super().__init__()
        self.stream = stream

    def _print(self, *args, sep=' ', end='\n', flush=True):
        print(*args, sep=sep, end=end, file=self.stream, flush=flush)


class DotsResult(StreamResult):
    def assertion_passed(self, *args, **kwargs):
        super().assertion_passed(*args, **kwargs)
        self._print('.', end='')

    def assertion_failed(self, *args, **kwargs):
        super().assertion_failed(*args, **kwargs)
        self._print('F', end='')

    def assertion_errored(self, *args, **kwargs):
        super().assertion_errored(*args, **kwargs)
        self._print('E', end='')

    def context_errored(self, *args, **kwargs):
        super().context_errored(*args, **kwargs)
        self._print('E', end='')


class SummarisingResult(SimpleResult, StreamResult):
    dashes = '-' * 70

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.summary = []
        self.current_indent = ''

    def context_started(self, context):
        super().context_started(context)
        self.current_summary = [context.name]
        self.indent()

    def context_ended(self, context):
        super().context_ended(context)
        context_vm = self.view_models[-1]
        if context_vm.assertion_failures or context_vm.assertion_errors:
            self.add_current_context_to_summary()
        self.dedent()

    def context_errored(self, context, exception):
        super().context_errored(context, exception)
        context_vm = self.view_models[-1]
        formatted_exc = ''.join(context_vm.error_summary).strip().split('\n')
        self.extend_summary(formatted_exc)
        self.add_current_context_to_summary()
        self.dedent()

    def assertion_started(self, assertion):
        super().assertion_started(assertion)

    def assertion_failed(self, assertion, exception):
        super().assertion_failed(assertion, exception)
        self.add_current_assertion_to_summary()

    def assertion_errored(self, assertion, exception):
        super().assertion_errored(assertion, exception)
        self.add_current_assertion_to_summary()

    def suite_ended(self, suite):
        super().suite_ended(suite)
        self.summarise()

    def indent(self):
        self.current_indent += '  '

    def dedent(self):
        self.current_indent = self.current_indent[:-2]

    def append_to_summary(self, string):
        self.current_summary.append(self.current_indent + string)

    def extend_summary(self, iterable):
        self.current_summary.extend(self.current_indent + s for s in iterable)

    def add_current_context_to_summary(self):
        self.summary.extend(self.current_summary)

    def summarise(self):
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
        num_ctx = len(self.view_models)
        num_ass = len(self.assertions)
        msg = "{}, {}".format(pluralise("context", num_ctx), pluralise("assertion", num_ass))
        return msg

    def failure_numbers(self):
        num_ctx = len(self.view_models)
        num_ass = len(self.assertions)
        num_ctx_err = len(self.context_errors)
        num_fail = len(self.assertion_failures)
        num_err = len(self.assertion_errors)
        msg =  "{}, {}: {} failed, {}".format(
            pluralise("context", num_ctx),
            pluralise("assertion", num_ass),
            num_fail,
            pluralise("error", num_err + num_ctx_err))
        return msg

    def add_current_assertion_to_summary(self):
        context_vm = self.view_models[-1]
        assertion_vm = context_vm.assertions[-1]
        formatted_exc = ''.join(assertion_vm.error_summary).strip().split('\n')
        
        if assertion_vm.status == "errored":
            self.append_to_summary('ERROR: ' + assertion_vm.name)
        elif assertion_vm.status == "failed":
            self.append_to_summary('FAIL: ' + assertion_vm.name)

        self.indent()
        self.extend_summary(formatted_exc)
        self.dedent()


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
        if self.buffer.getvalue():
            self.summary.append("  -------------------- >> begin captured stdout << -------------------")
            lines = self.buffer.getvalue().strip().split('\n')
            self.summary.extend('  ' + line for line in lines)
            self.summary.append("  --------------------- >> end captured stdout << --------------------")

    def assertion_failed(self, assertion, exception):
        super().assertion_failed(assertion, exception)
        if self.buffer.getvalue():
            self.current_summary.append("    ------------------- >> begin captured stdout << ------------------")
            lines = self.buffer.getvalue().strip().split('\n')
            self.current_summary.extend('    ' + line for line in lines)
            self.current_summary.append("    -------------------- >> end captured stdout << -------------------")

    def assertion_errored(self, assertion, exception):
        super().assertion_errored(assertion, exception)
        if self.buffer.getvalue():
            self.current_summary.append("    ------------------- >> begin captured stdout << ------------------")
            lines = self.buffer.getvalue().strip().split('\n')
            self.current_summary.extend('    ' + line for line in lines)
            self.current_summary.append("    -------------------- >> end captured stdout << -------------------")


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


class NonCapturingCLIResult(DotsResult, TimedResult, SummarisingResult):
    pass


class CapturingCLIResult(NonCapturingCLIResult, CapturingResult):
    pass


def format_exception(exception):
    ret = traceback.format_exception(type(exception), exception, exception.__traceback__)
    exception.__traceback__ = None
    return ret


def pluralise(noun, num):
    string = str(num) + ' ' + noun
    if num != 1:
        string += 's'
    return string
