Django payment gateway for smscoin service
==========================================

Payment gateway site: http://smscoin.com

Usage
=====

* You have to use south migrations to update your database::

    python manage.py migrate

* Django form field: ***SMSKeyField**. Example in **forms.py**::

    from smscoin.fields import SMSKeyField
    class SMSForm(forms.ModelForm):

        sms_pair = SMSKeyField(label=_("Access code"), required=True)

* **settings.py**::

    SMSCOIN_KEY = "12345" # Your smscoin.com account key

* **Provider** model::

    from smscoin.models import Provider

* Provides **CountryAdmin** to use at django admin interface

* Provides django management command to update sms tariffs frmo the cmscoin.com service::

    python manage.py update_sms_tariff

* help tag::

    {% smscoin_help %}

