# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ZKCommand(models.Model):
    _name = 'zkteco.command'
    _description = 'ZKTeco Device Commands'
    _order = 'id asc'

    device_id = fields.Many2one('zkteco.device', string='Device', required=True, ondelete='cascade')
    command_text = fields.Char(string='Command', required=True)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('completed', 'Completed'),
        ('error', 'Error')
    ], string='Status', default='pending')
    
    response = fields.Text(string='Response From Device')
    timestamp = fields.Datetime(string='Created At', default=fields.Datetime.now)

    @api.model
    def cron_clean_old_commands(self, days=7):
        """Cron: Membersihkan riwayat antrean command ADMS yang sudah selesai/sukses lebih dari X hari"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        old_commands = self.search([
            ('status', 'in', ['completed', 'error']),
            ('timestamp', '<', cutoff)
        ])
        count = len(old_commands)
        if old_commands:
            old_commands.unlink()
        return count
