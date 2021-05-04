import base64
import json

from otrs_python_api.exceptions import ArgumentMissingError, ArgumentInvalidError
from otrs_python_api.article import Article


class Ticket:
    def __init__(self, **kwargs):
        self._fields = {}
        self._fields.update(kwargs)
        self._tid = self._fields.get("TicketID", 0)
        self._dynamic_fields = {}
        self._attachments = []
        if self._fields.get('Article'):
            article_dict = self._fields['Article'][0]
            if 'Attachment' in article_dict:
                self._attachments = article_dict.pop('Attachment')
            self._article = Article(**article_dict)
            self._fields.pop('Article')
        else:
            self._article = None

        for field in list(self._fields):
            if field.startswith('DynamicField_'):
                self._dynamic_fields.update({field: self._fields[field]})
                self._fields.pop(field)

    def _parse_articles(self):
        lst = self._fields.get("Article", [])
        return [Article(item) for item in lst]

    def set_field(self, field_name, value):
        self._fields[field_name] = value

    def get_field(self, field_name):
        return self._fields.get(field_name)

    def set_dynamic_field(self, field_name, value):
        self._dynamic_fields['DynamicField_' + field_name] = value

    def get_dynamic_field(self, field_name):
        return self._dynamic_fields.get('DynamicField_' + field_name)

    def get_dynamic_fields(self, not_null=None):
        not_null = not_null or False
        df_list = []
        for k, v in self._dynamic_fields.items():
            if not_null and v or not not_null:
                df_list.append({"Name": k.split('_', 1)[1], "Value": v})
        return df_list

    @classmethod
    def create(cls, **kwargs):
        if 'Title' not in kwargs:
            raise ArgumentMissingError("Title required")
        if 'Queue' not in kwargs and 'QueueID' not in kwargs:
            raise ArgumentMissingError("Either Queue or QueueID required")
        if 'State' not in kwargs and 'StateID' not in kwargs:
            raise ArgumentMissingError("Either State or StateID required")
        if 'Priority' not in kwargs and 'PriorityID' not in kwargs:
            raise ArgumentMissingError(
                "Either Priority or PriorityID required")
        if 'CustomerUser' not in kwargs:
            raise ArgumentMissingError("CustomerUser is required")
        if 'Type' in kwargs and 'TypeID' in kwargs:
            raise ArgumentInvalidError("Either Type or TypeID - not both")
        if 'Service' not in kwargs and 'ServiceID' not in kwargs:
            raise ArgumentMissingError("Either Service or ServiceID required")
        return Ticket(**kwargs)

    @property
    def article(self):
        return self._article

    @article.setter
    def article(self, article):
        """ article : Article object """
        if not isinstance(article, Article):
            raise TypeError(("article should have Article type, "
                             "not {}").format(type(article)))
        self._article = article

    def add_attachment(self, attachment):
        if not isinstance(attachment, dict):
            raise TypeError()
        if not ('Content' in attachment and 'ContentType' in attachment):
            raise ValueError()
        if 'Filename' not in attachment or len(attachment) > 3:
            raise ValueError()
        self._attachments.append(attachment)

    def get_attachments(self):
        return self._attachments.copy()

    def json(self):
        return json.dumps(self.dict())

    def dict(self, articles=False, dynamic_fields=False, attachments=False):
        result_dict = {}
        result_dict.update(self._fields)
        if articles:
            result_dict['Article'] = self._article.dict()
        if dynamic_fields:
            result_dict.update(self._dynamic_fields)
        if attachments:
            result_dict['Attachment'] = self._attachments.copy()
        return result_dict

    def __repr__(self):
        return "<{0}(id={1}, number={2})>".format(
            self.__class__.__name__,
            self._tid,
            self._fields.get('TicketNumber'))
