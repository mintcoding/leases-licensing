from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from datetime import datetime
from leaseslicensing.utils.migration_utils import OrganisationReader, check_parks

import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Runs the initial deployment
    """

    help = "Run the initial deployment"

    def handle(self, *args, **options):

        # reader=OrganisationReader('leaseslicensing/utils/csv/CommercialLicencesMigration_09Dec2019.csv')
        # reader=OrganisationReader('leaseslicensing/utils/csv/EClass_licences_02Dec2019.csv')
        # reader=OrganisationReader('leaseslicensing/utils/csv/CommercialLicencesMigration_07Jan2020_final.csv')
        reader = OrganisationReader(
            "leaseslicensing/utils/csv/Commercial-RATIS-Migration-20200605.csv"
        )
        reader.add_users()
