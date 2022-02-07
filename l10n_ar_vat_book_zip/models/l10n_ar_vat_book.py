from odoo import models


class L10nARVatBook(models.AbstractModel):
    _name = "l10n_ar.vat.book"
    _inherit = "l10n_ar.vat.book"

    def _get_zip(self, options):
        return self.get_zip(options)
