# -*- coding: utf-8 -*-
from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    zk_pin = fields.Char(string='ID/PIN Mesin Absensi', help="Nomor PIN atau badge yang didaftarkan di mesin ZKTeco")

    # PMA No. 11 Tahun 2019 - Tukin Kemenag
    tukin_grade_id = fields.Many2one('tukin.grade', string='Grade Tukin')
    is_lecturer = fields.Boolean(string='Dosen?', default=False)
    has_serdos = fields.Boolean(string='Sudah Sertifikasi (Serdos)?', default=False)
    tpd_amount = fields.Monetary(string='Tunjangan Profesi (Selisih)', 
                                help="Input nilai TPD per bulan jika Dosen Serdos",
                                currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  related='company_id.currency_id')

    # Gelar Akademik
    gelar_depan = fields.Char(string='Gelar Depan', help='Contoh: Prof. Dr.')
    gelar_belakang = fields.Char(string='Gelar Belakang', help='Contoh: M.Ag, M.Pd')
