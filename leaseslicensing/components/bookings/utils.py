from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import render

from datetime import datetime, timedelta, date
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from leaseslicensing.components.main.models import ApplicationType
from leaseslicensing.components.proposals.models import Proposal, ProposalUserAction
from leaseslicensing.components.organisations.models import Organisation
from leaseslicensing.components.bookings.models import (
    Booking,
    BookingInvoice,
    ApplicationFee,
    ComplianceFee,
)

from leaseslicensing.components.bookings.email import (
    send_invoice_tclass_email_notification,
    send_monthly_confirmation_tclass_email_notification,
    send_confirmation_tclass_email_notification,
    send_monthly_invoice_tclass_email_notification,
)
from ledger_api_client.utils import (
    create_basket_session,
    use_existing_basket_from_invoice,
    create_checkout_session,
    # calculate_excl_gst,
    # get_cookie_basket,
    # createCustomBasket,
    # CreateInvoiceBasket,
    oracle_parser,
)

# from ledger.payments.invoice.utils import CreateInvoiceBasket
from ledger_api_client.ledger_models import EmailUserRO as EmailUser, Invoice
import json
import ast
from decimal import Decimal

import logging

logger = logging.getLogger("payment_checkout")


def create_booking(request, proposal, booking_type=Booking.BOOKING_TYPE_TEMPORARY):
    """Create the ledger lines - line items for invoice sent to payment system"""

    if (
        booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING
        and proposal.org_applicant
        and proposal.org_applicant.monthly_invoicing_allowed
    ):
        booking, created = Booking.objects.get_or_create(
            invoices__isnull=True,
            proposal_id=proposal.id,
            booking_type=booking_type,
            created__month=timezone.now().month,
            defaults={
                "created_by": request.user,
                "created": timezone.now(),
            },
        )
        # lines = ast.literal_eval(request.POST['line_details'])['tbody']
        lines = json.loads(request.POST["line_details"])["tbody"]

    elif (
        booking_type == Booking.BOOKING_TYPE_INTERNET
        and proposal.org_applicant
        and proposal.org_applicant.bpay_allowed
    ) or (booking_type == Booking.BOOKING_TYPE_RECEPTION):
        # (booking_type == Booking.BOOKING_TYPE_RECEPTION and proposal.org_applicant.other_allowed):
        booking = Booking.objects.create(
            proposal_id=proposal.id, created_by=request.user, booking_type=booking_type
        )
        # lines = ast.literal_eval(request.POST['line_details'])['tbody']
        lines = json.loads(request.POST["line_details"])["tbody"]

    else:
        booking = Booking.objects.create(
            proposal_id=proposal.id, created_by=request.user, booking_type=booking_type
        )
        lines = json.loads(request.POST["payment"])["tbody"]

    # Booking.objects.filter(invoices__isnull=True, booking_type=4, proposal_id=478, proposal__org_applicant=org)

    # tbody = json.loads(request.POST['payment'])['tbody']
    # lines = ast.literal_eval(request.POST['line_details'])['tbody']
    for row in lines:
        park_id = row[0]["value"]
        arrival = row[1]
        same_tour_group = True if row[2] == True else False
        no_adults = int(row[3]) if row[3] else 0
        no_children = int(row[4]) if row[4] else 0
        no_free_of_charge = int(row[5]) if row[5] else 0
        park = Park.objects.get(id=park_id)

        # same tour group visitors
        no_adults_same_tour = int(row[7]) if row[7] else 0
        no_children_same_tour = int(row[8]) if row[8] else 0
        no_free_of_charge_same_tour = int(row[9]) if row[9] else 0

        # no_adults = no_adults if no_adults_same_tour==0 else no_adults_same_tour
        # no_children = no_children if no_children_same_tour==0 else no_children_same_tour
        # no_free_of_charge = no_free_of_charge if no_free_of_charge_same_tour==0 else no_free_of_charge_same_tour

        if any([no_adults, no_children, no_free_of_charge]) > 0:
            park_booking = ParkBooking.objects.create(
                booking=booking,
                park_id=park_id,
                arrival=datetime.strptime(arrival, "%Y-%m-%d").date(),
                no_adults=no_adults,
                no_children=no_children,
                no_free_of_charge=no_free_of_charge,
                cost=no_adults * park.adult_price + no_children * park.child_price,
                no_adults_same_tour=no_adults_same_tour,
                no_children_same_tour=no_children_same_tour,
                no_free_of_charge_same_tour=no_free_of_charge_same_tour,
                same_tour_group=same_tour_group,
            )
    if not park_booking:
        raise ValidationError("Must have at least one person visiting the park")

    return booking


