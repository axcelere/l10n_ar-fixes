
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from dateutil.relativedelta import relativedelta
import logging
import re
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _l10n_ar_get_document_number_parts(self, document_number, document_type_code):
        document_number_splitted = document_number.split('-')
        if document_type_code in ['66', '67'] and len(document_number_splitted) == 2:
            return super(AccountMove, self)._l10n_ar_get_document_number_parts(document_number, document_type_code)
        elif len(document_number_splitted) > 2:
            document_number_splitted = document_number_splitted[-2:]
            numbers = re.findall(r'\d+', document_number_splitted[0])
            pos = int(''.join(numbers)) if numbers else None
            numbers = re.findall(r'\d+', document_number_splitted[1])
            invoice_number = int(''.join(numbers)) if numbers else None
        else:
            pos = 0
            invoice_number = document_number_splitted[0]
        return {'invoice_number': int(invoice_number), 'point_of_sale': int(pos)}
