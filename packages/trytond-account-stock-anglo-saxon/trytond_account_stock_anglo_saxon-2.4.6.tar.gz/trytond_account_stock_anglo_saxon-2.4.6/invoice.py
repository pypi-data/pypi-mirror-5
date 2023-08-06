#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from decimal import Decimal
import operator
from trytond.model import ModelView, ModelSQL
from trytond.pool import Pool
from trytond.transaction import Transaction


class InvoiceLine(ModelSQL, ModelView):
    _name = 'account.invoice.line'

    def _get_anglo_saxon_move_lines(self, line, amount, type_):
        '''
        Return account move for anglo-saxon stock accounting
        '''
        assert type_.startswith('in_') or type_.startswith('out_'), \
            'wrong type'

        result = []
        move_line = {}
        move_line['name'] = line.description
        move_line['amount_second_currency'] = Decimal('0.0')
        move_line['second_currency'] = None

        if type_.startswith('in_'):
            move_line['debit'] = amount
            move_line['credit'] = Decimal('0.0')
            account_type = type_[3:]
        else:
            move_line['debit'] = Decimal('0.0')
            move_line['credit'] = amount
            account_type = type_[4:]
        move_line['account'] = getattr(line.product,
                'account_stock_%s_used' % account_type).id

        result.append(move_line)
        move_line = move_line.copy()
        move_line['debit'], move_line['credit'] = \
                move_line['credit'], move_line['debit']
        if type_.endswith('supplier'):
            move_line['account'] = line.account.id
        else:
            move_line['account'] = line.product.account_cogs_used.id
        result.append(move_line)
        return result

    def get_move_line(self, line):
        pool = Pool()
        move_obj = pool.get('stock.move')
        currency_obj = pool.get('currency.currency')

        with Transaction().set_user(0, set_context=True):
            line = self.browse(line.id)
        result = super(InvoiceLine, self).get_move_line(line)

        if line.type != 'line':
            return result
        if not line.product:
            return result
        if line.product.type != 'goods':
            return result

        moves = []
        # other types will get current cost price
        if line.invoice.type == 'in_invoice':
            moves = [move for purchase_line in line.purchase_lines
                    for move in purchase_line.moves
                    if move.state == 'done']
        elif line.invoice.type == 'out_invoice':
            with Transaction().set_user(0, set_context=True):
                sale_lines = self.browse(line.id).sale_lines
            moves = [move for sale_line in sale_lines
                    for move in sale_line.moves
                    if move.state == 'done']
        if line.invoice.type == 'in_invoice':
            type_ = 'in_supplier'
        elif line.invoice.type == 'out_invoice':
            type_ = 'out_customer'
        elif line.invoice.type == 'in_credit_note':
            type_ = 'out_supplier'
        elif line.invoice.type == 'out_credit_note':
            type_ = 'in_customer'
        if line.quantity < 0:
            direction, target = type_.split('_')
            if direction == 'in':
                direction = 'out'
            else:
                direction = 'in'
            type_ = '%s_%s' % (direction, target)

        moves.sort(key=operator.attrgetter('effective_date'))
        cost = move_obj.update_anglo_saxon_quantity_product_cost(
                line.product, moves, abs(line.quantity), line.unit, type_)
        cost = currency_obj.round(line.invoice.currency, cost)

        anglo_saxon_move_lines = self._get_anglo_saxon_move_lines(line, cost,
                type_)
        result.extend(anglo_saxon_move_lines)
        return result

InvoiceLine()