"""
TEST 1:
1. create 1 Organisation:
   a. monthly_invoicing_allowed = True
   b. monthly_invoicing_period = 5 (create invoice 0 days from 1st of the month)
   c. monthly_payment_due = 20 (set settlement_date to 20 days after invoice created)
2. For Org, create 2 or 3 bookings, add parks --> pre-date booking to last month
3. run monthly invoice script:
   a. confirm monthly_script SKIPS invoice creation, if executed before the invoicing date (1st of the month + monthly_invoicing_period(5) --> before 6th day of the month)
   b. confirm monthly_script creates invoice, if executed after the invoicing date (1st of the month + monthly_invoicing_period(5) --> on or after 6th of the month)
   b. confirm the created invoice has the correct payment date printed on the PDF (invoice_created + monthly_invoicing_period(20) --> 26th of the month)
4. confirm cannot re-create invoice again for this booking

TEST 2:
1. create 2 Organisations (with different invoicing periods):
   ORG_1:
           a. monthly_invoicing_allowed = True
           b. monthly_invoicing_period = 3 (create invoice 3 days from 1st of the month)
           c. monthly_payment_due = 20 (set settlement_date to 20 days after invoice created)
   ORG_2:
           a. monthly_invoicing_allowed = True
           b. monthly_invoicing_period = 5 (create invoice 5 days from 1st of the month)
           c. monthly_payment_due = 20 (set settlement_date to 20 days after invoice created)
2. For Org_1, create 2 or 3 bookings, add parks --> pre-date booking to last month
3. For Org_3, create 2 or 3 bookings, add parks --> pre-date booking to last month
4. run monthly invoice script:
   a. confirm monthly_script SKIPS invoice creation (for both Orgs), if executed before the invoicing date (1st of the month + monthly_invoicing_period(3) --> before 4th day of the month)
   b. confirm monthly_script creates invoice for Org_1 only, if executed after the Org_1 invoicing date (1st of the month + monthly_invoicing_period(3) --> on or after 4th of the month)
   c. confirm monthly_script creates invoice for Org_2 only, if executed after the Org_2 invoicing date (1st of the month + monthly_invoicing_period(5) --> on or after 6th of the month)
   d. confirm the Org_1 invoice has the correct payment date printed on the PDF (invoice_created_date + monthly_invoicing_period(20) --> 24h of the month)
   e. confirm the Org_2 invoice has the correct payment date printed on the PDF (invoice_created_date + monthly_invoicing_period(20) --> 26 of the month)
4. confirm cannot re-create invoices again for these booking



"""


def create_monthly_invoice(user, offset_months=-1):
    bookings = Booking.objects.filter(
        invoices__isnull=True,
        booking_type=Booking.BOOKING_TYPE_MONTHLY_INVOICING,
        created__month=(timezone.now() + relativedelta(months=offset_months)).month,
    )

    failed_bookings = []
    for booking in bookings:
        with transaction.atomic():
            if is_invoicing_period(booking) and is_monthly_invoicing_allowed(booking):
                try:
                    logger.info(
                        "Creating monthly invoice for booking {}".format(
                            booking.admission_number
                        )
                    )
                    order = create_invoice(booking, payment_method="monthly_invoicing")
                    invoice = Invoice.objects.get(order_number=order.number)
                    # invoice.settlement_date = calc_payment_due_date(booking, invoice.created + relativedelta(months=1))
                    # invoice.save()

                    deferred_payment_date = calc_payment_due_date(
                        booking, invoice.created
                    )
                    book_inv = BookingInvoice.objects.create(
                        booking=booking,
                        invoice_reference=invoice.reference,
                        payment_method=invoice.payment_method,
                        deferred_payment_date=deferred_payment_date,
                    )

                    recipients = list(
                        set([booking.proposal.applicant_email, user.email])
                    )  # unique list
                    send_monthly_invoice_tclass_email_notification(
                        user, booking, invoice, recipients=recipients
                    )
                    ProposalUserAction.log_action(
                        booking.proposal,
                        ProposalUserAction.ACTION_SEND_MONTHLY_INVOICE.format(
                            invoice.reference,
                            booking.proposal.id,
                            ", ".join(recipients),
                        ),
                        user,
                    )
                except Exception as e:
                    logger.error(
                        "Failed to create monthly invoice for booking_id {}".format(
                            booking.id
                        )
                    )
                    logger.error("{}".format(e))
                    failed_bookings.append(booking.id)

    return failed_bookings


def create_monthly_confirmation(user, booking):
    """From 'Park Entry Fees' payment screen, monthly invoicing creates invoice later (the next month), so immediately we only send a confirmation.
    For more parks/arrival_dates booked for the same licence, the monthly confirmation pdf is appended with all the park entries for that given month.
    """

    failed_bookings = []
    with transaction.atomic():
        if (
            booking.booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING
            and booking.proposal.org_applicant
            and is_monthly_invoicing_allowed(booking)
        ):
            try:
                recipients = list(
                    set([booking.proposal.applicant_email, user.email])
                )  # unique list
                send_monthly_confirmation_tclass_email_notification(
                    user, booking, recipients=recipients
                )
                ProposalUserAction.log_action(
                    booking.proposal,
                    ProposalUserAction.ACTION_SEND_MONTHLY_CONFIRMATION.format(
                        booking.id, booking.proposal.id, ", ".join(recipients)
                    ),
                    user,
                )
            except Exception as e:
                logger.error(
                    "Failed to send Monthly Confirmation email for booking_id {}".format(
                        booking.id
                    )
                )
                logger.error("{}".format(e))
                failed_bookings.append(booking.id)

    return failed_bookings


