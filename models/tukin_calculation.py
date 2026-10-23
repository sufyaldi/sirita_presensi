# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
import calendar

class TukinCalculation(models.Model):
    _name = 'tukin.calculation'
    _description = 'Rekapitulasi Tukin Bulanan'
    _order = 'year desc, month desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    month = fields.Selection([
        ('1', 'Januari'), ('2', 'Februari'), ('3', 'Maret'), ('4', 'April'),
        ('5', 'Mei'), ('6', 'Juni'), ('7', 'Juli'), ('8', 'Agustus'),
        ('9', 'September'), ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember')
    ], string='Bulan', default=lambda self: str(date.today().month), required=True)
    
    year = fields.Selection([(str(y), str(y)) for y in range(2023, 2031)], 
                            string='Tahun', default=lambda self: str(date.today().year), required=True)
    
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    company_id = fields.Many2one('res.company', string='Satker', default=lambda self: self.env.company)
    
    # PEJABAT PENANDATANGAN (DINAMIS)
    rektor_id = fields.Many2one('hr.employee', string='Rektor (Tanda Tangan)')
    kabiro_id = fields.Many2one('hr.employee', string='Kepala Biro AUAK (Tanda Tangan)')

    line_ids = fields.One2many('tukin.calculation.line', 'calculation_id', string='Detail Karyawan')
    
    @api.depends('month', 'year')
    def _compute_name(self):
        for rec in self:
            rec.name = f"TUKIN/{rec.month}/{rec.year}"

    def action_calculate(self):
        """Proses perhitungan untuk semua karyawan aktif"""
        self.ensure_one()
        Employee = self.env['hr.employee'].search([('active', '=', True)])
        Line = self.env['tukin.calculation.line']
        
        # Range Tanggal untuk bulan terpilih
        first_day = date(int(self.year), int(self.month), 1)
        last_day = date(int(self.year), int(self.month), calendar.monthrange(int(self.year), int(self.month))[1])
        
        # Hapus data lama yang masih draft
        self.line_ids.unlink()
        
        for emp in Employee:
            if not emp.tukin_grade_id: continue
            
            pagu = emp.tukin_grade_id.pagu_tukin
            base_amount = pagu
            
            # ATURAN DOSEN PMA 11/2019
            if emp.is_lecturer:
                if not emp.has_serdos:
                    base_amount = 0.5 * pagu
                else:
                    base_amount = max(0, pagu - emp.tpd_amount)
            
            # [LOGIKA BARU] Analisis Absensi
            attendance_data = self._analyze_employee_attendance(emp, first_day, last_day)
            
            Line.create({
                'calculation_id': self.id,
                'employee_id': emp.id,
                'grade_name': emp.tukin_grade_id.name,
                'pagu_grade': pagu,
                'base_tukin': base_amount,
                
                # Detail Potongan
                'tl1_count': attendance_data['tl1'],
                'tl2_count': attendance_data['tl2'],
                'tl3_count': attendance_data['tl3'],
                'tl4_count': attendance_data['tl4'],
                'pc1_count': attendance_data['pc1'],
                'pc2_count': attendance_data['pc2'],
                'pc3_count': attendance_data['pc3'],
                'pc4_count': attendance_data['pc4'],
                'alpha_count': attendance_data['alpha'],
                
                'presence_deduction_pct': attendance_data['total_pct'],
                'final_tukin': base_amount - (base_amount * (attendance_data['total_pct'] / 100.0)),
            })

    def _analyze_employee_attendance(self, employee, start_date, end_date):
        """Menganalisis keterlambatan dan ketidakhadiran"""
        res = {
            'tl1': 0, 'tl2': 0, 'tl3': 0, 'tl4': 0,
            'pc1': 0, 'pc2': 0, 'pc3': 0, 'pc4': 0,
            'alpha': 0, 'total_pct': 0.0
        }
        
        attendances = self.env['hr.attendance'].search([
            ('employee_id', '=', employee.id),
            ('check_in', '>=', fields.Datetime.to_datetime(start_date)),
            ('check_in', '<=', fields.Datetime.to_datetime(end_date))
        ])

        calendar_obj = employee.resource_calendar_id or self.env.company.resource_calendar_id
        if not calendar_obj:
            return res
            
        for att in attendances:
            if not att.check_in: continue
            dayofweek = att.check_in.weekday()
            work_hours = calendar_obj.attendance_ids.filtered(lambda x: x.dayofweek == str(dayofweek) and x.day_period == 'morning')
            
            if work_hours:
                std_in = work_hours[0].hour_from
                check_in_local = fields.Datetime.context_timestamp(self, att.check_in)
                check_in_float = check_in_local.hour + check_in_local.minute / 60.0
                diff_minutes = (check_in_float - std_in) * 60.0
                if diff_minutes > 1:
                    if diff_minutes <= 30: res['tl1'] += 1; res['total_pct'] += 0.5
                    elif diff_minutes <= 60: res['tl2'] += 1; res['total_pct'] += 1.0
                    elif diff_minutes <= 90: res['tl3'] += 1; res['total_pct'] += 1.25
                    else: res['tl4'] += 1; res['total_pct'] += 1.5

            if att.check_out and work_hours:
                work_hours_pm = calendar_obj.attendance_ids.filtered(lambda x: x.dayofweek == str(dayofweek) and x.day_period == 'afternoon')
                std_out = work_hours_pm[-1].hour_to if work_hours_pm else work_hours[0].hour_to
                check_out_local = fields.Datetime.context_timestamp(self, att.check_out)
                check_out_float = check_out_local.hour + check_out_local.minute / 60.0
                diff_out = (std_out - check_out_float) * 60.0
                if diff_out > 1:
                    if diff_out <= 30: res['pc1'] += 1; res['total_pct'] += 0.5
                    elif diff_out <= 60: res['pc2'] += 1; res['total_pct'] += 1.0
                    elif diff_out <= 90: res['pc3'] += 1; res['total_pct'] += 1.25
                    else: res['pc4'] += 1; res['total_pct'] += 1.5
        return res

    def get_report_data(self):
        """Menyiapkan data matriks untuk PDF Report"""
        self.ensure_one()
        first_day = date(int(self.year), int(self.month), 1)
        last_day_val = calendar.monthrange(int(self.year), int(self.month))[1]
        
        days = list(range(1, last_day_val + 1))
        
        recap_data = []
        for line in self.line_ids:
            attendance_map = {}
            atts = self.env['hr.attendance'].search([
                ('employee_id', '=', line.employee_id.id),
                ('check_in', '>=', fields.Datetime.to_datetime(first_day)),
                ('check_in', '<=', fields.Datetime.to_datetime(date(int(self.year), int(self.month), last_day_val)))
            ])
            
            for att in atts:
                local_in = fields.Datetime.context_timestamp(self, att.check_in)
                day = local_in.day
                val_in = local_in.strftime('%H.%M')
                val_out = ""
                if att.check_out:
                    local_out = fields.Datetime.context_timestamp(self, att.check_out)
                    val_out = local_out.strftime('%H.%M')
                attendance_map[day] = {'in': val_in, 'out': val_out}
            
            recap_data.append({
                'name': line.employee_id.name,
                'nip': line.employee_id.barcode or '-',
                'attendances': attendance_map,
                'summary': {
                    'tl': line.tl1_count + line.tl2_count + line.tl3_count + line.tl4_count,
                    'pc': line.pc1_count + line.pc2_count,
                    'alpha': line.alpha_count,
                    'work_days': 20,
                }
            })
            
        return {
            'days': days,
            'employees': recap_data,
        }

class TukinCalculationLine(models.Model):
    _name = 'tukin.calculation.line'
    _description = 'Detail Tukin per Karyawan'

    calculation_id = fields.Many2one('tukin.calculation', ondelete='cascade')
    company_id = fields.Many2one('res.company', related='calculation_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)

    employee_id = fields.Many2one('hr.employee', string='Karyawan')
    grade_name = fields.Char(string='Grade')
    pagu_grade = fields.Monetary(string='Pagu Full (100%)', currency_field='currency_id')
    base_tukin = fields.Monetary(string='Basis Tukin', currency_field='currency_id')
    
    tl1_count = fields.Integer('TL1')
    tl2_count = fields.Integer('TL2')
    tl3_count = fields.Integer('TL3')
    tl4_count = fields.Integer('TL4')
    pc1_count = fields.Integer('PC1')
    pc2_count = fields.Integer('PC2')
    pc3_count = fields.Integer('PC3')
    pc4_count = fields.Integer('PC4')
    alpha_count = fields.Integer('Alpha')

    presence_deduction_pct = fields.Float(string='Total Pot. (%)')
    final_tukin = fields.Monetary(string='Tunjangan Bersih', currency_field='currency_id')
