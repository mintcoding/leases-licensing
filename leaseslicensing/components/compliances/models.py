from __future__ import unicode_literals

import json
import datetime
from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.core.exceptions import ValidationError

# from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from ledger_api_client.ledger_models import EmailUserRO as EmailUser
from leaseslicensing.ledger_api_utils import retrieve_email_user
from leaseslicensing import exceptions
from leaseslicensing.components.main.models import (
    CommunicationsLogEntry,
    UserAction,
    Document,
    RevisionedMixin,
)
from leaseslicensing.components.proposals.models import (
    ProposalRequirement,
    AmendmentReason,
)
from leaseslicensing.components.compliances.email import (
    send_compliance_accept_email_notification,
    send_amendment_email_notification,
    send_reminder_email_notification,
    send_external_submit_email_notification,
    send_submit_email_notification,
    send_internal_reminder_email_notification,
    send_due_email_notification,
    send_internal_due_email_notification,
    send_notification_only_email,
    send_internal_notification_only_email,
)
from ledger_api_client.ledger_models import Invoice

import logging

logger = logging.getLogger(__name__)


class Compliance(models.Model):
    # class Compliance(RevisionedMixin):

    PROCESSING_STATUS_CHOICES = (
        ("due", "Due"),
        ("future", "Future"),
        ("with_assessor", "With Assessor"),
        ("approved", "Approved"),
        ("discarded", "Discarded"),
    )

    CUSTOMER_STATUS_CHOICES = (
        ("due", "Due"),
        ("future", "Future"),
        ("with_assessor", "Under Review"),
        ("approved", "Approved"),
        ("discarded", "Discarded"),
    )

    lodgement_number = models.CharField(max_length=9, blank=True, default="")
    proposal = models.ForeignKey(
        "leaseslicensing.Proposal", related_name="compliances", on_delete=models.CASCADE
    )
    approval = models.ForeignKey(
        "leaseslicensing.Approval", related_name="compliances", on_delete=models.CASCADE
    )
    due_date = models.DateField()
    text = models.TextField(blank=True)
    # meta = JSONField(null=True, blank=True)
    num_participants = models.SmallIntegerField(
        "Number of participants", blank=True, null=True
    )
    processing_status = models.CharField(
        choices=PROCESSING_STATUS_CHOICES, max_length=20
    )
    customer_status = models.CharField(
        choices=CUSTOMER_STATUS_CHOICES,
        max_length=20,
        default=CUSTOMER_STATUS_CHOICES[1][0],
    )
    # assigned_to = models.ForeignKey(EmailUser,related_name='leaseslicensing_compliance_assignments',null=True,blank=True, on_delete=models.SET_NULL)
    assigned_to = models.IntegerField(null=True)  # EmailUserRO
    requirement = models.ForeignKey(
        ProposalRequirement,
        blank=True,
        null=True,
        related_name="compliance_requirement",
        on_delete=models.SET_NULL,
    )
    lodgement_date = models.DateTimeField(blank=True, null=True)
    # submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='leaseslicensing_compliances', on_delete=models.SET_NULL)
    submitter = models.IntegerField(null=True)  # EmailUserRO
    reminder_sent = models.BooleanField(default=False)
    post_reminder_sent = models.BooleanField(default=False)
    fee_invoice_reference = models.CharField(
        max_length=50, null=True, blank=True, default=""
    )

    class Meta:
        app_label = "leaseslicensing"

    @property
    def approval_number(self):
        return self.approval.lodgement_number if self.approval else ""

    @property
    def title(self):
        return self.proposal.title

    @property
    def holder(self):
        return self.proposal.applicant

    @property
    def reference(self):
        # return 'C{0:06d}'.format(self.id)
        return self.lodgement_number

    @property
    def allowed_assessors(self):
        return self.proposal.compliance_assessors

    @property
    def can_user_view(self):
        """
        :return: True if the compliance is not in the editable status for external user.
        """
        return (
            self.customer_status == "with_assessor"
            or self.customer_status == "approved"
        )

    @property
    def can_process(self):
        """
        :return: True if the compliance is ready for assessment.
        """
        return self.processing_status == "with_assessor"

    @property
    def amendment_requests(self):
        qs = ComplianceAmendmentRequest.objects.filter(compliance=self)
        return qs

    @property
    def participant_number_required(self):
        if (
            self.requirement.standard_requirement
            and self.requirement.standard_requirement.participant_number_required
        ):
            return True
        return False

    @property
    def fee_paid(self):
        return True if self.fee_invoice_reference else False

    @property
    def fee_amount(self):
        return (
            Invoice.objects.get(reference=self.fee_invoice_reference).amount
            if self.fee_paid
            else None
        )

    def save(self, *args, **kwargs):
        super(Compliance, self).save(*args, **kwargs)
        if self.lodgement_number == "":
            new_lodgment_id = "C{0:06d}".format(self.pk)
            self.lodgement_number = new_lodgment_id
            self.save()

    def submit(self, request):
        with transaction.atomic():
            try:
                if self.processing_status == "discarded":
                    raise ValidationError(
                        "You cannot submit this compliance with requirements as it has been discarded."
                    )
                if self.processing_status == "future" or "due":
                    self.processing_status = "with_assessor"
                    self.customer_status = "with_assessor"
                    self.submitter = request.user.id

                    if request.FILES:
                        for f in request.FILES:
                            document = self.documents.create(name=str(request.FILES[f]))
                            document._file = request.FILES[f]
                            document.save()
                    if self.amendment_requests:
                        qs = self.amendment_requests.filter(status="requested")
                        if qs:
                            for q in qs:
                                q.status = "amended"
                                q.save()

                # self.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()
                self.lodgement_date = timezone.now()
                self.save(
                        #version_comment="Compliance Submitted: {}".format(self.id)
                        )
                self.proposal.save(
                    #version_comment="Compliance Submitted: {}".format(self.id)
                )
                self.log_user_action(
                    ComplianceUserAction.ACTION_SUBMIT_REQUEST.format(self.id), request
                )
                send_external_submit_email_notification(request, self)
                send_submit_email_notification(request, self)
                self.documents.all().update(can_delete=False)
            except:
                raise

    def delete_document(self, request, document):
        with transaction.atomic():
            try:
                if document:
                    doc = self.documents.get(id=document[2])
                    doc.delete()
                return self
            except:
                raise ValidationError("Document not found")

    def assign_to(self, user, request):
        with transaction.atomic():
            self.assigned_to = user
            self.save()
            self.log_user_action(
                ComplianceUserAction.ACTION_ASSIGN_TO.format(retrieve_email_user(user).get_full_name()),
                request,
            )

    def unassign(self, request):
        with transaction.atomic():
            self.assigned_to = None
            self.save()
            self.log_user_action(ComplianceUserAction.ACTION_UNASSIGN, request)

    def accept(self, request):
        with transaction.atomic():
            self.processing_status = "approved"
            self.customer_status = "approved"
            self.save()
            self.log_user_action(
                ComplianceUserAction.ACTION_CONCLUDE_REQUEST.format(self.id), request
            )
            send_compliance_accept_email_notification(self, request)

    def send_reminder(self, user):
        with transaction.atomic():
            today = timezone.localtime(timezone.now()).date()
            try:
                if self.processing_status == "due":
                    if (
                        self.due_date < today
                        and self.lodgement_date == None
                        and self.post_reminder_sent == False
                    ):
                        send_reminder_email_notification(self)
                        send_internal_reminder_email_notification(self)
                        self.post_reminder_sent = True
                        self.reminder_sent = True
                        self.save()
                        ComplianceUserAction.log_action(
                            self,
                            ComplianceUserAction.ACTION_REMINDER_SENT.format(self.id),
                            user,
                        )
                        logger.info(
                            "Post due date reminder sent for Compliance {} ".format(
                                self.lodgement_number
                            )
                        )
                    elif (
                        self.due_date >= today
                        and today >= self.due_date - datetime.timedelta(days=14)
                        and self.reminder_sent == False
                    ):
                        # second part: if today is with 14 days of due_date, and email reminder is not sent (deals with Compliances created with the reminder period)
                        print(self.id)
                        if self.requirement.notification_only:
                            send_notification_only_email(self)
                            send_internal_notification_only_email(self)
                            self.reminder_sent = True
                            self.processing_status = "approved"
                            self.customer_status = "approved"
                            self.save()
                        else:
                            send_due_email_notification(self)
                            send_internal_due_email_notification(self)
                            self.reminder_sent = True
                            self.save()
                        ComplianceUserAction.log_action(
                            self,
                            ComplianceUserAction.ACTION_REMINDER_SENT.format(self.id),
                            user,
                        )
                        logger.info(
                            "Pre due date reminder sent for Compliance {} ".format(
                                self.lodgement_number
                            )
                        )

            except Exception as e:
                logger.info(
                    "Error sending Reminder Compliance {}\n{}".format(
                        self.lodgement_number, e
                    )
                )

    def log_user_action(self, action, request):
        return ComplianceUserAction.log_action(self, action, request.user.id)

    def __str__(self):
        return self.lodgement_number


