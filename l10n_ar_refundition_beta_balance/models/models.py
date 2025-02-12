
from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from dateutil.relativedelta import relativedelta
from contextlib import ExitStack, contextmanager
import logging
import re
_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    refundition_forced_account_id = fields.Many2one(
        'account.account',
        string='Cuenta para balance forzado (Asiento de refundición)')

class AccountMove(models.Model):
    _inherit = "account.move"

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        for move_id, sum_debit, sum_credit in unbalanced_moves:
            move = self.browse(move_id)
            if move.journal_id.refundition_forced_account_id:
                diff = sum_debit - sum_credit
                line = {
                    'name': _('Refundición'),
                    'account_id': move.journal_id.refundition_forced_account_id.id,
                    'debit': 0,
                    'credit': 0,
                }
                if sum_credit > sum_debit:
                    line['debit'] = abs(sum_credit - sum_debit)
                    line['credit'] = 0
                else:
                    line['debit'] = 0
                    line['credit'] = abs(sum_debit - sum_credit)
                move.write({'line_ids': [(0, 0, line)]})
                # move._post(soft=True)

        unbalanced_moves = self._get_unbalanced_moves(container)
        if not unbalanced_moves:
            return
        super(AccountMove, self)._check_balanced(container)