=================
django-i18n-model
=================

Adding translations to Django models is a topic that has been discussed from a
vast variety of angles, and yet still not very well defined. django-i18n-model
is yet another solution for adding i18n to your models.

It is very similar to django-hvad_ in that it uses the actual database and
metaclasses to do its job, but unlike django-hvad, it does not modify the source
model. Unlike django-modeltranslation_, and like django-hvad, django-i18n-models
does not add any new fields to the source model.

One interesting library for handling i18n in models is django is django-lingua_.
Unlike any of the database-backed solutions, it uses the gettext interface to
facilitate translation of model data. While we find lingua interesting in
principle, we believe translation of database data should be kept in the
database (and lingua didn't work very well for us anyway).

The main advantage of using django-i18n-model is the ability to:

1. Add custom fields to translations

2. Ability to use South migrations

3. Not necessary to modify your existing models

Keep in mind that this library is fairly young so it still lacks many of the
convenience features such as automatic translation of fields and admin
integration (features that other solutions do promise). Those features are
still being designed and are planned for future releases.

Overview
========

django-i18n-model works by creating a completely separate model for translation.
It does so by obtaining information about the model fields from the source model
and creating a clone with additional fields called ``i18n_language`` and
``i18n_source``. It currently offers several ways of referencing the translation
source model and the set of fields to include in the translations.

Installation
============

TODO

Basic usage
===========

To create a new translation model, simply subclass the ``I18nModel`` class::

    from django.db import models
    from i18n_model.models import I18nModel


    class Source(models.Model):
        """ Your normal model """
        title = models.CharField(max_length=20)
        body = models.TextField()
        date = models.DateField()

    class SourceI18N(I18nModel):
        class Meta:
            translatable_fields = ('title', 'body')

With the above setup, a new model is created that is named ``SourceI18N`` and it
will contain the ``title``, ``body``, ``i18n_language`` and ``i18n_source``
fields. The ``i18n_source`` is a foreign key to ``Source`` model.

Creating translations
=====================

You can create translations as usual by simply creating a new instance of the
``*I18N`` model, or you can use the ``translate`` class method on the ``*I18N``
class. Here is an example of the latter using the above code::

    my_source = Source(title='Test', body='test', date=datetime.date.today())
    my_translation = SourceI18N.translate(
        my_source,
        'sr',
        title='Тест',
        body='тест'
    )

Getting translations
====================

The translations are obtained using the ``translate`` class method. You can
obtain translations for a specific language by calling the ``translate``
class method without any keyword arguments::

    translation = SourceI18N.translate(my_source, 'sr')
    translation.title  # >> 'Тест'
    translation.body  # >> тест'

It is also possible to obtain translations directly from the source model. The
foreign key on the translation model creates a ``translations`` property on the
source model. This property is an instance of ``I18nManager`` custom manager,
and it behaves like a normal Django manager for most part. To get all
translations for a given object::

    my_source.translations.all()

To get translations for a specific language, the manager has shortcut manager
methods that are named after locales::

    translation = my_source.translations.sr().get()

Getting translation for current language
========================================

You can use the custom manager's ``current_language`` method to retrieve
translations for the currently active language::

    SourceI18N.objects.current_language()

This also works on related objects::

    my_source.translations.current_language().get()

.. _django-hvad: http://django-hvad.readthedocs.org/en/latest/index.html
.. _django-modeltranslation: https://github.com/deschler/django-modeltranslation
.. _django-lingua: http://code.google.com/p/django-lingua/