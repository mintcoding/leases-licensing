from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from datetime import datetime
from leaseslicensing.utils.migration_utils import run_deploy

import itertools

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Runs the initial deployment
    """

    help = "Run the initial deployment"

    def handle(self, *args, **options):
        dt = datetime(2019, 11, 29)  # never run after this date

        if datetime.now() < dt:
            logger.info("Running command {}".format(__name__))
            # run_deploy('leaseslicensing/utils/csv/Commercial-Licences-Migration-20191119.csv', 'leaseslicensing/utils/csv/E-Class-Licences-20191119.csv')
            run_deploy(
                "leaseslicensing/utils/csv/T-Class-Test.csv",
                "leaseslicensing/utils/csv/E-Class-Test.csv",
            )
