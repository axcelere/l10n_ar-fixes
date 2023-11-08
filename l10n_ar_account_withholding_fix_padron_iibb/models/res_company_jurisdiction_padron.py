import base64
import logging
import os
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

    def _condition_toclean_line(self, line, partners_vat):
        return ";0,00;0,00;00;00;" in line

    def generate_alicuota_fromzip(self):
        # 26092023;01102023;31102023;20000163989;D;S;N;0,00;0,00;00;00;ETCHEVERRIGARAY JUAN  CARLOS
        # fecha;fecha_inicio;fecha_fin;vat;D;S;N;alicuota_percepcion;alicuota_retencion
        Alicuot = self.env['res.partner.arba_alicuot']
        self.descompress_file(self.file_padron)
        filename = self.pdf_filename.replace('.zip', '')
        path_file = "/tmp/%s/%s.txt" % (filename, filename)
        temp_path_file = "/tmp/%s/%s_temp.txt" % (filename, filename)

        partners = self.env['res.partner'].search([('is_company', '=', True)])
        partners_vat = partners.mapped('vat')
        partner_dict = {partner.vat: partner.id for partner in partners}

        with open(path_file, "r", errors="replace") as input_f:
            lines_to_keep = [line for line in input_f if not self._condition_toclean_line(line, partners_vat)]

        with open(temp_path_file, "w", errors="replace") as output_f:
            output_f.writelines(lines_to_keep)

        os.replace(temp_path_file, path_file)

        with open(path_file, "r", errors="replace") as fp:
            line_number = 1
            bulk_vals = []
            for line_bytes in fp:
                line = line_bytes.strip()
                _logger.log(25, line)
                _logger.log(25, "************LINEA %s************" % str(line_number))
                line_number += 1
                values = line.split(";")
                partner_id = partner_dict.get(values[3], False)
                if partner_id:
                    bulk_vals.append({
                        'numero_comprobante': '',
                        'alicuota_percepcion': values[7].replace(",", "."),
                        'alicuota_retencion': values[8].replace(",", "."),
                        'partner_id': partner_id,
                        'company_id': self.company_id.id,
                        'tag_id': self.jurisdiction_id.id,
                        'from_date': self.l10n_ar_padron_from_date,
                        'to_date': self.l10n_ar_padron_to_date,
                    })
                    _logger.log(25, "Nueva alicuota a partner: %s" % partner_id)
            Alicuot.sudo().create(bulk_vals)
            return True

    def generate_alicuota(self):
        stream = BytesIO(base64.b64decode(self.file_padron)).read()
        total_len = len(str(stream).split("\\r\\n")) - 1
        cant = 0
        for line in str(stream).split("\\r\\n"):
            cant += 1
            values = line.split(";")
            if cant <= total_len and len(values) >= 8:
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