def create_bpay_invoice(user, booking):

    failed_bookings = []
    with transaction.atomic():
        if (
            booking.booking_type == Booking.BOOKING_TYPE_INTERNET
            and booking.proposal.org_applicant
            and booking.proposal.org_applicant.bpay_allowed
        ):
            try:
                now = timezone.now().date()
                dt = date(now.year, now.month, 1) + relativedelta(months=1)
                logger.info(
                    "Creating BPAY invoice for booking {}".format(
                        booking.admission_number
                    )
                )
                order = create_invoice(booking, payment_method="bpay")
                invoice = Invoice.objects.get(order_number=order.number)
                # invoice.settlement_date = calc_payment_due_date(booking, dt) - relativedelta(days=1)
                # invoice.save()

                deferred_payment_date = calc_payment_due_date(
                    booking, dt
                ) - relativedelta(days=1)
                book_inv = BookingInvoice.objects.create(
                    booking=booking,
                    invoice_reference=invoice.reference,
                    payment_method=invoice.payment_method,
                    deferred_payment_date=deferred_payment_date,
                )

                # send_monthly_invoice_tclass_email_notification(user, booking, invoice, recipients=[booking.proposal.applicant_email])
                recipients = list(
                    set([booking.proposal.applicant_email, user.email])
                )  # unique list
                send_invoice_tclass_email_notification(
                    user, booking, invoice, recipients=recipients
                )
                send_confirmation_tclass_email_notification(
                    user, booking, invoice, recipients=recipients
                )
                ProposalUserAction.log_action(
                    booking.proposal,
                    ProposalUserAction.ACTION_SEND_BPAY_INVOICE.format(
                        invoice.reference, booking.proposal.id, ", ".join(recipients)
                    ),
                    user,
                )
            except Exception as e:
                logger.error(
                    "Failed to create BPAY invoice for booking_id {}".format(booking.id)
                )
                logger.error("{}".format(e))
                failed_bookings.append(booking.id)

    return failed_bookings


def create_other_invoice(user, booking):
    """This method allows internal payments officer to pay via ledger directly i.e. over the phone credit card details or cheque by post or cash etc

    Currently not USED in COLS (Only Payments by CC, BPAY and Monthly Invoicing is allowed), but implemented for use possibly in the future
    """

    failed_bookings = []
    with transaction.atomic():
        # if booking.booking_type == Booking.BOOKING_TYPE_RECEPTION and booking.proposal.org_applicant.other_allowed:
        if booking.booking_type == Booking.BOOKING_TYPE_RECEPTION:
            try:
                now = timezone.now().date()
                dt = date(now.year, now.month, 1) + relativedelta(months=1)
                logger.info(
                    "Creating OTHER (CASH/CHEQUE) invoice for booking {}".format(
                        booking.admission_number
                    )
                )
                order = create_invoice(booking, payment_method="other")
                invoice = Invoice.objects.get(order_number=order.number)

                # TODO determine actual deferred_payment_date - currently defaulting to BPAY equiv.
                deferred_payment_date = calc_payment_due_date(
                    booking, dt
                ) - relativedelta(days=1)
                book_inv = BookingInvoice.objects.create(
                    booking=booking,
                    invoice_reference=invoice.reference,
                    payment_method=invoice.payment_method,
                    deferred_payment_date=deferred_payment_date,
                )

                # TODO - determine what emails to be sent and when
                # send_monthly_invoice_tclass_email_notification(user, booking, invoice, recipients=[booking.proposal.applicant_email])
                # ProposalUserAction.log_action(booking.proposal,ProposalUserAction.ACTION_SEND_MONTHLY_INVOICE.format(booking.proposal.id),booking.proposal.applicant_email)
            except Exception as e:
                logger.error(
                    "Failed to create OTHER invoice for booking_id {}".format(
                        booking.id
                    )
                )
                logger.error("{}".format(e))
                failed_bookings.append(booking.id)

    return failed_bookings


def calc_payment_due_date(booking, _date):
    org_applicant = booking.proposal.org_applicant
    if (
        isinstance(org_applicant, Organisation)
        and org_applicant.monthly_payment_due_period > 0
    ):
        return _date + relativedelta(days=org_applicant.monthly_payment_due_period)
    return _date + relativedelta(days=30)


def is_invoicing_period(booking):
    org_applicant = booking.proposal.org_applicant
    if isinstance(org_applicant, Organisation):
        return timezone.now().day >= org_applicant.monthly_invoicing_period
    return False


def is_monthly_invoicing_allowed(booking):
    org_applicant = booking.proposal.org_applicant
    if isinstance(org_applicant, Organisation):
        return (
            booking.booking_type == Booking.BOOKING_TYPE_MONTHLY_INVOICING
            and org_applicant
            and org_applicant.monthly_invoicing_allowed
        )
    return False


def get_session_booking(session):
    if "cols_booking" in session:
        booking_id = session["cols_booking"]
    else:
        raise Exception("Booking not in Session")

    try:
        return Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Exception("Booking not found for booking_id {}".format(booking_id))


def set_session_booking(session, booking):
    session["cols_booking"] = booking.id
    session.modified = True


def delete_session_booking(session):
    if "cols_booking" in session:
        del session["cols_booking"]
        session.modified = True


def get_session_application_invoice(session):
    """Application Fee session ID"""
    if "cols_app_invoice" in session:
        application_fee_id = session["cols_app_invoice"]
    else:
        raise Exception("Application not in Session")

    try:
        # return Invoice.objects.get(id=application_invoice_id)
        # return Proposal.objects.get(id=proposal_id)
        return ApplicationFee.objects.get(id=application_fee_id)
    except Invoice.DoesNotExist:
        raise Exception(
            "Application not found for application {}".format(application_fee_id)
        )


def set_session_application_invoice(session, application_fee):
    """Application Fee session ID"""
    session["cols_app_invoice"] = application_fee.id
    session.modified = True


def delete_session_application_invoice(session):
    """Application Fee session ID"""
    if "cols_app_invoice" in session:
        del session["cols_app_invoice"]
        session.modified = True


# Events - Compliance
def get_session_compliance_invoice(session):
    """Compliance Fee session ID"""
    if "cols_comp_invoice" in session:
        compliance_fee_id = session["cols_comp_invoice"]
    else:
        raise Exception("Compliance not in Session")

    try:
        return ComplianceFee.objects.get(id=compliance_fee_id)
    except Invoice.DoesNotExist:
        raise Exception(
            "Compliance record not found for compliance {}".format(compliance_fee_id)
        )


