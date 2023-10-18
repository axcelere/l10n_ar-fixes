import base64
import logging
from io import BytesIO

from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class ResCompanyJurisdictionPadron(models.Model):
    _inherit = "res.company.jurisdiction.padron"
    _description = "res.company.jurisdiction.padron"

    pdf_filename = fields.Char("PDF Filename")

    @api.constrains('jurisdiction_id')
    def check_jurisdiction_id(self):
        pass
        # arba_tag = self.env.ref('l10n_ar_ux.tag_tax_jurisdiccion_902')
        # for rec in self:
        #     if rec.jurisdiction_id != arba_tag:
        #         raise ValidationError("El padron para (%s) no está implementado." % rec.jurisdiction_id.name)

    def generate_alicuota_fromzip(self):
        # 26092023;01102023;31102023;20000163989;D;S;N;0,00;0,00;00;00;ETCHEVERRIGARAY JUAN  CARLOS
        # fecha;fecha_inicio;fecha_fin;vat;D;S;N;alicuota_percepcion;alicuota_retencion
        Alicuot = self.env['res.partner.arba_alicuot']
        Partner = self.env['res.partner']
        self.descompress_file(self.file_padron)
        filename = self.pdf_filename.replace('.zip', '')
        path_file = "/tmp/%s/%s.txt" % (filename, filename)
        with open(path_file, "r") as fp:
            for line in fp.readlines():
                values = line.split(";")
                partner_id = Partner.search([('vat', '=', values[3])], limit=1)
                if partner_id:
                    vals = {
                        'numero_comprobante': '',
                        'alicuota_percepcion': values[7].replace(",", "."),
                        'alicuota_retencion': values[8].replace(",", "."),
                        'partner_id': partner_id.id,
                        'company_id': self.company_id.id,
                        'tag_id': self.jurisdiction_id.id,
                        'from_date': self.l10n_ar_padron_from_date,
                        'to_date': self.l10n_ar_padron_to_date,
                    }
                    Alicuot.create(vals)

    def generate_alicuota(self):
        stream = BytesIO(base64.b64decode(self.file_padron)).read()
        total_len = len(str(stream).split("\\r\\n")) - 1
        cant = 0
        for line in str(stream).split("\\r\\n"):
            cant += 1
            if cant <= total_len:
                values = line.split(";")
                partner_id = self.env['res.partner'].search([('vat', '=', values[4])], limit=1)
                if partner_id:
                    vals = {
                        'numero_comprobante': '',
                        # 'alicuota_retencion': float(alicuot_ret),
                        'alicuota_percepcion': values[8].replace(",", "."),
                        'partner_id': partner_id.id,
                        'company_id': self.company_id.id,
                        'tag_id': self.jurisdiction_id.id,
                        'from_date': self.l10n_ar_padron_from_date,
                        'to_date': self.l10n_ar_padron_to_date,
                    }
                    self.env['res.partner.arba_alicuot'].create(vals)
