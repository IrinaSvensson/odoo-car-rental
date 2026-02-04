from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)

class CreateInvoiceWizardCarRental(models.TransientModel):
    _name = 'create.invoice.wizard.car.rental'
    _description = "Car Rental Invoice Wizard"

    car_id = fields.Many2one('car.rental.car', string="Bil")
    from_date = fields.Date(string="Från datum", required=True)
    to_date = fields.Date(string="Till datum", required=True)

    def action_create_invoice(self):

        """Här kommer fakturalogiken."""

        # Get booking lines connect to the car
        # Filter on date from and to

        bookings = self.env['car.rental.booking'].search([ # en lista med alla bokningar som ska faktureras
        ('car_id','=',self.car_id.id),
        ("start_date",'>=',self.from_date),
        ("end_date",'<=',self.to_date)
        ])

        _logger.warning(f"test {bookings=}") # skriver ut vilka bokningar hittades

        for booking in bookings: # loopar igenom varje bokning en i taget

            inv = self.env['account.move'].create({ # skapar en faktura i modellen account.move
            'partner_id':booking.customer_id.id, # kunden hämtas från bokningen
            'date':booking.start_date, # fakturadatum samma som bokningens startdatum
            'move_type':"out_invoice", # kundfaktura
            'car_id':booking.car_id.id # bilen som fakturan gäller
            #'line_id':[(0,0,{})]
            })

            # get number of days between booking.start_date and booking.end_date

            days = (booking.end_date - booking.start_date).days + 1

            #  KOPPLA BOKNINGEN TILL FAKTURAN

            booking.invoice_id = inv

            inv_line = self.env['account.move.line'].create({ # skapar en fakturarad kopplad till fakturan
            'move_id':inv.id, # vilken faktura raden ska hamna i
            'quantity':booking.days, # räkna hur många dagar det är mellan från och till
            'price_unit':booking.car_id.daily_price, # pris per dag
            'name':booking.name or "Car rental", # vet inte om det bra att ha
            })

            _logger.warning(f"{inv=}") # loggar den skapade fakturan
        return True


