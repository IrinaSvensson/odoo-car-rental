from odoo import http, _
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CarBookingWebsite(http.Controller):

    @http.route(
        '/cars',
        type='http',
        auth='public',
        website=True,
    )
    def car_list(self, **kwargs):
        """Visa alla bilar på webben"""
        cars = request.env['car.rental.car'].sudo().search([('active', '=', True)])
        return request.render(
            'car_booking.car_rental_car_website_list',
            {'cars': cars}
        )

    @http.route(
        '/cars/book/<int:car_id>',
        type='http',
        auth='user',          # kräver inloggad användare
        website=True,
        methods=['GET', 'POST'],
        csrf=True,
    )
    def car_booking(self, car_id, **post):
        """Visa formulär (GET) eller skapa bokning (POST)"""
        car = request.env['car.rental.car'].sudo().browse(car_id).exists()
        if not car:
            return request.redirect('/cars')

        # 1) GET -> visa formuläret
        if request.httprequest.method == 'GET':
            return request.render(
                'car_booking.car_rental_booking_form',
                {'car': car}
            )

        # 2) POST -> skapa bokning
        partner = request.env.user.partner_id.sudo()


        start_date = post.get("start_date")
        end_date = post.get("end_date")
        notes = post.get("notes")

        booking_vals = {
            'car_id': car.id,
            'customer_id': partner.id,
            'start_date': post.get('start_date'),
            'end_date': post.get('end_date'),
            'notes': post.get('notes'),
        }
        _logger.info("### Creating car.rental.booking with vals: %s", booking_vals)

        booking = request.env['car.rental.booking'].sudo().create(booking_vals)

        return request.render(
            'car_booking.car_rental_booking_thanks',
            {'booking': booking, 'car': car}
        )

    @http.route(
        '/my/car_bookings',
        type='http',
        auth='user',      # kräver inloggad användare
        website=True,
    )
    def my_car_bookings(self, **kwargs):
        """Visa lista över bokningar för inloggad användare."""
        partner = request.env.user.partner_id.sudo()
        bookings = request.env['car.rental.booking'].sudo().search(
            [('customer_id', '=', partner.id)],
            order="start_date desc, id desc",
        )
        values = {
            'bookings': bookings,
            'partner': partner,
        }
        return request.render('car_booking.car_rental_my_bookings', values)

    @http.route(
        '/my/car_bookings/pay/<int:booking_id>',
        type='http',
        auth='user',
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def my_car_bookings_pay(self, booking_id, **kwargs):
        """Markera en bokning som betald (demo)."""
        Booking = request.env['car.rental.booking'].sudo()
        booking = Booking.browse(booking_id).exists()
        partner = request.env.user.partner_id

        # Säkerhet: bara ägaren får uppdatera
        if not booking or booking.customer_id.id != partner.id:
            return request.redirect('/my/car_bookings')

        booking.write({
            'paid': True,
            'state': 'confirmed',
        })

        return request.redirect('/my/car_bookings')
