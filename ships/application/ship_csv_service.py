"""
Ship CSV Service (Application Layer)
Handles business workflows for vessel CSV template generation and bulk CSV data ingestion.
"""

import csv
from io import StringIO
from django.http import HttpResponse
from django.apps import apps

class ShipCsvService:
    """Use case service for CSV imports and template generation of fishing vessels."""

    KNOWN_HEADERS = [
        'name', 'nama_kapal', 'registration_number', 'no_buku_kapal',
        'length', 'panjang', 'width', 'lebar', 'gross_tonnage', 'tonase_kotor',
        'year_built', 'tahun_dibuat', 'home_port', 'pelabuhan_asal', 'active', 'aktif'
    ]

    @staticmethod
    def generate_template() -> HttpResponse:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ship_import_template.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'name',
            'registration_number',
            'length',
            'width',
            'gross_tonnage',
            'year_built',
            'home_port',
            'active'
        ])
        writer.writerow([
            'Nama Kapal',
            'REG001',
            '20.5',
            '5.2',
            '100.5',
            '2020',
            'Pelabuhan Asal',
            'true'
        ])
        return response

    @staticmethod
    def parse_and_import(csv_file_upload=None, csv_data=None):
        """
        Parses CSV data (file or string) and creates/updates vessels.
        """
        Ship = apps.get_model('ships', 'Ship')
        Owner = apps.get_model('owners', 'Owner')
        Captain = apps.get_model('owners', 'Captain')

        if csv_file_upload:
            file_content = csv_file_upload.read().decode('utf-8')
            csv_file = StringIO(file_content)
        elif csv_data:
            csv_file = StringIO(csv_data)
        else:
            raise ValueError('File atau data CSV tidak tersedia')

        reader = csv.DictReader(csv_file)
        has_headers = any(h in reader.fieldnames for h in ShipCsvService.KNOWN_HEADERS) if reader.fieldnames else False

        created_count = 0
        updated_count = 0
        error_count = 0
        error_details = []

        if not has_headers:
            csv_file.seek(0)
            simple_reader = csv.reader(csv_file)
            for row_num, row in enumerate(simple_reader, 1):
                if not row or not any(row):
                    continue
                try:
                    name = row[0].strip() if len(row) > 0 else f'Kapal-{row_num}'
                    reg_num = row[1].strip() if len(row) > 1 else f'REG-POS-{row_num:03d}'
                    length = float(row[2]) if len(row) > 2 and row[2] else 10.0
                    width = float(row[3]) if len(row) > 3 and row[3] else 3.0
                    gt = float(row[4]) if len(row) > 4 and row[4] else 30.0
                    year_built = int(row[5]) if len(row) > 5 and row[5] else 2020
                    home_port = row[6].strip() if len(row) > 6 else 'Pelabuhan Default'
                    active = row[7].strip().lower() in ('true', '1', 't', 'y', 'yes') if len(row) > 7 else True

                    _, created = Ship.objects.update_or_create(
                        registration_number=reg_num,
                        defaults={
                            'name': name,
                            'length': length,
                            'width': width,
                            'gross_tonnage': gt,
                            'year_built': year_built,
                            'home_port': home_port,
                            'active': active,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    error_count += 1
                    error_details.append(f"Baris {row_num}: {str(e)}")
        else:
            for row_num, row in enumerate(reader, 1):
                try:
                    reg_num = (row.get('registration_number') or row.get('no_buku_kapal') or '').strip()
                    if not reg_num:
                        error_count += 1
                        error_details.append(f"Baris {row_num}: Nomor registrasi kosong")
                        continue

                    name = (row.get('name') or row.get('nama_kapal') or f'Kapal-{row_num}').strip()
                    length = float(row.get('length') or row.get('panjang') or 10.0)
                    width = float(row.get('width') or row.get('lebar') or 3.0)
                    gt = float(row.get('gross_tonnage') or row.get('tonase_kotor') or 30.0)
                    year_built = int(row.get('year_built') or row.get('tahun_dibuat') or 2020)
                    home_port = (row.get('home_port') or row.get('pelabuhan_asal') or 'Pelabuhan Default').strip()
                    active_val = row.get('active') or row.get('aktif') or 'true'
                    active = str(active_val).strip().lower() in ('true', '1', 't', 'y', 'yes')

                    _, created = Ship.objects.update_or_create(
                        registration_number=reg_num,
                        defaults={
                            'name': name,
                            'length': length,
                            'width': width,
                            'gross_tonnage': gt,
                            'year_built': year_built,
                            'home_port': home_port,
                            'active': active,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    error_count += 1
                    error_details.append(f"Baris {row_num}: {str(e)}")

        return {
            'created': created_count,
            'updated': updated_count,
            'errors': error_count,
            'error_details': error_details if error_details else None
        }
