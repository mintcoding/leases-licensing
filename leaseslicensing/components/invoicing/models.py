from django.db import models
from datetime import datetime
import pytz
from ledger_api_client import settings_base
from dateutil.relativedelta import relativedelta


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class ChargeMethod(models.Model):
    """A class to represent a competitive process"""

    key = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200,)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return self.display_name


class RepetitionType(models.Model):
    key = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200,)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return self.display_name


class ReviewDateAnnually(BaseModel):
    review_date = models.DateField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Review Date Annually'

    @staticmethod
    def get_review_date_annually_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_annually = ReviewDateAnnually.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return review_date_annually


class ReviewDateQuarterly(BaseModel):
    review_date_q1 = models.DateField()
    review_date_q2 = models.DateField()
    review_date_q3 = models.DateField()
    review_date_q4 = models.DateField()
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Review Date Quarterly'

    @staticmethod
    def get_review_date_quarterly_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_quarterly = ReviewDateQuarterly.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return review_date_quarterly


class ReviewDateMonthly(BaseModel):
    review_date = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Review Date Monthly'

    @staticmethod
    def get_review_date_monthly_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        review_date_monthly = ReviewDateMonthly.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return review_date_monthly


class InvoicingDateAnnually(BaseModel):
    invoicing_date = models.DateField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Invoicing Date Annually'

    @staticmethod
    def get_invoicing_date_annually_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_annually = InvoicingDateAnnually.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return invoicing_date_annually


class InvoicingDateQuarterly(BaseModel):
    invoicing_date_q1 = models.DateField()
    invoicing_date_q2 = models.DateField()
    invoicing_date_q3 = models.DateField()
    invoicing_date_q4 = models.DateField()
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Invoicing Date Quarterly'

    @staticmethod
    def get_invoicing_date_quarterly_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_quarterly = InvoicingDateQuarterly.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return invoicing_date_quarterly


class InvoicingDateMonthly(BaseModel):
    invoicing_date = models.PositiveSmallIntegerField(null=True, blank=True)
    date_of_enforcement = models.DateField()

    class Meta:
        app_label = "leaseslicensing"
        verbose_name_plural = 'Invoicing Date Monthly'

    @staticmethod
    def get_invoicing_date_monthly_by_date(target_date=datetime.now(pytz.timezone(settings_base.TIME_ZONE)).date()):
        """
        Return an setting object which is enabled at the target_date
        """
        invoicing_date_monthly = InvoicingDateMonthly.objects.filter(
            date_of_enforcement__lte=target_date,
        ).order_by('date_of_enforcement').last()
        return invoicing_date_monthly


def get_year():
    cpis = ConsumerPriceIndex.objects.all()
    if cpis:
        latest_cpis = cpis.order_by('year').last()
        return getattr(latest_cpis, 'year') + 1
    else:
        return ConsumerPriceIndex.start_year


class ConsumerPriceIndex(BaseModel):
    start_year = 2021

    year = models.PositiveSmallIntegerField(null=True, blank=True, default=get_year)
    cpi_value_q1 = models.FloatField('CPI (Q1)', null=True, blank=True)
    cpi_value_q2 = models.FloatField('CPI (Q2)', null=True, blank=True)
    cpi_value_q3 = models.FloatField('CPI (Q3)', null=True, blank=True)
    cpi_value_q4 = models.FloatField('CPI (Q4)', null=True, blank=True)

    class Meta:
        app_label = "leaseslicensing"

    def __str__(self):
        return '{}'.format(self.name)

    @property
    def name(self):
        if self.year:
            return '{} --- {}'.format(str(self.year), str(self.year + 1))
        else:
            return '---'

    @property
    def q1_start_date(self):
        return datetime.strptime(str(self.year) + '/07/01', '%Y/%m/%d')

    @property
    def q2_start_date(self):
        return datetime.strptime(str(self.year) + '/10/01', '%Y/%m/%d')

    @property
    def q3_start_date(self):
        return datetime.strptime(str(self.year + 1) + '/01/01', '%Y/%m/%d')

    @property
    def q4_start_date(self):
        return datetime.strptime(str(self.year + 1) + '/04/01', '%Y/%m/%d')

    @property
    def q1_end_date(self):
        return self.q1_start_date + relativedelta(months=3) - relativedelta(days=1)

    @property
    def q2_end_date(self):
        return self.q2_start_date + relativedelta(months=3) - relativedelta(days=1)

    @property
    def q3_end_date(self):
        return self.q3_start_date + relativedelta(months=3) - relativedelta(days=1)

    @property
    def q4_end_date(self):
        return self.q4_start_date + relativedelta(months=3) - relativedelta(days=1)


class InvoicingDetails(BaseModel):
    """
    This is the main model to store invoicing details, generated by a proposal first (Proposal has a field: invoicing_details)
    then copied and/or edited as business run
    """
    charge_method = models.ForeignKey(ChargeMethod, null=True, blank=True, on_delete=models.SET_NULL)
    base_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    once_off_charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    review_once_every = models.PositiveSmallIntegerField(null=True, blank=True)
    invoicing_once_every = models.PositiveSmallIntegerField(null=True, blank=True)
    review_repetition_type = models.ForeignKey(RepetitionType, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoicing_details_set_for_review')
    invoicing_repetition_type = models.ForeignKey(RepetitionType, null=True, blank=True, on_delete=models.SET_NULL, related_name='invoicing_details_set_for_invoicing')

    approval = models.ForeignKey('Approval', null=True, blank=True, on_delete=models.SET_NULL)
    previous_invoicing_details = models.OneToOneField('self', null=True, blank=True, related_name='next_invoicing_details', on_delete=models.SET_NULL)

    class Meta:
        app_label = "leaseslicensing"

        # constraints = [
        #     models.CheckConstraint(
        #         check=Q(base_fee_amount=0) | Q(once_off_charge_amount=0),
        #         name='either_one_null',
        #     )
        # ]


class FixedAnnualIncrement(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    increment_amount = models.DecimalField(max_digits=10, decimal_places=2, default="0.00")
    invoicing_details = models.ForeignKey(InvoicingDetails, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = "leaseslicensing"


class FixedAnnualPercentage(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    percentage = models.FloatField(default=0)
    invoicing_details = models.ForeignKey(InvoicingDetails, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = "leaseslicensing"


class PercentageOfGrossTurnover(BaseModel):
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    percentage = models.FloatField(default=0)
    invoicing_details = models.ForeignKey(InvoicingDetails, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = "leaseslicensing"


class CrownLandRentReviewDate(BaseModel):
    review_date = models.DateField(null=True, blank=True)
    invoicing_details = models.ForeignKey(InvoicingDetails, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        app_label = "leaseslicensing"
