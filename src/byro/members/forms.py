from django import forms
from django.db.models.fields.related import OneToOneRel
from django.utils.timezone import now

from byro.common.models import Configuration
from byro.members.models import Member, Membership, get_next_member_number

MAPPING = {
    'member': Member,
    'membership': Membership,
}


class CreateMemberForm(forms.Form):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        config = Configuration.get_solo().registration_form or []
        config = sorted(
            [field for field in config if field['position'] is not None],
            key=lambda field: field['position']
        )
        profiles = {
            profile.related_model.__name__: profile.related_model
            for profile in Member._meta.related_objects
            if isinstance(profile, OneToOneRel) and profile.name.startswith('profile_')
        }
        for field in config:
            model_name = field['name'].split('__')[0]
            if model_name in MAPPING:
                model = MAPPING[model_name]
            else:
                model = profiles[field['name'].split('__')[0]]
            temp_form = forms.modelform_factory(model, fields=[field['name'].split('__')[-1]])()
            form_field = [field for field in temp_form.fields.values()][0]
            form_field.model = model
            self.fields[field['name']] = form_field
        if 'member__number' in self.fields:
            self.fields['member__number'].initial = get_next_member_number()
        if 'membership__start' in self.fields:
            self.fields['membership__start'].initial = now().date()

    def save(self):
        profiles = {
            profile.related_model.__name__: profile.related_model()
            for profile in Member._meta.related_objects
            if isinstance(profile, OneToOneRel) and profile.name.startswith('profile_')
        }
        member = Member()
        membership = Membership()

        for key, value in self.cleaned_data.items():
            model_name = key.split('__')[0]
            if model_name == 'member':
                obj = member
            elif model_name == 'membership':
                obj = membership
            else:
                obj = profiles[key.split('__')[0]]
            setattr(obj, key.split('__', maxsplit=1)[-1], value)
        member.save()
        member.refresh_from_db()
        membership.member = self.instance = member
        membership.save()
        for profile in profiles.values():
            profile.member = member
            profile.save()