def set_session_compliance_invoice(session, compliance_fee):
    """Compliance Fee session ID"""
    session["cols_comp_invoice"] = compliance_fee.id
    session.modified = True


def delete_session_compliance_invoice(session):
    """Compliance Fee session ID"""
    if "cols_comp_invoice" in session:
        del session["cols_comp_invoice"]
        session.modified = True


# Filming - Fee (Application and Licence)
def get_session_filming_invoice(session):
    """Filming Fee session ID"""
    if "cols_filming_invoice" in session:
        filming_fee_id = session["cols_filming_invoice"]
    else:
        raise Exception("Filming not in Session")

    try:
        return FilmingFee.objects.get(id=filming_fee_id)
    except Invoice.DoesNotExist:
        raise Exception(
            "Filming record not found for filming_fee {}".format(filming_fee_id)
        )


def set_session_filming_invoice(session, filming_fee):
    """Filming Fee session ID"""
    session["cols_filming_invoice"] = filming_fee.id
    session.modified = True


def delete_session_filming_invoice(session):
    """Filming Fee session ID"""
    if "cols_filming_invoice" in session:
        del session["cols_filming_invoice"]
        session.modified = True


def create_compliance_fee_lines(
    compliance, invoice_text=None, vouchers=[], internal=False
):
    """Create the ledger lines - line item for compliance fee sent to payment system"""

    def add_line_item(park, price, no_persons):
        if no_persons > 0:
            return {
                "ledger_description": "{}, participants: {}".format(
                    park.name, no_persons
                ),
                "oracle_code": park.oracle_code(compliance.proposal.application_type),
                #'oracle_code': 'NNP415 GST',
                "price_incl_tax": price,
                "price_excl_tax": price,  # NO GST
                #'price_excl_tax':  price if park.is_gst_exempt else round(float(calculate_excl_gst(price)), 2),
                "quantity": 1,  # no_persons,
            }
        return None

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    events_park_price = compliance.proposal.application_type.events_park_fee
    events_parks = compliance.proposal.events_parks.all().distinct("park__name")
    # cost_per_park = (events_park_price * compliance.num_participants) / len(events_parks)
    invoice_total = events_park_price * compliance.num_participants
    if settings.DEBUG:
        # since Ledger UAT only handles whole integer total
        invoice_total = round(invoice_total, 0)

    alloc_per_park = round(invoice_total / len(events_parks), 2)
    rounding_error = round(invoice_total - (alloc_per_park * len(events_parks)), 2)

    lines = []
    for idx, events_park in enumerate(events_parks, 1):
        park = events_park.park
        if idx == len(events_parks):
            # add rounding error to last line/product
            lines.append(
                add_line_item(
                    park,
                    price=alloc_per_park + rounding_error,
                    no_persons=compliance.num_participants,
                )
            )
        else:
            lines.append(
                add_line_item(
                    park, price=alloc_per_park, no_persons=compliance.num_participants
                )
            )

    # logger.info('{}'.format(lines))
    return lines


def create_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    lines = []
    if proposal.application_type.name == ApplicationType.TCLASS:
        return create_tclass_fee_lines(proposal, invoice_text, vouchers, internal)
    elif proposal.application_type.name == ApplicationType.EVENT:
        return create_event_fee_lines(proposal, invoice_text, vouchers, internal)

    return lines


def create_tclass_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    """Create the ledger lines - line item for application fee sent to payment system"""

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    application_price = proposal.application_type.application_fee
    licence_price = proposal.licence_fee_amount

    if proposal.application_type.name == ApplicationType.TCLASS:
        if proposal.org_applicant.apply_application_discount:
            application_discount = min(
                proposal.org_applicant.application_discount, application_price
            )
        if proposal.org_applicant.apply_licence_discount:
            licence_discount = min(
                proposal.org_applicant.licence_discount, licence_price
            )

    line_items = [
        {
            "ledger_description": "Application Fee - {} - {}".format(
                now, proposal.lodgement_number
            ),
            "oracle_code": proposal.application_type.oracle_code_application,
            "price_incl_tax": application_price,
            #'price_excl_tax':  application_price if proposal.application_type.is_gst_exempt else calculate_excl_gst(application_price),
            "quantity": 1,
        },
        {
            "ledger_description": "Licence Charge {} - {} - {}".format(
                proposal.other_details.get_preferred_licence_period_display(),
                now,
                proposal.lodgement_number,
            ),
            "oracle_code": proposal.application_type.oracle_code_licence,
            "price_incl_tax": licence_price,
            #'price_excl_tax':  licence_price if proposal.application_type.is_gst_exempt else calculate_excl_gst(licence_price),
            "quantity": 1,
        },
    ]

    # Add fee Waiver To T Class, if any
    if (
        proposal.application_type.name == ApplicationType.TCLASS
        and proposal.org_applicant
    ):
        if proposal.org_applicant.apply_application_discount:
            line_items += [
                {
                    "ledger_description": "Application Fee Waiver - {} - {}".format(
                        now, proposal.lodgement_number
                    ),
                    "oracle_code": proposal.application_type.oracle_code_application,
                    "price_incl_tax": -application_discount,
                    "price_excl_tax": -application_discount,
                    "quantity": 1,
                }
            ]
        if proposal.org_applicant.apply_licence_discount:
            line_items += [
                {
                    "ledger_description": "Licence Charge Waiver - {} - {}".format(
                        now, proposal.lodgement_number
                    ),
                    "oracle_code": proposal.application_type.oracle_code_application,
                    "price_incl_tax": -licence_discount,
                    "price_excl_tax": -licence_discount,
                    "quantity": 1,
                }
            ]

    logger.info("{}".format(line_items))
    return line_items


