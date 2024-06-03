import logging

from odoo.exceptions import UserError

from odoo import models, _

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    def get_agip_data(self, partner, date):
        raise UserError(_(
            'Falta cargar la alícuota de percepción/retención de IIBB de la jurisdicción del partner.'
            'Puede cargarla manualmente en la pestaña "datos fiscales" del partner agregando una línea '
            'en "Alícuotas PERC-RET o cargar el padrón desde Contabilidad/Configuración/Padrón de Alícuotas'))
