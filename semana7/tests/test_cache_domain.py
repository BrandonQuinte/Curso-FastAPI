import pytest
from app.cache.redis_config import cache_manager

class TestDomainCache:

    def test_cache_basic_functionality(self):
        """Verifica que se pueda setear, recuperar e invalidar un valor"""
        test_key = "test_entity_123"
        test_data = {"id": 123, "nombre": "Test Entity"}

        # Guardar
        assert cache_manager.set_cache(test_key, test_data)

        # Leer
        cached_data = cache_manager.get_cache(test_key)
        assert cached_data == test_data

        # Invalidar
        cache_manager.invalidate_cache(test_key)
        assert cache_manager.get_cache(test_key) is None

    def test_domain_specific_caching(self):
        """Verifica caching usando un TTL profile específico"""
        entity_data = {"specific_field": "domain_value"}
        cache_key = "domain_specific_test"

        # Guardar con ttl_type 'frequent_data'
        cache_manager.set_cache(cache_key, entity_data, ttl_type="frequent_data")
        retrieved = cache_manager.get_cache(cache_key)

        assert retrieved == entity_data

        # Invalidar
        cache_manager.invalidate_cache(cache_key)
        assert cache_manager.get_cache(cache_key) is None

    def test_invalidate_by_pattern(self):
        """Verifica que la invalidación por patrón funciona"""
        k1, k2 = "curso:1", "curso:2"
        d1, d2 = {"id": 1}, {"id": 2}

        cache_manager.set_cache(k1, d1)
        cache_manager.set_cache(k2, d2)

        # Ambos deberían estar en cache
        assert cache_manager.get_cache(k1) == d1
        assert cache_manager.get_cache(k2) == d2

        # Invalida por patrón
        cache_manager.invalidate_cache("curso:*")

        # Ambos deberían desaparecer
        assert cache_manager.get_cache(k1) is None
        assert cache_manager.get_cache(k2) is None

    def test_overwrite_existing_key(self):
        """Verifica que un valor pueda sobrescribirse en cache"""
        key = "overwrite_test"
        first_value = {"id": 1}
        second_value = {"id": 2}

        cache_manager.set_cache(key, first_value)
        assert cache_manager.get_cache(key) == first_value

        # Sobrescribir
        cache_manager.set_cache(key, second_value)
        assert cache_manager.get_cache(key) == second_value

        # Limpieza
        cache_manager.invalidate_cache(key)
