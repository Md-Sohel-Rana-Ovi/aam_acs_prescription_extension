# -*- coding: utf-8 -*-

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta


class StoreRequisition(models.Model):
    _name = "store.requisition"
    _description = "Store Requisition"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    department_id = fields.Many2one("hr.department", string="Department",
                                    default=lambda self: self.env.user.employee_id.department_id.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.user.employee_id.id)
    requsition_line_ids = fields.One2many('store.requisition.line', 'store_requisition_id', string='Lines')
    approved_by = fields.Many2one("res.users", string="Approved by")
    approved_date = fields.Date("Approved On")
    confirmed_by = fields.Many2one("res.users", string="Confirmed by")
    confirmed_date = fields.Date("Confirmed On")
    transfered_by = fields.Many2one("res.users", string="Transfered by")
    transfered_date = fields.Date("Transfered On")
    rejected_by = fields.Many2one("res.users", string="Rejected by")
    rejected_date = fields.Date("Rejected On")
    state = fields.Selection([('draft', 'Draft'),
                              ('request', 'Requested'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('transfer', 'Transfered'),
                              ('partial', 'Partially Transfered'),
                              ('reject', 'Rejected')], string="Status", default='draft')

    transfer_type = fields.Selection([('full', "Complete Transfer"), ('partial', 'Partial Transfer')],
                                     string="Transfer Type", default='full')

    picking_count = fields.Integer(string='Transfer',
                                   compute='_compute_picking_ids',
                                   readonly=True,
                                   )

    def action_view_transfer(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        transfer_ids = self.env['stock.picking'].search([('store_requisition_id', '=', self.id)]).ids
        action['domain'] = [('id', 'in', transfer_ids)]
        return action

    def _compute_picking_ids(self):
        for item in self:
            item.picking_count = self.env['stock.picking'].search_count([('store_requisition_id', '=', self.id)])

    def request(self):
        self.state = "request"

    def confirm(self):
        self.state = "confirm"
        self.confirmed_by = self.env.user.id
        self.confirmed_date = date.today()

    def approve(self):
        self.state = "approve"
        self.approved_by = self.env.user.id
        self.approved_date = date.today()

    def prepare_transfer(self):
        for line in self.requsition_line_ids:
            line.quantity_inprogress = line.quantity - line.quantity_done
            if line.quantity_inprogress > line.available_qty:
                line.quantity_inprogress = line.available_qty

        return {
            'name': _('Transfer Control'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'store.requisition',
            'view_id': self.env.ref('aam_requisition.aam_requisition_view_wizard').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }

    def transfer(self):
        self.transfered_by = self.env.user.id
        self.transfered_date = date.today()

        destination_location = self.env.ref('aam_requisition.store_requisition_location').id
        source_location = self.env.ref('stock.stock_location_stock').id
        warehouse_id = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1)
        picking_id = self.env['stock.picking'].create({
            'partner_id': self.employee_id.user_id.partner_id.id,
            'origin': self.name,
            'location_id': source_location,
            'location_dest_id': destination_location,
            'picking_type_id': warehouse_id.out_type_id.id,
            'store_requisition_id': self.id,
        })
        check_partial = False
        for line in self.requsition_line_ids:
            move_id = self.env['stock.move'].create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity_inprogress,
                'reserved_availability': line.quantity_inprogress,
                'quantity_done': line.quantity_inprogress,
                'product_uom': line.uom_id.id,
                'picking_id': picking_id.id,
                'location_id': source_location,
                'location_dest_id': destination_location,
            })
            line.quantity_done = line.quantity_done + line.quantity_inprogress
            if line.quantity_done != line.quantity:
                check_partial = True

        picking_id.button_validate()

        if check_partial:
            self.state = "partial"
        else:
            self.state = "transfer"
        self.transfered_by = self.env.user.id
        self.transfered_date = date.today()

    def reject(self):
        self.state = "reject"
        self.rejected_by = self.env.user.id
        self.rejected_date = date.today()

    @api.model
    def create(self, values):
        if values.get('name', '/') == '/':
            values['name'] = self.env['ir.sequence'].next_by_code(
                'store.requisition')
        return super(StoreRequisition, self).create(values)

    def unlink(self):
        if self.filtered(lambda r: r.state != 'draft'):
            raise UserError(_('Only requests on draft state can be unlinked'))
        return super(StoreRequisition, self).unlink()


class StoreRequisitionLine(models.Model):
    _name = "store.requisition.line"
    _description = "Store Requisition Line"

    product_id = fields.Many2one("product.product", string="Product")
    uom_id = fields.Many2one("uom.uom", string="Unit(s)")
    quantity = fields.Integer("Quantity")
    quantity_inprogress = fields.Integer("Quantity In-Progress")
    quantity_done = fields.Integer("Quantity Done")
    available_qty = fields.Integer("Available Qty", compute="get_available_qty")
    store_requisition_id = fields.Many2one('store.requisition', string="Requisition")

    def get_available_qty(self):
        for item in self:
            if item.product_id:
                item.available_qty = item.product_id.qty_available

    @api.onchange('product_id')
    def onchange_product_id(self):
        for item in self:
            if item.product_id:
                item.uom_id = item.product_id.uom_id.id


class StockPicking(models.Model):
    _inherit = "stock.picking"

    store_requisition_id = fields.Many2one('store.requisition', string="Requisition")
