from django import forms as dj_forms
from minerva.models import UserProfile, Word

class QuestionForm(dj_forms.Form):
    meta = dj_forms.CharField(widget=dj_forms.HiddenInput)
    answer = dj_forms.ChoiceField(choices=((False, 'False'), (True, 'True')),
            widget=dj_forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        question = kwargs.pop("question", None)
        answers = kwargs.pop('answers', None)
        super(QuestionForm, self).__init__(*args, **kwargs)
        # FIXME: This is a little hack-tastic. Maybe we get this from meta and
        # meta will always be present (either initial data or from form).
        if answers:
            self.fields['answer'].choices = answers
            if question:
                self.fields['meta'].initial = \
                        self._pack_meta_data(question, answers)

    def clean_meta(self):
        data = self.cleaned_data["meta"]
        # XXX: Hack (for now). This populates valid choice for "answer" before
        # it gets cleaned. Kind of an abuse of clean_FOO(), so I'll tidy it up
        # later.
        pieces = self._unpack_question_meta_data(data)
        self.fields["answer"].choices = [(bit, bit) for bit in pieces[1]]
        return pieces

    def _pack_meta_data(self, correct, possible_answers):
        """
        Flatten the question meta data so that we know which choices were
        presented to the user without having to store anything on the server.
        """
        data = [str(correct[0])]
        data.extend([str(item[0]) for item in possible_answers])
        return "|".join(data)
    
    def _unpack_question_meta_data(self, packed_data):
        data = [int(i) for i in packed_data.split("|")]
        return data[0], data[1:]

class UserProfileForm(dj_forms.ModelForm):
    class Meta:
        model=UserProfile
        exclude = ('student', )

    def clean_language(self):
        data = self.cleaned_data['language']
        if data not in Word.objects.all().values_list('language', flat=True).distinct():
            raise dj_forms.ValidationError("language %s is not supported" % data)
        return data
