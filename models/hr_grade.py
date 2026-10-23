# -*- coding: utf-8 -*-
from odoo import models, fields

class TukinGrade(models.Model):
    _name = 'tukin.grade'
    _description = 'Kelas Jabatan & Pagu Tukin'
    _order = 'grade desc'

    name = fields.Char(string='Nama Jabatan / Kelas', required=True)
    grade = fields.Integer(string='Kelas Jabatan', required=True, help="1 s/d 17")
    pagu_tukin = fields.Monetary(string='Pagu Tukin (100%)', required=True, currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', string='Currency', 
                                  default=lambda self: self.env.company.currency_id)

    _sql_unique_grade = models.Constraint(
        'UNIQUE(grade)',
        'Kelas Jabatan ini sudah ada!'
    )
