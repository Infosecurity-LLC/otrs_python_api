#!/usr/bin/env python3
"""
    Модуль предоставляет интерфейс для взаимодействия с OTRS 4 версии.
"""
from otrs_python_api.article import Article
from otrs_python_api.connection import Connection
from otrs_python_api.exceptions import InvalidTicketGetArgument, InvalidTicketCreateArgument, \
    InvalidTicketUpdateArgument
from otrs_python_api.ticket import Ticket


class OTRS:
    def __init__(self, url: str = None, login: str = None, password: str = None, interface: str = None,
                 session_timeout: int = None, priority: int = None, verify: bool = None, session_id: str = None,
                 session_time_created: int = None, webservice_url: str = None, connect_timeout: float = None,
                 read_timeout: float = None, connection: Connection = None):
        self.connection = connection or Connection(url=url, login=login, password=password, interface=interface,
                                                   session_timeout=session_timeout, session_id=session_id,
                                                   session_time_created=session_time_created,
                                                   priority=priority, verify=verify,
                                                   webservice_url=webservice_url, connect_timeout=connect_timeout,
                                                   read_timeout=read_timeout)

    def ticket_search(self, **kwargs) -> list:
        """
            Returns: list of tickets id
        """
        params = '&'.join([f'{k}={v}' for k, v in kwargs.items()])
        resp = self.connection.send_request(
            http_method='GET',
            semantic_url='Ticket?SessionID={SessionID}&{params}',
            params=params
        )
        return resp.get('TicketID', [])

    def ticket_get(self, ticket_id, articles: bool = True, dynamic_fields: bool = True, attachments: bool = True) \
            -> Ticket:
        if not isinstance(ticket_id, (str, int)):
            raise InvalidTicketGetArgument(f"Ticket id {ticket_id} must be str")
        if not isinstance(articles, bool):
            raise InvalidTicketGetArgument(f"Articles {ticket_id} must be bool")
        if not isinstance(dynamic_fields, bool):
            raise InvalidTicketGetArgument(f"Dynamic fields {dynamic_fields} must be bool")
        if not isinstance(attachments, bool):
            raise InvalidTicketGetArgument(f"Attachments {attachments} must be bool")

        args = {
            'AllArticles': int(articles),
            'DynamicFields': int(dynamic_fields),
            'Attachments': int(attachments)
        }
        params = '&'.join([f'{k}={v}' for k, v in args.items()])

        resp = self.connection.send_request(
            http_method='GET',
            semantic_url='Ticket/{TicketID}?SessionID={SessionID}&{params}',
            TicketID=ticket_id,
            params=params
        )
        return Ticket(**resp['Ticket'][0])

    def ticket_create(self, ticket: Ticket, article: Article, **kwargs) -> dict:
        """
            Return: {"TicketID": str, "TicketNumber": str, "ArticleID": str}
        """
        if not isinstance(ticket, Ticket):
            raise InvalidTicketCreateArgument(f"Ticket id {ticket} must be Ticket instance")
        if not isinstance(article, Article):
            raise InvalidTicketCreateArgument(f"Articles {article} must be Article instance")

        fields = self._prepare_fields(ticket, article, **kwargs)

        resp = self.connection.send_request(
            http_method='POST',
            semantic_url='Ticket?SessionID={SessionID}',
            Ticket=ticket.dict(dynamic_fields=True),
            **fields
        )
        return resp

    def ticket_update(self, ticket_id, ticket: Ticket, article: Article = None, **kwargs) -> dict:
        if not isinstance(ticket_id, (str, int)):
            raise InvalidTicketUpdateArgument(f"Ticket id {ticket_id} must be str")
        if not isinstance(ticket, Ticket):
            raise InvalidTicketUpdateArgument(f"Ticket {ticket} must be Ticket instance")
        if article and not isinstance(article, Article):
            raise InvalidTicketUpdateArgument(f"Article {article} must be Article instance")

        fields = self._prepare_fields(ticket, article, are_dynamic_fields_not_null=True, **kwargs)
        resp = self.connection.send_request(
            http_method='PATCH',
            semantic_url='Ticket/{TicketID}?SessionID={SessionID}',
            TicketID=ticket_id,
            Ticket=ticket.dict(),
            **fields
        )
        return resp

    @staticmethod
    def _prepare_fields(ticket: Ticket, article: Article = None, are_dynamic_fields_not_null: bool = False, **kwargs) \
            -> dict:
        if article:
            kwargs.update({'Article': article.dict()})

        dynamic_fields = ticket.get_dynamic_fields(not_null=are_dynamic_fields_not_null)
        if dynamic_fields:
            kwargs.update({'DynamicField': dynamic_fields})

        attachments = ticket.get_attachments()
        if attachments:
            kwargs.update({'Attachment': attachments})
        return kwargs
