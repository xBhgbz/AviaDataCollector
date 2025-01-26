def get_value_or_default(instance, field, default='--'):
    """Возвращает значение атрибута или его display-значение, либо значение по умолчанию."""
    value = getattr(instance, field, None)
    if value is not None:
        display_method = f'get_{field}_display'
        if hasattr(instance, display_method):
            return getattr(instance, display_method)()
        return value
    return default
