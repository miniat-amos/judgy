from rest_framework import serializers
from django.utils import timezone
from .models import Competition, Problem

class CompSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            'name', 'description', 'start', 'end',
            'enroll_start', 'enroll_end', 'team_size_limit', 'color'
        ]

    def validate(self, data):
        start = data.get('start', getattr(self.instance, 'start', None))
        end = data.get('end', getattr(self.instance, 'end', None))
        enroll_start = data.get('enroll_start', getattr(self.instance, 'enroll_start', None))
        enroll_end = data.get('enroll_end', getattr(self.instance, 'enroll_end', None))
        
        now = timezone.now()

        # Validate that start is before end
        if start and end and start >= end:
            raise serializers.ValidationError({'end': 'End date must be after start date.'})

        # Validate that enroll_start is before enroll_end
        if enroll_start and enroll_end and enroll_start >= enroll_end:
            raise serializers.ValidationError({'enroll_end': 'Enrollment end date must be after enrollment start date.'})

        # Validate that dates are not in the past
        if self.instance:
            if start < now and self.instance.start != start:
                raise serializers.ValidationError({'start': 'You cannot change the start date to a past date.'})
                
            if end < now and self.instance.end != end:
                raise serializers.ValidationError({'end': 'End date cannot be in the past.'})
            
            if enroll_start < now and self.instance.enroll_start != enroll_start:
                raise serializers.ValidationError({'enroll_start': 'You cannot change the enroll start date to a past date.'})
            
            if enroll_end < now and self.instance.enroll_end != enroll_end:
                raise serializers.ValidationError({'enroll_end': 'Enrollment end date cannot be in the past.'})

        return data

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
