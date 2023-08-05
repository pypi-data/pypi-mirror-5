from __future__ import unicode_literals
import logging
import pickle
from StringIO import StringIO
import sys

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models as django_models
from django.test.testcases import TransactionTestCase
from django.utils.unittest.case import skipIf

from .. import get_tenant_model
from ..models import (db_schema_table, Tenant, TenantModel, TenantModelBase,
    TenantModelDescriptor, TenantSpecificModel)
from ..utils import model_name

from .managers import ManagerOtherSubclass, ManagerSubclass
from .models import (AbstractTenantModel, NonTenantModel, RelatedSpecificModel,
    RelatedTenantModel, SpecificModel, SpecificModelProxy,
    SpecificModelProxySubclass, SpecificModelSubclass, TenantModelMixin)
from .utils import logger, skipIfCustomTenant, TenancyTestCase


class TenantTest(TransactionTestCase):
    def assertSwapFailure(self, tenant_model, expected_message):
        with self.assertRaisesMessage(ImproperlyConfigured, expected_message):
            with self.settings(TENANCY_TENANT_MODEL=tenant_model):
                get_tenant_model()

    def test_invalid_tenant_user_model_format(self):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger.addHandler(handler)
        with self.settings(TENANCY_TENANT_MODEL='invalid'):
            pass
        logger.removeHandler(handler)
        stream.seek(0)
        self.assertIn(
            "TENANCY_TENANT_MODEL must be of the form 'app_label.model_name'",
            stream.read()
        )

    def test_swap_failures(self):
        """
        Make sure tenant swap failures raise the correct exception
        """
        self.assertSwapFailure(
            'not.Installed',
            "TENANCY_TENANT_MODEL refers to model 'not.Installed' that has not been installed"
        )
        self.assertSwapFailure(
            'contenttypes.ContentType',
            "TENANCY_TENANT_MODEL refers to models 'contenttypes.ContentType' which is not a subclass of 'tenancy.AbstractTenant'"
        )

    @skipIfCustomTenant
    def test_content_types_deleted(self):
        """
        Make sure content types of tenant models are deleted upon their related
        tenant deletion.
        """
        tenant = Tenant.objects.create(name='tenant')
        model = tenant.specificmodels.model
        content_type = ContentType.objects.get_for_model(model)
        tenant.delete()
        self.assertFalse(ContentType.objects.filter(pk=content_type.pk).exists())


class TenantModelsCacheTest(TenancyTestCase):
    def test_initialized_models(self):
        """
        Make sure models are loaded upon model initialization.
        """
        self.assertIn('models', self.tenant.__dict__)


