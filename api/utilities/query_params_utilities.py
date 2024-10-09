def clean_query_param(values, filter_class, return_type=str):
    if values is None:
        return values

    def clean_value(value):
        return return_type(filter_class.field_class().clean(value))

    return [clean_value(value) for value in values] if isinstance(values, list) else clean_value(values)