def update_proposal_complaince_filename(instance, filename):
    return "{}/proposals/{}/compliance/{}".format(
        settings.MEDIA_APP_DIR, instance.compliance.proposal.id, filename
    )


class ComplianceDocument(Document):
    compliance = models.ForeignKey(
        "Compliance", related_name="documents", on_delete=models.CASCADE
    )
    _file = models.FileField(
        upload_to=update_proposal_complaince_filename, max_length=512
    )
    can_delete = models.BooleanField(
        default=True
    )  # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ComplianceDocument, self).delete()
        logger.info(
            "Cannot delete existing document object after Compliance has been submitted (including document submitted before Compliance pushback to status Due): {}".format(
                self.name
            )
        )

    class Meta:
        app_label = "leaseslicensing"


class ComplianceUserAction(UserAction):
    ACTION_CREATE = "Create compliance {}"
    ACTION_SUBMIT_REQUEST = "Submit compliance {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_REMINDER_SENT = "Reminder sent for compliance {}"
    ACTION_STATUS_CHANGE = "Change status to Due for compliance {}"
    # Assessors

    ACTION_CONCLUDE_REQUEST = "Conclude request {}"

    @classmethod
    def log_action(cls, compliance, action, user):
        return cls.objects.create(compliance=compliance, who=user, what=str(action))

    compliance = models.ForeignKey(
        Compliance, related_name="action_logs", on_delete=models.CASCADE
    )

    class Meta:
        app_label = "leaseslicensing"


