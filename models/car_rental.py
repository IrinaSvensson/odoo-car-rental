from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    car_id = fields.Many2one(
        "car.rental.car",
        string="Car",
    )


class CarRentalCar(models.Model):
    _name = "car.rental.car"
    _description = "Car available for rental"
    _inherit = "image.mixin"

    name = fields.Char(string="Car Name", required=True)
    license_plate = fields.Char(string="License Plate", required=True)
    daily_price = fields.Float(string="Daily Price", required=True)
    active = fields.Boolean(string="Active", default=True)
    image_1920 = fields.Image()

    booking_ids = fields.One2many(
        "car.rental.booking",
        "car_id",
        string="Bookings",
    )

    move_ids = fields.One2many(
        "account.move",
        "car_id",
        string="Invoices",
    )

    _sql_constraints = [
        (
            "license_plate_unique",
            "unique(license_plate)",
            "License Plate must be unique.",
        ),
    ]

    def open_create_wizard(self):
        """Öppna wizard för fakturering."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Skapa Faktura",
            "res_model": "create.invoice.wizard.car.rental",
            "target": "new",
            "view_mode": "form",
            "view_type": "form",
            "context": {
                "default_car_id": self.id,
            },
        }


class CarRentalBooking(models.Model):
    _name = "car.rental.booking"
    _description = "Car Rental Booking"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Booking Reference",
        required=True,
        copy=False,
        compute="_compute_name",
    )

    car_id = fields.Many2one(
        "car.rental.car",
        string="Car",
        required=True,
    )

    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        readonly=True,
    )

    image_1920 = fields.Image(related="car_id.image_1920")

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
    )

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    days = fields.Integer(
        string="Days",
        compute="_compute_days",
        store=True,
    )

    price_total = fields.Float(
        string="Total Price",
        compute="_compute_price_total",
        store=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
    )

    paid = fields.Boolean(
        string="Paid",
        default=False,
    )

    notes = fields.Text(string="Notes")

    @api.depends("car_id.license_plate", "start_date", "end_date")
    def _compute_name(self):
        for rec in self:
            rec.name = "New Booking"
            if rec.car_id and rec.start_date and rec.end_date:
                rec.name = (
                f"{rec.car_id.license_plate}-"
                f"{rec.start_date.strftime('%y%m%d')}/"
                f"{rec.end_date.strftime('%y%m%d')}"
            )

    @api.depends("start_date", "end_date")
    def _compute_days(self):
        """Beräkna antal dagar, eller 0 om datum saknas/ogiltiga."""
        for rec in self:
            rec.days = 0
            if rec.start_date and rec.end_date:
                # gör om sträng -> date-objekt
                start = fields.Date.to_date(rec.start_date)
                end = fields.Date.to_date(rec.end_date)
                if end >= start:
                    rec.days = (end - start).days + 1

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start = fields.Date.to_date(rec.start_date)
                end = fields.Date.to_date(rec.end_date)
                if end < start:
                    raise ValidationError(
                        _("End Date cannot be before Start Date.")
                    )

    @api.depends("days", "car_id.daily_price")
    def _compute_price_total(self):
        for rec in self:
            rec.price_total = rec.days * (rec.car_id.daily_price or 0.0)

    @api.constrains("car_id", "start_date", "end_date")
    def _check_car_availability(self):
        for rec in self:
            if not rec.car_id or not rec.start_date or not rec.end_date:
                continue

            overlapping = self.search(
                [
                    ("id", "!=", rec.id),  # inte samma bokning
                    ("car_id", "=", rec.car_id.id),  # samma bil
                    (
                        "state",
                        "in",
                        ["draft", "confirmed", "done"],
                    ),  # aktiva bokningar
                    ("start_date", "<=", rec.end_date),  # överlappning
                    ("end_date", ">=", rec.start_date),
                ]
            )

            if overlapping:
                raise ValidationError(
                    _("This car is already booked for the selected period!")
                )
