# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2025 Vertel AB info@vertel.se
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

#
# https://www.odoo.com/documentation/19.0/reference/module.html
#
{
    'name': 'Car Rental',
    'version': '1.0',
    'summary': "Allow customers to book and rent cars directly from your website",
    'category': 'Sales',
    # 'icon': 'static/description/icon.png',
    'description': """
    Car Rental – Online car booking for your website

    Funktioner:
    - Visa tillgängliga bilar på webbplatsen (modell, registreringsnummer, kategori m.m.)
    - Kund kan välja datum/tid, bil och eventuella tillval
    - Skapar offert eller försäljningsorder automatiskt vid bokning
    - Hantering av status (bokad, utlämnad, återlämnad, avbokad)
    - Integration med Odoo Försäljning / Invoicing för fakturering av hyran
    - Enkel konfiguration av prislistor (per dag, vecka, månad, extra kilometer osv.)

    - Den här modulen är tänkt som ett exempel/projekt och kan byggas ut med:
    - Integration med Fleet/Rental (fordonshantering)
    - Kalenderöversikt för bokningar
    - Automation (påminnelser via e-post/SMS inför hämtning och återlämning)
    """,

    'author': 'Vertel AB',
    'website': 'https://vertel.se',
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',

    'depends': [
        'base',
        'website',
        'contacts',
        'mail',
        'sale',              # för offert/försäljningsorder
        'sale_management',   # extra säljfunktioner (offerter etc.)
        'account',           # för fakturering
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'wizard/wizard_views.xml',
        'data/car_data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
