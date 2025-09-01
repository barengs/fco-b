from rest_framework import serializers
from .models import FishSpecies, Fish

class FishSpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FishSpecies
        fields = ['id', 'name', 'scientific_name', 'description', 'created_at', 'updated_at']
        labels = {
            'name': 'nama_ikan',
            'scientific_name': 'nama_ilmiah',
            'description': 'deskripsi',
            'created_at': 'tanggal_dibuat',
            'updated_at': 'tanggal_diperbarui'
        }

class FishSerializer(serializers.ModelSerializer):
    species_name = serializers.CharField(source='species.name', read_only=True)

    class Meta:
        model = Fish
        fields = ['id', 'species', 'species_name', 'name', 'weight', 'notes', 'created_at', 'updated_at']
        labels = {
            'species': 'jenis_ikan',
            'species_name': 'nama_jenis_ikan',
            'name': 'nama_ikan',
            'weight': 'berat_kg',
            'notes': 'catatan',
            'created_at': 'tanggal_dibuat',
            'updated_at': 'tanggal_diperbarui'
        }