def create_event_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    """EVENT: Create the ledger lines - line item for application fee sent to payment system"""

    def get_application_fee():
        application_fee = proposal.application_type.application_fee

        org = proposal.org_applicant
        if org.charge_once_per_year:
            year_start = date(
                proposal.event_activity.commencement_date.year,
                org.charge_once_per_year.month,
                org.charge_once_per_year.day,
            )
            year_end = year_start + relativedelta(years=1)
            fees_paid = [
                (p, p.fee_amount)
                for p in Proposal.objects.filter(
                    org_applicant=org,
                    application_type__name=ApplicationType.EVENT,
                    event_activity__commencement_date__gte=year_start,
                    event_activity__completion_date__lt=year_end,
                )
                if p.fee_amount and p.fee_amount != "null" and float(p.fee_amount) > 0.0
            ]

            logger.info(
                "{} - {}: Fees paid between {} - {}\{})".format(
                    proposal, org, year_start, year_end, fees_paid
                )
            )
            if fees_paid:
                # application fee has already been paid at least once for the calendar period
                application_fee = Decimal("0.0")
                logger.info(
                    "{} - {}: Setting Application Fee to 0.0 (free free for period {} - {})".format(
                        proposal, org, year_start, year_end
                    )
                )

        return application_fee

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    application_price = get_application_fee()

    if proposal.application_type.name == ApplicationType.EVENT:
        # There is no Licence fee for Event application.
        line_items = [
            {
                "ledger_description": "Application Fee - {} - {}".format(
                    now, proposal.lodgement_number
                ),
                "oracle_code": proposal.application_type.oracle_code_application,
                "price_incl_tax": application_price,
                #'price_excl_tax':  application_price if proposal.application_type.is_gst_exempt else calculate_excl_gst(application_price),
                "quantity": 1,
            },
        ]
    logger.info("{}".format(line_items))
    return line_items


def create_filming_park_fee_lines(proposal, licence_fee, licence_text, filming_period):
    """Create the ledger lines, line items for each park - filming licence fee divided evenly and sent to payment system"""

    def add_line_item(park, price):
        return {
            "ledger_description": f"{park.name} ({licence_text} - {filming_period})",
            "oracle_code": park.oracle_code(proposal.application_type),
            "price_incl_tax": float(price),
            "price_excl_tax": float(price),  # NO GST
            "quantity": 1,  # no_persons,
        }

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    filming_parks = proposal.filming_parks.all().distinct("park__name")
    invoice_total = licence_fee
    if settings.DEBUG:
        # since Ledger UAT only handles whole integer total
        invoice_total = round(invoice_total, 0)

    alloc_per_park = round(invoice_total / len(filming_parks), 2)
    rounding_error = round(invoice_total - (alloc_per_park * len(filming_parks)), 2)

    lines = []
    for idx, filming_park in enumerate(filming_parks, 1):
        park = filming_park.park
        if idx == len(filming_parks):
            # add rounding error to last line/product
            lines.append(add_line_item(park, price=alloc_per_park + rounding_error))
        else:
            lines.append(add_line_item(park, price=alloc_per_park))

    # logger.info('{}'.format(lines))
    return lines


def create_filming_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    if "motion_film" in proposal.filming_activity.film_type:
        # Filming (and perhaps Photography)
        desc = "Filming/Photography"
        if proposal.filming_licence_charge_type == proposal.HALF_DAY_CHARGE:
            licence_fee = proposal.application_type.filming_fee_half_day
            licence_text = "Half day"
        elif proposal.filming_licence_charge_type == proposal.FULL_DAY_CHARGE:
            licence_fee = proposal.application_type.filming_fee_full_day
            licence_text = "Full day"
        elif proposal.filming_licence_charge_type == proposal.TWO_DAYS_CHARGE:
            licence_fee = proposal.application_type.filming_fee_2days
            licence_text = "Two days"
        elif proposal.filming_licence_charge_type == proposal.THREE_OR_MORE_DAYS_CHARGE:
            licence_fee = proposal.application_type.filming_fee_3days
            licence_text = "Three days or more"
        elif proposal.filming_licence_charge_type == proposal.NON_STANDARD_CHARGE:
            licence_fee = proposal.filming_non_standard_charge
            licence_text = "Non-standard charge"
        else:
            raise Exception("Unknown filming charge type")
    else:
        # Photography
        desc = "Photography"
        if proposal.filming_licence_charge_type == proposal.HALF_DAY_CHARGE:
            licence_fee = proposal.application_type.photography_fee_half_day
            licence_text = "Half day"
        elif proposal.filming_licence_charge_type == proposal.FULL_DAY_CHARGE:
            licence_fee = proposal.application_type.photography_fee_full_day
            licence_text = "Full day"
        elif proposal.filming_licence_charge_type == proposal.TWO_DAYS_CHARGE:
            licence_fee = proposal.application_type.photography_fee_2days
            licence_text = "Two days"
        elif proposal.filming_licence_charge_type == proposal.THREE_OR_MORE_DAYS_CHARGE:
            licence_fee = proposal.application_type.photography_fee_3days
            licence_text = "Three days or more"
        elif proposal.filming_licence_charge_type == proposal.NON_STANDARD_CHARGE:
            licence_fee = proposal.filming_non_standard_charge
            licence_text = "Non-standard charge"
        else:
            raise Exception("Unknown filming charge type")

    application_fee = proposal.application_type.application_fee
    filming_period = "{} - {}".format(
        proposal.filming_activity.commencement_date,
        proposal.filming_activity.completion_date,
    )

    lines_app = [
        {
            "ledger_description": "{} Application Fee - {}".format(
                desc, proposal.lodgement_number
            ),
            "oracle_code": proposal.application_type.oracle_code_application,
            "price_incl_tax": str(application_fee),
            #'price_excl_tax':  str(application_fee) if proposal.application_type.is_gst_exempt else str(calculate_excl_gst(application_fee)),
            "quantity": 1,
        }
    ]
    lines_parks_aggregated = [
        {
            "ledger_description": "{} Licence Fee ({} - {}) - {}".format(
                desc, licence_text, filming_period, proposal.lodgement_number
            ),
            "oracle_code": proposal.application_type.oracle_code_licence,  # this line is dummy, for aggregated (externally generated) invoice
            "price_incl_tax": str(licence_fee),
            #'price_excl_tax':  str(licence_fee) if proposal.application_type.is_gst_exempt else str(calculate_excl_gst(licence_fee)),
            "quantity": 1,
        }
    ]
    lines_aggregated = lines_app + lines_parks_aggregated
    lines = lines_app + create_filming_park_fee_lines(
        proposal, licence_fee, licence_text, filming_period
    )
    return lines, lines_aggregated


