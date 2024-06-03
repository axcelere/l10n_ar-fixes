from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _compute_amount(self, base_amount, price_unit, quantity=1.0, product=None, partner=None, fixed_multiplicator=1):
        if self.amount_type == 'partner_tax':
            date = self._context.get('invoice_date', fields.Date.context_today(self))

            # Evitar cálculos redundantes
            date = date or fields.Date.context_today(self)
            partner = partner and partner.sudo()
            # Cálculo del impuesto
            return base_amount * self.sudo().get_partner_alicuota_percepcion(partner, date)
        else:
            # Llamada al método padre
            return super(AccountTax, self)._compute_amount(base_amount, price_unit, quantity=quantity, product=product,
                partner=partner, fixed_multiplicator=fixed_multiplicator)

    from dateutil.relativedelta import relativedelta

    def get_partner_alicuot(self, partner, date):
        self.ensure_one()
        commercial_partner = partner.commercial_partner_id
        company = self.company_id
        alicuot = self.env['res.partner.arba_alicuot'].browse()
        # Buscar alícuota en base a la responsabilidad fiscal del partner
        if commercial_partner.l10n_ar_afip_responsibility_type_id.code in ['1', '1FM', '2', '3', '4', '6', '11', '13']:
            invoice_tags = self.invoice_repartition_line_ids.mapped('tag_ids')
            padron_file = self.env['res.company.jurisdiction.padron'].search([
                ('jurisdiction_id', 'in', invoice_tags.ids),
                ('company_id', '=', company.id),
                '|',
                ('l10n_ar_padron_from_date', '=', False),
                ('l10n_ar_padron_from_date', '<=', date),
                '|',
                ('l10n_ar_padron_to_date', '=', False),
                ('l10n_ar_padron_to_date', '>=', date),
            ], limit=1)
            from_date = date + relativedelta(day=1)
            to_date = date + relativedelta(day=1, days=-1, months=+1)
            agip_tag = self.env.ref('l10n_ar_ux.tag_tax_jurisdiccion_901')
            arba_tag = self.env.ref('l10n_ar_ux.tag_tax_jurisdiccion_902')
            cdba_tag = self.env.ref('l10n_ar_ux.tag_tax_jurisdiccion_904')
            if padron_file:
                nro, alicuot_ret, alicuot_per = padron_file._get_aliquit(commercial_partner)
                if nro:
                    alicuot = partner.arba_alicuot_ids.sudo().create({
                        'numero_comprobante': nro,
                        'alicuota_retencion': float(alicuot_ret),
                        'alicuota_percepcion': float(alicuot_per),
                        'partner_id': commercial_partner.id,
                        'company_id': company.id,
                        'tag_id': padron_file.jurisdiction_id.id,
                        'from_date': from_date,
                        'to_date': to_date,
                    })
            elif arba_tag and arba_tag.id in invoice_tags.ids:
                arba_data = company.get_arba_data(commercial_partner, from_date, to_date)
                if not arba_data.get('numero_comprobante'):
                    arba_data.update({
                        'numero_comprobante': 'Alícuota no inscripto',
                        'alicuota_retencion': company.arba_alicuota_no_sincripto_retencion,
                        'alicuota_percepcion': company.arba_alicuota_no_sincripto_percepcion,
                    })
                arba_data.update({
                    'partner_id': commercial_partner.id,
                    'company_id': company.id,
                    'tag_id': arba_tag.id,
                    'from_date': from_date,
                    'to_date': to_date,
                })
                alicuot = partner.arba_alicuot_ids.sudo().create(arba_data)
            elif agip_tag and agip_tag.id in invoice_tags.ids:
                agip_data = company.get_agip_data(commercial_partner, date)
                if not agip_data.get('numero_comprobante'):
                    agip_data.update({
                        'numero_comprobante': 'Alícuota no inscripto',
                        'alicuota_retencion': company.agip_alicuota_no_sincripto_retencion,
                        'alicuota_percepcion': company.agip_alicuota_no_sincripto_percepcion,
                    })
                agip_data.update({
                    'from_date': from_date,
                    'to_date': to_date,
                    'partner_id': commercial_partner.id,
                    'company_id': company.id,
                    'tag_id': agip_tag.id,
                })
                alicuot = partner.arba_alicuot_ids.sudo().create(agip_data)
            elif cdba_tag and cdba_tag.id in invoice_tags.ids:
                cordoba_data = company.get_cordoba_data(commercial_partner, date)
                cordoba_data.update({
                    'from_date': from_date,
                    'to_date': to_date,
                    'partner_id': commercial_partner.id,
                    'company_id': company.id,
                    'tag_id': cdba_tag.id,
                })
                alicuot = partner.arba_alicuot_ids.sudo().create(cordoba_data)
        return alicuot

