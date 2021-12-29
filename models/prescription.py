from odoo import api, fields, models, _
from odoo.exceptions import UserError




class ACSPrescriptionOrder(models.Model):
    _inherit='prescription.order'

    external_medicine_ids = fields.One2many('external.medicine.line', 'prescription_id', string='External Medicine')
    test_ids = fields.One2many('lab.test.prescription', 'prescription_id', string='Lab Test')
    suggestion_ids = fields.Many2many('doctor.suggestion', string="Suggestion")
    follow_up_date = fields.Date(string="Next Follow-up")


class ACSPrescriptionOrderLine(models.Model):
    _inherit='prescription.line'

    @api.onchange('dose','days')
    def _get_total_qty(self):
        for rec in self:
            rec.quantity = rec.days * rec.dose


class ExternalMedicine(models.Model):
    _name = 'external.medicine'

    name = fields.Char("External Medicine")


class ExternalMedicineLine(models.Model):
    _name = 'external.medicine.line'

    prescription_id = fields.Many2one('prescription.order', ondelete="cascade", string='Prescription ID', )
    external_medicine_id = fields.Many2one('external.medicine', ondelete="cascade", string='External Medicine', required=True)
    allow_substitution = fields.Boolean(string='Allow Substitution')
    active_component_ids = fields.Many2many('active.comp','product_pres_ext_comp_rel','product_id','pres_id','Active Component')
    quantity = fields.Float(string='Total Qty', compute="_get_total_qty")
    common_dosage = fields.Many2one('medicament.dosage', ondelete="cascade", string='Dosage/Frequency', help='Drug form, such as tablet or gel')
    short_comment = fields.Char(string='Comment', help='Short comment on the specific drug')
    days = fields.Integer(string="Days")
    dose = fields.Integer(string="Qty Dose")
    qty_per_day = fields.Integer(string="Qty Per Day")

    @api.depends('dose','days')
    @api.onchange('dose','days')
    def _get_total_qty(self):
        for rec in self:
            rec.quantity = rec.days * rec.dose

class LabTestPrescription(models.Model):
    _name = 'lab.test.prescription'

    prescription_id = fields.Many2one('prescription.order', ondelete="cascade", string='Prescription ID', )
    labtest_id = fields.Many2one('acs.lab.test', string='Test')
    note = fields.Char(string='Note')



class DoctorsSuggestion(models.Model):
    _name = 'doctor.suggestion'

    name = fields.Char("Suggestion")