def create_lines(request, invoice_text=None, vouchers=[], internal=False):
    """Create the ledger lines - line items for invoice sent to payment system"""

    def add_line_item(park, arrival, age_group, price, no_persons):
        # price = Decimal(price)
        price = round(float(price), 2)
        # if no_persons > 0 or (same_tour_group and no_persons >= 0):
        if no_persons > 0:
            return {
                "ledger_description": "{} - {} - {}".format(
                    park.name, arrival, age_group
                ),
                "oracle_code": park.oracle_code(ApplicationType.TCLASS),
                "price_incl_tax": price,
                #'price_excl_tax':  price if park.is_gst_exempt else round(float(calculate_excl_gst(price)), 2),
                "quantity": no_persons,
            }
        return None

    lines = []
    tbody = json.loads(request.POST["payment"])["tbody"]
    for row in tbody:
        park_id = row[0]["value"]
        arrival = row[1]
        same_tour_group = True if row[2] else False
        no_adults = int(row[3]) if row[3] else 0
        no_children = int(row[4]) if row[4] else 0
        no_free_of_charge = int(row[5]) if row[5] else 0
        park = Park.objects.get(id=park_id)

        # same tour group visitors
        no_adults_same_tour = (
            int(row[7]) if (row[7] != "" and row[7] is not None) else None
        )
        no_children_same_tour = (
            int(row[8]) if (row[8] != "" and row[8] is not None) else None
        )
        no_free_of_charge_same_tour = (
            int(row[9]) if (row[9] != "" and row[9] is not None) else None
        )

        # no_adults = no_adults if no_adults_same_tour==0 else no_adults_same_tour
        # no_children = no_children if no_children_same_tour==0 else no_children_same_tour
        # no_free_of_charge = no_free_of_charge if no_free_of_charge_same_tour==0 else no_free_of_charge_same_tour

        if same_tour_group and no_adults_same_tour is not None:
            if no_adults_same_tour > 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Adult (Same Tour Group, Total {})".format(no_adults),
                        price=park.adult_price,
                        no_persons=no_adults_same_tour,
                    )
                )
            elif no_adults_same_tour == 0 and no_adults != 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Adult (Same Tour Group, Total {})".format(no_adults),
                        price=0.0,
                        no_persons=no_adults,
                    )
                )
        elif no_adults > 0:
            lines.append(
                add_line_item(
                    park, arrival, "Adult", price=park.adult_price, no_persons=no_adults
                )
            )

        if same_tour_group and no_children_same_tour is not None:
            if no_children_same_tour > 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Child (Same Tour Group, Total {})".format(no_children),
                        price=park.child_price,
                        no_persons=no_children_same_tour,
                    )
                )
            elif no_children_same_tour == 0 and no_children != 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Child (Same Tour Group, Total {})".format(no_children),
                        price=0.0,
                        no_persons=no_children,
                    )
                )
        elif no_children > 0:
            lines.append(
                add_line_item(
                    park,
                    arrival,
                    "Child",
                    price=park.child_price,
                    no_persons=no_children,
                )
            )

        if same_tour_group and no_free_of_charge_same_tour is not None:
            if no_free_of_charge_same_tour > 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Free (Same Tour Group, Total {})".format(no_free_of_charge),
                        price=0.0,
                        no_persons=no_free_of_charge_same_tour,
                    )
                )
            elif no_free_of_charge_same_tour == 0 and no_free_of_charge != 0:
                lines.append(
                    add_line_item(
                        park,
                        arrival,
                        "Free (Same Tour Group, Total {})".format(no_free_of_charge),
                        price=0.0,
                        no_persons=no_free_of_charge,
                    )
                )
        elif no_free_of_charge > 0:
            lines.append(
                add_line_item(
                    park, arrival, "Free", price=0.0, no_persons=no_free_of_charge
                )
            )

    return lines


