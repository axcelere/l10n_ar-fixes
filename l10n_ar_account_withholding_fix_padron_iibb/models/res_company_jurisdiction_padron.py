from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from io import BytesIO
import zipfile
import tempfile
import os
import re
import logging
import base64
_logger = logging.getLogger(__name__)


class ResCompanyJurisdictionPadron(models.Model):
    _inherit = "res.company.jurisdiction.padron"
    _description = "res.company.jurisdiction.padron"

    @api.constrains('jurisdiction_id')
    def check_jurisdiction_id(self):
        pass
        # arba_tag = self.env.ref('l10n_ar_ux.tag_tax_jurisdiccion_902')
        # for rec in self:
        #     if rec.jurisdiction_id != arba_tag:
        #         raise ValidationError("El padron para (%s) no está implementado." % rec.jurisdiction_id.name)
