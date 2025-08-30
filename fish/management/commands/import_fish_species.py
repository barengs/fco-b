import csv
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from django.apps import apps

class Command(BaseCommand):
    help = 'Import fish species data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing fish species before importing',
        )

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        clear_existing = options['clear']
        
        # Get the FishSpecies model dynamically to avoid type checking issues
        FishSpecies = apps.get_model('fish', 'FishSpecies')
        
        # Clear existing data if requested
        if clear_existing:
            FishSpecies._default_manager.all().delete()  # type: ignore
            self.stdout.write(
                'Successfully cleared all existing fish species'
            )
        
        # Read and process the CSV file
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                created_count = 0
                updated_count = 0
                error_count = 0
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 since header is row 1
                    try:
                        # Extract data from CSV row
                        name = row.get('name', '').strip()
                        scientific_name = row.get('scientific_name', '').strip() or None
                        description = row.get('description', '').strip() or None
                        
                        # Validate required fields
                        if not name:
                            self.stdout.write(
                                f'Row {row_num}: Missing name, skipping'
                            )
                            error_count += 1
                            continue
                        
                        # Create or update the fish species
                        fish_species, created = FishSpecies._default_manager.get_or_create(  # type: ignore
                            name=name,
                            defaults={
                                'scientific_name': scientific_name,
                                'description': description,
                            }
                        )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(
                                f'Created: {name}'
                            )
                        else:
                            # Update existing record if there's new data
                            updated = False
                            if scientific_name and fish_species.scientific_name != scientific_name:
                                fish_species.scientific_name = scientific_name
                                updated = True
                            if description and fish_species.description != description:
                                fish_species.description = description
                                updated = True
                            
                            if updated:
                                fish_species.save()
                                updated_count += 1
                                self.stdout.write(
                                    f'Updated: {name}'
                                )
                            else:
                                self.stdout.write(
                                    f'No changes: {name}'
                                )
                    
                    except ValidationError as e:
                        self.stdout.write(
                            f'Row {row_num}: Validation error - {e}'
                        )
                        error_count += 1
                    except Exception as e:
                        self.stdout.write(
                            f'Row {row_num}: Unexpected error - {e}'
                        )
                        error_count += 1
                
                # Print summary
                self.stdout.write(
                    f'Import completed. Created: {created_count}, Updated: {updated_count}, Errors: {error_count}'
                )
        
        except FileNotFoundError:
            self.stdout.write(
                f'File not found: {csv_file_path}'
            )
        except Exception as e:
            self.stdout.write(
                f'Error reading CSV file: {e}'
            )