# Copyright 2018 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class RequisitionConfigSettings(models.Model):
    _inherit = 'requisition.config.settings'


    aam_source_location_id = fields.Many2one('stock.location', string="Store Location", domain=[('usage','=','internal')])
    aam_employee_location_id = fields.Many2one('stock.location', string="Employee Location", domain=[('usage','=','customer')])
