# -*- coding: utf-8 -*-
{
    'name': 'SIRITA - Presensi & Tukin Terintegrasi (ZKTeco ADMS & PMA 11/2019)',
    'version': '20.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Menerima Push Log ZKTeco ADMS, Mapping Karyawan & Perhitungan Tukin Kemenag',
    'description': """
        Modul Lengkap Presensi & Tukin IAIN Parepare:
        1. ADMS ZKTeco Integrator:
           - HTTP Controller Endpoint (/iclock/cdata)
           - Registrasi Serial Number Mesin ZKTeco
           - Antrean Sinkronisasi User & Sidik Jari
           - Auto-create hr.attendance
        2. Tunjangan Kinerja Kemenag (PMA No. 11 Tahun 2019):
           - Master Kelas Jabatan (Grade 1 - 17) & Pagu Tukin
           - Pengaturan Khusus Dosen (Non-Serdos 50%, Serdos Selisih TPD)
           - Analisis Keterlambatan TL1-TL4 & Pulang Cepat PC1-PC4 otomatis dari hr.attendance
           - Cetak Rekapitulasi Matriks Bulanan (Style Excel Landscape PDF)
    """,
    'author': 'SIRITA | sufyaldys@gmail.com',
    'depends': ['base', 'hr', 'hr_attendance', 'resource'],
    'data': [
        'security/ir.access.csv',
        'data/tukin_grade_data.xml',
        'data/ir_cron_data.xml',
        'report/tukin_report_templates_v2.xml',
        'report/tukin_report_templates.xml',
        'views/zk_user_queue_view.xml',
        'views/zk_command_views.xml',
        'views/zk_device_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_grade_views.xml',
        'views/tukin_calculation_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'GPL-3',
}
