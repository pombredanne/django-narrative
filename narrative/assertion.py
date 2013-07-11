import abc
import copy
import datetime

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.mail import EmailMultiAlternatives

from .models import Issue, ModelIssue, IssueStatusType, IssueResolutionStepActionType


### misc utility methods ###
def blast_email(subject, message_txt, message_html, recipients):
    email = EmailMultiAlternatives(
        subject, message_txt, settings.NARRATIVE_REPLY_EMAIL_ADDRESS,
        recipients, headers={'Reply-To': settings.NARRATIVE_REPLY_EMAIL_ADDRESS})

    if message_html:
        email.attach_alternative(message_html, 'text/html')

    email.send()


class Assertion(object):
    """
    The assertion class is used for making
    assertions about properties of the system.
    If an assertion is violated, it attempts
    to fix the problem by calling any provided
    diagnostic methods.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, assertion_meta):
        self.assertion_meta = assertion_meta
        self.current_issue = None

    @abc.abstractmethod
    def check(self):
        pass

    ### Diagnostic related methods ###
    def diagnose(self, *args, **kwargs):
        """
        Run diagnostic cases and find all potential solutions.
        If there are more than one solutions, log them and notify
        the someone.
        If there are no solutions found, notify someone.
        If one solution is found, apply it.
        """
        current_issue = kwargs.pop('current_issue')
        # Get all diagnostic results
        resolution_steps = [
            getattr(self, diagnostic_case_name)(current_issue, *args, **kwargs)
            for diagnostic_case_name in self.diagnostic_cases
        ]

        # Filter out any 'None' results
        resolution_steps = filter(bool, resolution_steps)

        # Save all of the proposed resolution steps
        for irs in resolution_steps:
            if irs.solution:
                # Now this is pretty weird; the solution is an unsaved model;
                # I don't understand why, but after we save he solution,
                # we need to re-reference it before we save the thing pointing
                # to the solution.
                # Is this a bug in Django or am I doing something incredibly wrong and subtle?
                soln = irs.solution
                soln.save()
                irs.solution = soln

            irs.issue = current_issue
            irs.save()

        if len(resolution_steps) == 0:
            # No solution found, notify the admins
            message = 'Failed Assertion: {0} ({1}) has no proposed solutions'.format(
                self.assertion_meta.display_name, self.__class__.__name__)

            self.do_defer_to_admins('Failed assertion; No solutions found', message)
        elif len(resolution_steps) > 1:
            # Multiple solutions found; record them and, notify the admins
            current_issue.status = IssueStatusType.IMPASSE
            current_issue.save()

            self.do_defer_multiple_solutions_to_admins(resolution_steps)
        else:
            # Found a single proposed resolution step; if the step is to do something, do it
            diagnosis = resolution_steps[0]

            if IssueResolutionStepActionType.EXEC == diagnosis.action_type:
                self.execute_solution(diagnosis.solution)

            current_issue.status = IssueStatusType.SOLUTION_APPLIED
            current_issue.save()

    def post_recovery_cleanup(self):
        """
        Perform any cleanup actions needed after
        this assertion begins passing again.
        """
        pass

    def build_unresolved_issue_queryset(self, *args, **kwargs):
        return Issue.objects.filter(
            failed_assertion=self.assertion_meta).exclude(status=IssueStatusType.RESOLVED)

    def create_issue(self, *args, **kwargs):
        return Issue.objects.create(
            failed_assertion=self.assertion_meta)

    def check_and_diagnose(self, *args, **kwargs):
        """
        Check and diagnose this assertion for these parameters.
        """
        unresolved_issue_queryset = self.build_unresolved_issue_queryset(
            *args, **kwargs)

        if self.check(*args, **kwargs):
            # Everything is currently okay
            if unresolved_issue_queryset.exists():
                # This assertion just started passing.
                # Close any open issues and do any needed clean up.
                unresolved_issue_queryset.update(status=IssueStatusType.RESOLVED)

                self.post_recovery_cleanup(*args, **kwargs)

            return True
        else:
            # Something's wrong
            if unresolved_issue_queryset.exists():
                # Issue alredy exists
                current_issue = unresolved_issue_queryset[0]
            else:
                # No issue yet exists; create one
                current_issue = self.create_issue(*args, **kwargs)

            kwargs['current_issue'] = current_issue

            # Try to fix the issue
            self.diagnose(*args, **kwargs)

            return False

    @property
    def diagnostic_cases(self):
        """
        Get all diagnostic case methods.
        """
        return [
            member_name for member_name in dir(self)
            if member_name.startswith('diagnostic_case_') and
            callable(getattr(self, member_name))
        ]

    ### Misc utilties for working with solutions ###
    def get_action_handler(self, action_name):
        return 'do_{0}'.format(action_name)

    def validate_solution(self, solution):
        """"
        Examin all of the steps in a solution and verify
        that they are supported by this Assertion.

        If they are not, notify the admins that a bad solution
        was generated.
        """
        for step in solution.plan:
            action, kwargs = step

            if not hasattr(self, self.get_action_handler(action)):
                self.do_defer_to_admins('Invalid solution: {0}'.format(str(solution)))
                return False

        else:
            return True

    def get_utc_now(self):
        return datetime.datetime.utcnow()

    def execute_solution(self, solution):
        """
        Validate a solution, then step through and execute each of it's steps.
        """
        if self.validate_solution(solution):
            for step in solution.plan:
                action, kwargs = step

                getattr(self, self.get_action_handler(action))(**kwargs)

            solution.enacted = self.get_utc_now()
            solution.save()

    ### do_* methods for executing particular operations such as notifying individuals ###
    def do_defer_to_admins(self, subject, message, message_html=None):
        admin_group = Group.objects.get(name=settings.NARRATIVE_ADMIN_GROUP_NAME)
        admins = admin_group.user_set.all()

        admin_emails = [admin.email for admin in admins]

        blast_email(subject, message, message_html, admin_emails)

    def do_defer_multiple_solutions_to_admins(self, solutions):
        subject = 'Impasse: "{0}" has Multiple solutions proposed'.format(
            self.assertion_meta.display_name)

        message = 'Assertion: {0} ({1}) has {2} proposed solutions'.format(
            self.assertion_meta.display_name, self.__class__.__name__, len(solutions))

        hints = map(str, solutions)

        message += '\n'.join(hints)

        message_html = message

        self.do_defer_to_admins(subject, message, message_html)

    def do_email(self, address, subject, message_txt, message_html):
        blast_email(subject, message_txt, message_html, [address])


class ModelAssertion(Assertion):
    """
    ModelAssertion is a class for making assertions about
    a particular set of models.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        super(ModelAssertion, self).__init__(*args, **kwargs)

    @abc.abstractproperty
    def queryset(self):
        """
        Return the queryset of records to check.
        """
        pass

    @abc.abstractmethod
    def check_record(self, record):
        pass

    def check(self, *args, **kwargs):
        return self.check_record(kwargs.pop('record'))

    def build_unresolved_issue_queryset(self, *args, **kwargs):
        """
        We override this to query for Model Issues instead of
        just Issues like the base Assertion class.
        """
        record = kwargs.pop('record')

        return ModelIssue.objects.filter(
            failed_assertion=self.assertion_meta,
            model_type__model=record.__class__.__name__.lower(),
            model_id=record.id).exclude(status=IssueStatusType.RESOLVED)

    def create_issue(self, *args, **kwargs):
        """
        We override this to create Model Issues instead of
        just Issues like the base Assertion class.
        """
        record = kwargs.pop('record')

        return ModelIssue.objects.create(
            failed_assertion=self.assertion_meta,
            model=record)

    def check_and_diagnose(self, *args, **kwargs):
        """
        ModelAssertion is kind of funny; all of the logic of
        the base Assertion class needs to be ran, but for a particular
        record.  So that's exactly what we do.
        """
        for record in self.queryset:
            # For each record
            args_copy = copy.copy(args)
            kwargs_copy = copy.copy(kwargs)
            kwargs_copy['record'] = record

            super(ModelAssertion, self).check_and_diagnose(*args_copy, **kwargs_copy)
