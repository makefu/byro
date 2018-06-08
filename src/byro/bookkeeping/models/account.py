from django.db import models
from django.db.models import Q
from django.utils.decorators import classproperty
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from byro.common.models.auditable import Auditable
from byro.common.models.choices import Choices


class AccountCategory(Choices):
    # Regular Categories
    MEMBER_DONATION = 'member_donation'  # deprecated
    MEMBER_FEES = 'member_fees'  # deprecated

    # Categories for double-entry bookkeeping
    ASSET = 'asset'  # de: Aktiva, for example your bank account or cash
    LIABILITY = 'liability'  # de: Passiva, for example invoices you have to pay
    INCOME = 'income'  # de: Ertragskonten, for example for fees paid
    EXPENSE = 'expense'  # de: Aufwandskonten, for example for fees to be paid

    @classproperty
    def choices(cls):
        return (
            (cls.MEMBER_DONATION, _('Donation account')),
            (cls.MEMBER_FEES, _('Membership fee account')),
            (cls.ASSET, _('Asset account')),
            (cls.LIABILITY, _('Liability account')),
            (cls.INCOME, _('Income account')),
            (cls.EXPENSE, _('Expense account')),
        )


class Account(Auditable, models.Model):
    account_category = models.CharField(
        choices=AccountCategory.choices,
        max_length=AccountCategory.max_length,
    )
    name = models.CharField(max_length=300, null=True)  # e.g. 'Laser donations'

    class Meta:
        unique_together = (
            ('account_category', 'name'),
        )

    def __str__(self):
        if self.name:
            return self.name
        return '{self.account_category} account #{self.id}'.format(self=self)

    @property
    def transactions(self):
        from byro.bookkeeping.models import VirtualTransaction
        return VirtualTransaction.objects.filter(
            Q(source_account=self) | Q(destination_account=self)
        )

    def _aggregate_by_date(self, qs, start, end):
        if start:
            qs = qs.filter(value_datetime__gte=start)
        if end:
            qs = qs.filter(value_datetime__lte=end)
        return qs.aggregate(total=models.Sum('amount'))['total'] or 0

    def total_in(self, start=None, end=now()):
        return self._aggregate_by_date(self.incoming_transactions, start=start, end=end)

    def total_out(self, start=None, end=now()):
        return self._aggregate_by_date(self.outgoing_transactions, start=start, end=end)

    def balance(self, start=None, end=now()):
        incoming_sum = self.total_in(start=start, end=end)
        outgoing_sum = self.total_out(start=start, end=end)
        return incoming_sum - outgoing_sum