class TenantModelBaseTest(TenancyTestCase):
    def test_simple_instancecheck(self):
        instance = self.tenant.specificmodels.create()
        self.assertIsInstance(instance, django_models.Model)
        self.assertIsInstance(instance, TenantModelMixin)
        self.assertIsInstance(instance, SpecificModel)
        self.assertNotIsInstance(instance, SpecificModelSubclass)
        self.assertNotIsInstance(instance, RelatedSpecificModel)
        self.assertNotIsInstance(instance, TenantModelBaseTest)

    def test_concrete_inheritance_instancecheck(self):
        instance = self.tenant.specific_models_subclasses.create()
        self.assertIsInstance(instance, django_models.Model)
        self.assertIsInstance(instance, TenantModelMixin)
        self.assertIsInstance(instance, SpecificModel)
        self.assertIsInstance(instance, SpecificModelSubclass)
        self.assertNotIsInstance(instance, RelatedSpecificModel)
        self.assertNotIsInstance(instance, TenantModelBaseTest)

    def test_proxy_inheritance_instancecheck(self):
        instance = self.tenant.specific_model_proxies.create()
        self.assertIsInstance(instance, django_models.Model)
        self.assertIsInstance(instance, TenantModelMixin)
        self.assertIsInstance(instance, SpecificModel)
        self.assertIsInstance(instance, SpecificModelProxy)
        self.assertNotIsInstance(instance, RelatedSpecificModel)
        self.assertNotIsInstance(instance, TenantModelBaseTest)

    def assertIsSubclass(self, cls, base):
        self.assertTrue(issubclass(cls, base))

    def assertIsNotSubclass(self, cls, base):
        self.assertFalse(issubclass(cls, base))

    def test_subclasscheck(self):
        self.assertIsSubclass(SpecificModel, TenantModelMixin)
        tenant_specific_model = self.tenant.specificmodels.model
        self.assertIsSubclass(tenant_specific_model, AbstractTenantModel)
        self.assertIsSubclass(tenant_specific_model, SpecificModel)
        self.assertIsSubclass(tenant_specific_model, django_models.Model)
        self.assertIsNotSubclass(tenant_specific_model, SpecificModelSubclass)
        self.assertIsNotSubclass(tenant_specific_model, RelatedSpecificModel)
        self.assertIsNotSubclass(tenant_specific_model, tuple)

    def test_concrete_inheritance_subclasscheck(self):
        tenant_specific_model = self.tenant.specificmodels.model
        tenant_specific_model_subclass = self.tenant.specific_models_subclasses.model
        self.assertIsSubclass(tenant_specific_model_subclass, SpecificModel)
        self.assertIsSubclass(tenant_specific_model_subclass, tenant_specific_model)

    def test_proxy_inheritance_subclasscheck(self):
        specific_model = self.tenant.specificmodels.model
        specific_model_proxy = SpecificModelProxy.for_tenant(self.tenant)
        self.assertIsSubclass(specific_model_proxy, SpecificModel)
        self.assertIsSubclass(specific_model_proxy, SpecificModelProxy)
        self.assertIsSubclass(specific_model_proxy, specific_model)
        specific_model_proxy_subclass = SpecificModelProxySubclass.for_tenant(self.tenant)
        self.assertIsSubclass(specific_model_proxy_subclass, SpecificModel)
        self.assertIsSubclass(specific_model_proxy_subclass, SpecificModelProxy)
        self.assertIsSubclass(specific_model_proxy_subclass, SpecificModelProxySubclass)
        self.assertIsSubclass(specific_model_proxy_subclass, specific_model)
        self.assertIsSubclass(specific_model_proxy_subclass, specific_model_proxy)

    def assertPickleEqual(self, obj):
        pickled = pickle.dumps(obj)
        self.assertEqual(pickle.loads(pickled), obj)

    @skipIf(sys.version_info < (2, 7),
            "Model class can't be pickled on python < 2.7")
    def test_pickling(self):
        self.assertPickleEqual(SpecificModel)
        self.assertPickleEqual(self.tenant.specificmodels.model)
        self.assertPickleEqual(self.tenant.specificmodels.model.__bases__[0])
        self.assertPickleEqual(self.tenant.specific_models_subclasses.model)
        self.assertPickleEqual(self.tenant.specific_models_subclasses.model.__bases__[0])

    def test_tenant_specific_model_dynamic_subclassing(self):
        """
        Make sure tenant specific models can be dynamically subclassed.
        """
        model = self.tenant.specificmodels.model
        model_subclass = type(
            str("%sDynamicSubclass" % model.__name__),
            (model,),
            {'__module__': model.__module__}
        )
        self.assertEqual(model.tenant, model_subclass.tenant)
        self.assertIsSubclass(model_subclass, model)
        self.assertIsNotSubclass(model, model_subclass)

    def test_exceptions_subclassing(self):
        """
        Make sure tenant specific models exceptions subclass their exposed
        model one.
        """
        for model in TenantModelBase.references:
            tenant_model = model.for_tenant(self.tenant)
            try:
                tenant_model._default_manager.get()
            except Exception as e:
                self.assertIsInstance(e, model.DoesNotExist)
                for parent in model._meta.parents:
                    self.assertIsInstance(e, parent.DoesNotExist)

    def test_parent_subclassing(self):
        """
        Make sure references to the exposed model are all removed.
        """
        tenant_specific_model = self.tenant.specificmodels.model
        self.assertNotIn(
            SpecificModel,
            tenant_specific_model._meta.parents
        )
        attr_name = "%s_ptr" % model_name(SpecificModel._meta)
        self.assertFalse(hasattr(tenant_specific_model, attr_name))

    def test_manager_assignment(self):
        """
        Managers should be inherited correctly.
        """
        # Concrete
        specific_model = SpecificModel.for_tenant(self.tenant)
        self.assertIsInstance(specific_model._default_manager, ManagerSubclass)
        self.assertIsInstance(specific_model.objects, ManagerSubclass)
        self.assertIsInstance(
            specific_model.custom_objects, ManagerOtherSubclass
        )
        # Proxy
        specific_model_proxy = SpecificModelProxy.for_tenant(self.tenant)
        self.assertIsInstance(
            specific_model_proxy._default_manager, ManagerOtherSubclass
        )
        self.assertIsInstance(
            specific_model_proxy.objects, ManagerOtherSubclass
        )
        self.assertIsInstance(
            specific_model_proxy.proxied_objects, ManagerSubclass
        )
        # Concrete subclass
        specific_model_subclass = SpecificModelSubclass.for_tenant(self.tenant)
        self.assertIsInstance(
            specific_model_subclass._default_manager, ManagerOtherSubclass
        )
        self.assertIsInstance(
            specific_model_subclass.objects, ManagerOtherSubclass
        )