# def create_filmingfee_lines(request, proposal, invoice_text=None, vouchers=[], internal=False):
#
#    if proposal.filming_activity.num_filming_days == 1:
#        licence_fee = proposal.application_type.filming_fee_full_day if 'motion_film' in proposal.filming_activity.film_type else proposal.application_type.photography_fee_full_day
#        licence_text =  'Full day'
#    elif proposal.filming_activity.num_filming_days > 1 and proposal.filming_activity.num_filming_days < 4:
#        full_day_fee = proposal.application_type.filming_fee_full_day if 'motion_film' in proposal.filming_activity.film_type else proposal.application_type.photography_fee_full_day
#        subsequent_day_fee = proposal.application_type.filming_fee_subsequent_day if 'motion_film' in proposal.filming_activity.film_type else proposal.application_type.photography_fee_subsequent_day
#        licence_fee = full_day_fee + (subsequent_day_fee * (proposal.filming_activity.num_filming_days-1))
#        licence_text = '{} days'.format(proposal.filming_activity.num_filming_days)
#    elif proposal.filming_activity.num_filming_days >= 4:
#        licence_fee = proposal.application_type.filming_fee_4days if 'motion_film' in proposal.filming_activity.film_type else proposal.application_type.photography_fee_full_4days
#        licence_text = '4 days or more'.format(proposal.filming_activity.num_filming_days)
#
#    application_fee = proposal.application_type.application_fee
#    filming_period = '{} - {}'.format(proposal.filming_activity.commencement_date, proposal.filming_activity.completion_date)
#
#    lines = [
#        {
#            'ledger_description': 'Filming/Photography Application Fee - {}'.format(proposal.lodgement_number),
#            'oracle_code': proposal.application_type.oracle_code_licence,
#            'price_incl_tax':  application_fee,
#            'price_excl_tax':  application_fee if proposal.application_type.is_gst_exempt else calculate_excl_gst(application_fee),
#            'quantity': 1
#        },
#        {
#            'ledger_description': 'Filming/Photography Licence Fee ({} - {}) - {}'.format(licence_text, filming_period, proposal.lodgement_number),
#            'oracle_code': proposal.application_type.oracle_code_licence,
#            'price_incl_tax':  licence_fee,
#            'price_excl_tax':  licence_fee if proposal.application_type.is_gst_exempt else calculate_excl_gst(licence_fee),
#            'quantity': 1
#        },
#    ]
#
#    return lines


def get_basket(request):
    return get_cookie_basket(settings.OSCAR_BASKET_COOKIE_OPEN, request)


def checkout(
    request,
    proposal,
    lines,
    return_url_ns="public_booking_success",
    return_preload_url_ns="public_booking_success",
    invoice_text=None,
    vouchers=[],
    proxy=False,
):
    basket_params = {
        "products": lines,
        "vouchers": vouchers,
        "system": settings.PAYMENT_SYSTEM_ID,
        "custom_basket": True,
    }

    basket, basket_hash = create_basket_session(request, basket_params)
    # fallback_url = request.build_absolute_uri('/')
    checkout_params = {
        "system": settings.PAYMENT_SYSTEM_ID,
        "fallback_url": request.build_absolute_uri(
            "/"
        ),  # 'http://mooring-ria-jm.dbca.wa.gov.au/'
        "return_url": request.build_absolute_uri(
            reverse(return_url_ns)
        ),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        "return_preload_url": request.build_absolute_uri(
            reverse(return_url_ns)
        ),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        #'fallback_url': fallback_url,
        #'return_url': fallback_url,
        #'return_preload_url': fallback_url,
        "force_redirect": True,
        #'proxy': proxy,
        "invoice_text": invoice_text,  # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
        #'invoice_reference': '05572565342',
    }
    #    if not internal:
    #        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    # if internal or request.user.is_anonymous():
    if proxy or request.user.is_anonymous():
        # checkout_params['basket_owner'] = booking.customer.id
        checkout_params["basket_owner"] = proposal.submitter_id

    create_checkout_session(request, checkout_params)

    #    if internal:
    #        response = place_order_submission(request)
    #    else:
    response = HttpResponseRedirect(reverse("checkout:index"))
    # inject the current basket into the redirect response cookies
    # or else, anonymous users will be directionless
    response.set_cookie(
        settings.OSCAR_BASKET_COOKIE_OPEN,
        basket_hash,
        max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
        secure=settings.OSCAR_BASKET_COOKIE_SECURE,
        httponly=True,
    )

    #    if booking.cost_total < 0:
    #        response = HttpResponseRedirect('/refund-payment')
    #        response.set_cookie(
    #            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
    #            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
    #            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
    #        )
    #
    # Zero booking costs
    # if booking.cost_total < 1 and booking.cost_total > -1:
    # if invoice_text == 'Application Fee' and proposal.application_type.name=='T Class' and proposal.org_applicant and proposal.allow_full_discount:
    if invoice_text == "Application Fee" and proposal.allow_full_discount:
        response = HttpResponseRedirect(reverse("zero_fee_success"))
        response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN,
            basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE,
            httponly=True,
        )

    return response


def checkout_existing_invoice(
    request,
    invoice,
    lines,
    return_url_ns="public_booking_success",
    return_preload_url_ns="public_booking_success",
    invoice_text=None,
    vouchers=[],
    proxy=False,
):
    basket_params = {
        #'products': invoice.order.basket.lines.all(),
        "products": lines,
        "vouchers": vouchers,
        "system": settings.PAYMENT_SYSTEM_ID,
        "custom_basket": True,
    }

    basket, basket_hash = use_existing_basket_from_invoice(invoice.reference)
    checkout_params = {
        "system": settings.PAYMENT_SYSTEM_ID,
        "fallback_url": request.build_absolute_uri("/"),
        "return_url": request.build_absolute_uri(reverse(return_url_ns)),
        "return_preload_url": request.build_absolute_uri(reverse(return_url_ns)),
        "force_redirect": True,
        "invoice_text": invoice.text,
    }

    create_checkout_session(request, checkout_params)

    # response = HttpResponseRedirect(reverse('checkout:index'))
    # use HttpResponse instead of HttpResponseRedirect - HttpResonseRedirect does not pass cookies which is important for ledger to get the correct basket
    response = HttpResponse(
        "<script> window.location='"
        + reverse("checkout:index")
        + "';</script> <a href='"
        + reverse("checkout:index")
        + "'> Redirecting please wait: "
        + reverse("checkout:index")
        + "</a>"
    )

    # inject the current basket into the redirect response cookies
    # or else, anonymous users will be directionless
    response.set_cookie(
        settings.OSCAR_BASKET_COOKIE_OPEN,
        basket_hash,
        max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
        secure=settings.OSCAR_BASKET_COOKIE_SECURE,
        httponly=True,
    )

    return response


