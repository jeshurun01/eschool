from django import forms
from django.core.exceptions import ValidationError
from .models import ClassRoom, Level, AcademicYear, Subject, TeacherAssignment, Enrollment, Grade, Attendance
from accounts.models import Teacher, Student


class ClassRoomForm(forms.ModelForm):
    """Formulaire pour créer/modifier une classe"""
    
    class Meta:
        model = ClassRoom
        fields = ['name', 'level', 'academic_year', 'head_teacher', 'capacity', 'room_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: 6ème A'
            }),
            'level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'academic_year': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'head_teacher': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'min': '1',
                'placeholder': '30'
            }),
            'room_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: A101'
            }),
        }
        labels = {
            'name': 'Nom de la classe',
            'level': 'Niveau',
            'academic_year': 'Année académique',
            'head_teacher': 'Professeur principal',
            'capacity': 'Capacité maximale',
            'room_number': 'Numéro de salle',
        }
        help_texts = {
            'capacity': 'Nombre maximum d\'élèves dans la classe',
            'room_number': 'Numéro ou code de la salle de classe',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre head_teacher optionnel avec une option vide
        self.fields['head_teacher'].required = False
        self.fields['head_teacher'].empty_label = "Aucun professeur principal"
        self.fields['room_number'].required = False
        
        # Filtrer les enseignants actifs
        self.fields['head_teacher'].queryset = Teacher.objects.select_related('user').filter(
            user__is_active=True
        )
    
    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity and capacity < 1:
            raise ValidationError('La capacité doit être au moins de 1 élève.')
        return capacity
    
    def clean(self):
        cleaned_data = super().clean()
        level = cleaned_data.get('level')
        academic_year = cleaned_data.get('academic_year')
        name = cleaned_data.get('name')
        
        # Vérifier l'unicité du nom de classe pour une année et un niveau donnés
        if level and academic_year and name:
            # Exclure l'instance actuelle en cas de modification
            queryset = ClassRoom.objects.filter(
                name=name,
                level=level,
                academic_year=academic_year
            )
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(
                    f'Une classe "{name}" existe déjà pour le niveau {level} '
                    f'dans l\'année {academic_year}.'
                )
        
        return cleaned_data


class TeacherAssignmentForm(forms.ModelForm):
    """Formulaire pour assigner un enseignant à une matière dans une classe"""
    
    class Meta:
        model = TeacherAssignment
        fields = ['classroom', 'teacher', 'subject']
        widgets = {
            'classroom': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'teacher': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les enseignants actifs
        self.fields['teacher'].queryset = Teacher.objects.select_related('user').filter(
            user__is_active=True
        )


class EnrollmentForm(forms.ModelForm):
    """Formulaire pour inscrire un élève dans une classe"""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'classroom', 'academic_year', 'enrollment_date', 'is_active']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'classroom': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'academic_year': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'enrollment_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-blue-600 focus:ring-blue-500'
            }),
        }


class GradeForm(forms.ModelForm):
    """Formulaire pour saisir une note"""
    
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'teacher', 'classroom', 'evaluation_name', 'evaluation_type', 
                  'score', 'max_score', 'coefficient', 'date', 'comments']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'teacher': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'classroom': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'evaluation_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Ex: Contrôle 1'
            }),
            'evaluation_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'score': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.5',
                'min': '0'
            }),
            'max_score': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.5',
                'min': '0'
            }),
            'coefficient': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'step': '0.1',
                'min': '0.1'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'comments': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': '3',
                'placeholder': 'Commentaire optionnel sur la note'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get('score')
        max_score = cleaned_data.get('max_score')
        
        if score is not None and max_score is not None:
            if score > max_score:
                raise ValidationError('La note ne peut pas être supérieure à la note maximale.')
        
        return cleaned_data


class AttendanceForm(forms.ModelForm):
    """Formulaire pour enregistrer les présences"""
    
    class Meta:
        model = Attendance
        fields = ['student', 'classroom', 'subject', 'teacher', 'date', 'status', 'justification']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'classroom': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'subject': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'teacher': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'justification': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'rows': '2',
                'placeholder': 'Justification optionnelle'
            }),
        }