class ComplianceLogEntry(CommunicationsLogEntry):
    compliance = models.ForeignKey(
        Compliance, related_name="comms_logs", on_delete=models.CASCADE
    )

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.compliance.id
        super(ComplianceLogEntry, self).save(**kwargs)

    class Meta:
        app_label = "leaseslicensing"


def update_compliance_comms_log_filename(instance, filename):
    return "{}/proposals/{}/compliance/communications/{}".format(
        settings.MEDIA_APP_DIR, instance.log_entry.compliance.proposal.id, filename
    )


class ComplianceLogDocument(Document):
    log_entry = models.ForeignKey(
        "ComplianceLogEntry", related_name="documents", on_delete=models.CASCADE
    )
    _file = models.FileField(
        upload_to=update_compliance_comms_log_filename, max_length=512
    )

    class Meta:
        app_label = "leaseslicensing"


class CompRequest(models.Model):
    compliance = models.ForeignKey(Compliance, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    # officer = models.ForeignKey(EmailUser, null=True, on_delete=models.SET_NULL)
    officer = models.IntegerField()  # EmailUserRO

    class Meta:
        app_label = "leaseslicensing"


class ComplianceAmendmentReason(models.Model):
    reason = models.CharField("Reason", max_length=125)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return self.reason


class ComplianceAmendmentRequest(CompRequest):
    STATUS_CHOICES = (("requested", "Requested"), ("amended", "Amended"))
    # try:
    #     # model requires some choices if AmendmentReason does not yet exist or is empty
    #     REASON_CHOICES = list(AmendmentReason.objects.values_list('id', 'reason'))
    #     if not REASON_CHOICES:
    #         REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                           (1, 'There was missing information'),
    #                           (2, 'Other'))
    # except:
    #     REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                       (1, 'There was missing information'),
    #                       (2, 'Other'))

    status = models.CharField(
        "Status", max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    # reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])
    reason = models.ForeignKey(
        ComplianceAmendmentReason, blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        app_label = "leaseslicensing"

    def generate_amendment(self, request):
        with transaction.atomic():
            if self.status == "requested":
                compliance = self.compliance
                if compliance.processing_status != "due":
                    compliance.processing_status = "due"
                    compliance.customer_status = "due"
                    compliance.save()
                # Create a log entry for the proposal
                compliance.log_user_action(
                    ComplianceUserAction.ACTION_ID_REQUEST_AMENDMENTS, request
                )
                # Create a log entry for the organisation
                applicant_field = getattr(
                    compliance.proposal, compliance.proposal.applicant_field
                )
                #applicant_field.log_user_action(
                #    ComplianceUserAction.ACTION_ID_REQUEST_AMENDMENTS, request
                #)
                send_amendment_email_notification(self, request, compliance)
