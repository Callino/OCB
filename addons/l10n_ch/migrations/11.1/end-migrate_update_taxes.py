# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, SUPERUSER_ID
from odoo.addons.account.models.chart_template import update_taxes_from_templates


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # We had corrupted data, handle the correction so the tax update can proceed.
    # See https://github.com/odoo/odoo/commit/7b07df873535446f97abc1de9176b9332de5cb07
    taxes_to_check = ('vat_purchase_81_return', 'vat_77_purchase_return')
    tax_ids = env['ir.model.data'].search([('name', 'in', taxes_to_check)]).mapped('res_id')
    for tax in env['account.tax'].browse(tax_ids):
        for child in tax.children_tax_ids:
            if child.type_tax_use not in ('none', tax.type_tax_use):
                # set the child to it's parent's value
                child.type_tax_use = tax.type_tax_use

    # Update taxes
    new_template_to_tax = update_taxes_from_templates(cr, 'l10n_ch.l10nch_chart_template')
    if new_template_to_tax:
        _, new_tax_ids = zip(*new_template_to_tax)
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['account.tax'].browse(new_tax_ids).active = True