def oracle_integration(date, override):
    system = "0557"
    oracle_codes = oracle_parser(
        date, system, "Commercial Operator Licensing", override=override
    )


def redirect_to_zero_payment_view(request, proposal, lines):
    """
    redirect to Zero Payment preview, instead of Credit Card checkout view
    """
    template_name = "leaseslicensing/booking/preview.html"

    if proposal.allow_full_discount:
        logger.info(
            "{} built payment line item {} for Application Fee and handing over to ZERO Payment preview".format(
                "User {} with id {}".format(
                    proposal.submitter.get_full_name(), proposal.submitter.id
                ),
                proposal.id,
            )
        )
        basket = createCustomBasket(lines, request.user, settings.PAYMENT_SYSTEM_ID)
        context = {
            "basket": basket,
            "lines": basket.lines.all(),
            "line_details": basket.lines.all(),  # request.POST['payment'],
            "proposal_id": proposal.id,
            "payment_method": "ZERO",
            "redirect_url": reverse("zero_fee_success"),
        }
        return render(request, template_name, context)


def test_create_invoice(payment_method="bpay"):
    """
    This will create and invoice and order from a basket bypassing the session
    and payment bpoint code constraints.

    To test:
            from ledger.payments.invoice.utils import test_create_invoice


            from ledger.checkout.utils import createCustomBasket
            from ledger.payments.invoice.utils import CreateInvoiceBasket
            from decimal import Decimal

            products = [{u'oracle_code': u'ABC123 GST', u'price_incl_tax': Decimal('10.00'), u'price_excl_tax': Decimal('9.090909090909'), u'ledger_description': u'Booking Date 2019-09-24: Neale Junction Nature Reserve - 2019-09-24 - Adult', u'quantity': 1}]
            or
            products = Booking.objects.last().as_line_items

            user = EmailUser.objects.get(email__icontains='walter.genuit@dbca')
            payment_method = 'bpay' (or 'monthly_invoicing')

            basket  = createCustomBasket(products, user, 'S557', bpay_allowed=True, monthly_invoicing_allowed=True)
            order = CreateInvoiceBasket(payment_method='bpay', system='0557').create_invoice_and_order(basket, 0, None, None, user=user, invoice_text='CIB7')

            Invoice.objects.get(order_number=order.number)
            <Invoice: Invoice #05572188633>

            To view:
                    http://localhost:8499/ledger/payments/invoice/05572188633

    """
    from ledger.checkout.utils import createCustomBasket
    from ledger.payments.invoice.utils import CreateInvoiceBasket
    from ledger.accounts.models import EmailUser
    from decimal import Decimal

    products = [
        {
            "oracle_code": "ABC123 GST",
            "price_incl_tax": Decimal("10.00"),
            "price_excl_tax": Decimal("9.090909090909"),
            "ledger_description": "Neale Junction Nature Reserve - 2019-09-24 - Adult",
            "quantity": 1,
        }
    ]
    # products = Booking.objects.last().as_line_items

    user = EmailUser.objects.get(email="jawaid.mushtaq@dbca.wa.gov.au")
    # payment_method = 'bpay'
    payment_method = "monthly_invoicing"

    basket = createCustomBasket(products, user, "S557")
    order = CreateInvoiceBasket(
        payment_method=payment_method, system="0557"
    ).create_invoice_and_order(basket, 0, None, None, user=user, invoice_text="CIB7")
    print("Created Order: {}".format(order.number))
    print("Created Invoice: {}".format(Invoice.objects.get(order_number=order.number)))

    return order


def create_invoice(booking, payment_method="bpay"):
    """
    This will create and invoice and order from a basket bypassing the session
    and payment bpoint code constraints.
    """
    from ledger.checkout.utils import createCustomBasket
    from ledger.payments.invoice.utils import CreateInvoiceBasket
    from ledger.accounts.models import EmailUser
    from decimal import Decimal

    # products = Booking.objects.last().as_line_items
    products = booking.as_line_items
    try:
        user = EmailUser.objects.get(email=booking.proposal.applicant_email.lower())
    except Exception:
        user = EmailUser.objects.get(email=booking.proposal.submitter.email.lower())

    if payment_method == "monthly_invoicing":
        invoice_text = "Monthly Payment Invoice"
    elif payment_method == "bpay":
        invoice_text = "BPAY Payment Invoice"
    else:
        invoice_text = "Payment Invoice"

    basket = createCustomBasket(products, user, settings.PAYMENT_SYSTEM_ID)
    order = CreateInvoiceBasket(
        payment_method=payment_method, system=settings.PAYMENT_SYSTEM_PREFIX
    ).create_invoice_and_order(
        basket, 0, None, None, user=user, invoice_text=invoice_text
    )

    return order