class TenantModelDescriptorTest(TenancyTestCase):
    def test_class_accessing(self):
        """
        Make sure the descriptor is available from the class.
        """
        self.assertIsInstance(Tenant.specificmodels, TenantModelDescriptor)

    def test_related_name(self):
        """
        Make sure the descriptor is correctly attached to the Tenant model
        when the related_name is specified or not.
        """
        self.assertTrue(issubclass(
            self.tenant.specificmodels.model, SpecificModel)
        )
        self.assertTrue(issubclass(
            self.tenant.related_specific_models.model, RelatedSpecificModel)
        )

    def test_content_type_created(self):
        """
        Make sure the content type associated with the returned model is
        always created.
        """
        opts = self.tenant.specificmodels.model._meta
        self.assertTrue(
            ContentType.objects.filter(
                app_label=opts.app_label,
                model=model_name(opts)
            ).exists()
        )


class TenantModelTest(TenancyTestCase):
    def test_isolation_between_tenants(self):
        """
        Make sure instances created in a tenant specific schema are not
        shared between tenants.
        """
        self.tenant.related_specific_models.create()
        self.assertEqual(self.other_tenant.related_specific_models.count(), 0)
        self.other_tenant.related_specific_models.create()
        self.assertEqual(self.tenant.related_specific_models.count(), 1)

    def test_db_table(self):
        """
        Make sure the `db_table` associated with tenant models is correctly
        prefixed based on the tenant and suffixed by the un-managed model's
        `db_table`.
        """
        self.assertEqual(
            self.tenant.specificmodels.model._meta.db_table,
            db_schema_table(self.tenant, SpecificModel._meta.db_table)
        )
        self.assertEqual(
            self.tenant.specific_models_subclasses.model._meta.db_table,
            db_schema_table(self.tenant, SpecificModelSubclass._meta.db_table)
        )

    def test_field_names(self):
        """
        Make sure tenant specific models' fields are the same as the one
        defined on the un-managed one.
        """
        models = (
            SpecificModel,
            SpecificModelSubclass,  # Test inheritance scenarios
            RelatedTenantModel,  # And models with m2m fields
        )
        for tenant in Tenant.objects.all():
            for model in models:
                opts = model._meta
                tenant_model = model.for_tenant(tenant)
                tenant_opts = tenant_model._meta
                for field in (opts.local_fields + opts.many_to_many):
                    tenant_field = tenant_opts.get_field(field.name)
                    self.assertEqual(tenant_field.__class__, field.__class__)

    def test_foreign_key_between_tenant_models(self):
        """
        Make sure foreign keys between TenantModels work correctly.
        """
        for tenant in Tenant.objects.all():
            # Test object creation
            specific = tenant.specificmodels.create()
            related = tenant.related_tenant_models.create(fk=specific)
            # Test reverse related manager
            self.assertEqual(specific.fks.get(), related)
            # Test reverse filtering
            self.assertEqual(tenant.specificmodels.filter(fks=related).get(), specific)

    def test_m2m(self):
        """
        Make sure m2m between TenantModels work correctly.
        """
        for tenant in Tenant.objects.all():
            # Test object creation
            related = tenant.related_tenant_models.create()
            specific_model = related.m2m.create()
            # Test reverse related manager
            self.assertEqual(specific_model.m2ms.get(), related)
            # Test reverse filtering
            self.assertEqual(tenant.specificmodels.filter(m2ms=related).get(), specific_model)

    def test_m2m_with_through(self):
        for tenant in Tenant.objects.all():
            related = tenant.related_tenant_models.create()
            specific = tenant.specificmodels.create()
            tenant.m2m_specifics.create(
                related=related,
                specific=specific
            )
            self.assertEqual(related.m2m_through.get(), specific)
            self.assertEqual(specific.m2ms_through.get(), related)

    def test_m2m_to_non_tenant(self):
        """
        Make sure m2m between TenantModels work correctly.
        """
        for tenant in Tenant.objects.all():
            # Test object creation
            related = tenant.related_tenant_models.create()
            non_tenant = related.m2m_non_tenant.create()
            # Test reverse related manager
            reverse_descriptor_name = "tenant_%s_relatedtenantmodels" % tenant.name
            self.assertEqual(getattr(non_tenant, reverse_descriptor_name).get(), related)
            # Test reverse filtering
            self.assertEqual(NonTenantModel.objects.filter(
                **{reverse_descriptor_name:related}).get(), non_tenant)

    def test_not_managed_auto_intermediary_model(self):
        """
        Make sure that exposed un-managed models with m2m relations have their
        intermediary models also un-managed.
        """
        get_field = RelatedTenantModel._meta.get_field
        self.assertFalse(get_field('m2m').rel.through._meta.managed)
        self.assertFalse(get_field('m2m_to_undefined').rel.through._meta.managed)
        self.assertFalse(get_field('m2m_through').rel.through._meta.managed)
        self.assertFalse(get_field('m2m_recursive').rel.through._meta.managed)
        self.assertFalse(get_field('m2m_non_tenant').rel.through._meta.managed)

    def test_invalid_foreign_key_related_name(self):
        # Ensure `related_name` with no %(tenant)s format placeholder also
        # raises an improperly configured error.
        with self.assertRaisesMessage(ImproperlyConfigured,
            "Since `InvalidRelatedName.fk` is originating from an instance "
            "of `TenantModelBase` and not pointing to one "
            "its `related_name` option must ends with a "
            "'+' or contain the '%(class)s' format "
            "placeholder."):
            class InvalidRelatedName(TenantModel):
                fk = django_models.ForeignKey(NonTenantModel, related_name='no-tenant')

    def test_invalid_m2m_through(self):
        with self.assertRaisesMessage(ImproperlyConfigured,
            "Since `InvalidThrough.m2m` is originating from an instance of "
            "`TenantModelBase` its `through` option must also be pointing "
            "to one."):
            class InvalidThrough(TenantModel):
                m2m = django_models.ManyToManyField(NonTenantModel,
                                                    through='InvalidIntermediary')
            class InvalidIntermediary(django_models.Model):
                pass

    def test_non_tenant_related_descriptor(self):
        """
        Make sure related descriptor are correctly attached to non-tenant
        models and removed on tenant deletion.
        """
        for tenant in Tenant.objects.all():
            attr = "tenant_%s_specificmodels" % tenant.name
            self.assertTrue(hasattr(NonTenantModel, attr))
            tenant.delete()
            self.assertFalse(hasattr(NonTenantModel, attr))

    def test_subclassing(self):
        """
        Make sure tenant model subclasses share the same tenant.
        """
        for tenant in Tenant.objects.all():
            parents = tenant.specific_models_subclasses.model._meta.parents
            for parent in parents:
                if issubclass(parent, TenantSpecificModel):
                    self.assertEqual(parent.tenant, tenant)
            tenant.specific_models_subclasses.create()
            self.assertEqual(tenant.specificmodels.count(), 1)

    def test_signals(self):
        """
        Make sure signals are correctly dispatched for tenant models
        """
        for tenant in Tenant.objects.all():
            signal_model = tenant.signal_models.model
            instance = signal_model()
            instance.save()
            instance.delete()
            self.assertListEqual(
                signal_model.logs(),
                [
                 django_models.signals.pre_init,
                 django_models.signals.post_init,
                 django_models.signals.pre_save,
                 django_models.signals.post_save,
                 django_models.signals.pre_delete,
                 django_models.signals.post_delete
                 ]
            )


class NonTenantModelTest(TransactionTestCase):
    def test_fk_to_tenant(self):
        """
        Non-tenant models shouldn't be allowed to have a ForeignKey pointing
        to an instance of `TenantModelBase`.
        """
        with self.assertRaisesMessage(ImproperlyConfigured,
            "`NonTenantFkToTenant.fk`'s `to` option` can't point to an "
            "instance of `TenantModelBase` since it's not one itself."):
            class NonTenantFkToTenant(django_models.Model):
                fk = django_models.ForeignKey('UndeclaredSpecificModel')

            class UndeclaredSpecificModel(TenantModel):
                pass

    def test_m2m_to_tenant(self):
        """
        Non-tenant models shouldn't be allowed to have ManyToManyField pointing
        to an instance of `TenantModelBase`.
        """
        with self.assertRaisesMessage(ImproperlyConfigured,
            "`NonTenantM2MToTenant.m2m`'s `to` option` can't point to an "
            "instance of `TenantModelBase` since it's not one itself."):
            class NonTenantM2MToTenant(django_models.Model):
                m2m = django_models.ManyToManyField(SpecificModel)
