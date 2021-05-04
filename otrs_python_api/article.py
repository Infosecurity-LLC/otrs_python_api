class Article:
    def __init__(self, **kwargs):
        self._fields = {}
        if 'Subject' not in kwargs or 'Body' not in kwargs:
            raise TypeError()
        self._fields.update(kwargs)

        if 'MimeType' not in self._fields and \
                'ContentType' not in self._fields:
            self._fields['MimeType'] = 'text/plain'
            self._fields['ContentType'] = 'text/plain'
        if 'Charset' not in self._fields:
            self._fields['Charset'] = 'UTF8'

        self._dynamic_fields = {}
        for field in list(self._fields):
            if field.startswith('DynamicField_'):
                self._dynamic_fields.update({field: self._fields[field]})
                self._fields.pop(field)

    def dict(self):
        return self._fields.copy()

    def set_field(self, field_name, value):
        self._fields[field_name] = value

    def get_field(self, field_name):
        return self._fields.get(field_name)

    def __repr__(self):
        return "<Article(Subject=\"{0}\", Body=\"{1}\")>".format(
            self._fields['Subject'], repr(self._fields['Body']))


def debug_article(html=False):
    """
        Создание тестового article для отладки.
        html: boolean - определеяет, должен ли MimeType быть text/html.
    """
    if html:
        return Article(Subject="TestSubject", Body="TestBody",
                       MimeType='text/html')
    else:
        return Article(Subject="TestSubject", Body="TestBody")
