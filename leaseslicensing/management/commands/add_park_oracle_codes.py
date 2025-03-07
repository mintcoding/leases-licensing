from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from leaseslicensing.components.main.models import ApplicationType, Park
import csv
import datetime


import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Upload Oracle Codes for Parks"

    def handle(self, *args, **options):

        logger.info("Running command {}".format(__name__))

        # with open('leaseslicensing/utils/csv/park_oracle_codes_09Nov2020.csv') as csvfile:
        with open(
            "leaseslicensing/utils/csv/park_oracle_codes_03Dec2020.csv"
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            header = next(reader)
            for row in reader:
                park_name = row[0]
                oracle_code_tclass = row[1]
                oracle_code_filming = row[2]
                oracle_code_event = row[3]
                try:
                    park = Park.objects.get(name=park_name)
                    park.oracle_codes.update_or_create(
                        code=oracle_code_tclass, code_type=ApplicationType.TCLASS
                    )
                    park.oracle_codes.update_or_create(
                        code=oracle_code_filming, code_type=ApplicationType.FILMING
                    )
                    park.oracle_codes.update_or_create(
                        code=oracle_code_event, code_type=ApplicationType.EVENT
                    )
                except Exception as e:
                    print(e)
                    print(row[0], row[1], row[2], row[3])
                    print

        logger.info("Command {} completed".format(__name__))
