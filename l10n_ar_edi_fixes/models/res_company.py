import base64

from odoo.exceptions import UserError

from odoo import models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    def _get_key_and_certificate(self):
        """ Return the pkey and certificate string representations in order to be used. Also raise exception if any key or certificate is not defined """
        self.ensure_one()
        pkey = base64.decodebytes(self.with_context(bin_size=False).l10n_ar_afip_ws_key) if self.l10n_ar_afip_ws_key else ''
        try:
            cert = base64.decodebytes(self.l10n_ar_afip_ws_crt) if self.l10n_ar_afip_ws_crt else ''
        except Exception:
            cert = base64.decodebytes(self.with_context(bin_size=False).l10n_ar_afip_ws_crt) if self.l10n_ar_afip_ws_crt else ''
            pass
        res = (pkey, cert)
        if not all(res):
            error = '\n * ' + _(' Missing private key.') if not pkey else ''
            error += '\n * ' + _(' Missing certificate.') if not cert else ''
            raise UserError(_('Missing configuration to connect to AFIP:') + error)
        self._l10n_ar_is_afip_crt_expire()
        return res
