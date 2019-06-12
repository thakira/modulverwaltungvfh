from django import forms
from .models import Assignment, Module, Prerequisite
import sys


class AssignmentForm(forms.ModelForm):
    SEMESTER = [
        (u'', u'---'),
        ('WS', 'WS'),
        ('SS', 'SS')
    ]

    class Meta:
        model = Assignment
        fields = ('accredited',)

    type_of_semester = forms.CharField(label='Sommer- oder Wintersemester',
                                       widget=forms.Select(choices=SEMESTER,
                                                           attrs={'placeholder': 'Select the category'}))
    year = forms.CharField(max_length=2, label="Jahr des Semesters (zum Beispiel 17 für WS17/18)")
    module = forms.ModelChoiceField(queryset=None, label="Modul", empty_label='---')
    accredited = forms.BooleanField(required=False, label='anerkannt')
    score = forms.FloatField(required=False, label="Note")

    def get_semester(self):
        type_of_semester = self.cleaned_data['type_of_semester']
        year = self.cleaned_data['year']

        if type_of_semester == "WS":
            year = year + "/" + str((int(year, 10) + 1))

        return type_of_semester + year

    def get_data(self, name):
        return self.cleaned_data[name]

    def __init__(self, user, *args, **kwargs):
        super(AssignmentForm, self).__init__(*args, **kwargs)

        self.fields['module'].queryset = Module.objects.none()

        my_assignments = Assignment.objects.filter(student__userid=user)
        my_modules = my_assignments.values('module')
        my_modules_names = list(my_modules.values_list('module_id', flat=True))
        all_modules_except_mine = Module.objects.exclude(MID__in=my_modules_names)

        if 'type_of_semester' in self.data:
            try:
                type_of_semester = self.data.get('type_of_semester')
                self.fields['module'].queryset = all_modules_except_mine.filter(**{type_of_semester: True})
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['module'].queryset = Module.objects.none()

        '''

        '''
