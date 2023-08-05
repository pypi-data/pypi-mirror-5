# -*- coding: utf-8 -*-
from decimal import Decimal
import logging
import datetime
from django.core.urlresolvers import reverse
from django.db.models import get_model
from django.utils.timezone import utc
import requests
import time
from getpaid.signals import user_data_query
from getpaid.backends import PaymentProcessorBase
from lxml import etree

logger = logging.getLogger('getpaid.backends.moip')


class MoipTransactionStatus:
    AUTHORIZED = 1
    STARTED = 2
    IN_PROGRESS = 3
    AVAILABLE = 4
    CANCELED = 5
    PENDING = 6
    CHARGEBACK = 7
    IN_DISPUTE = 8
    REFUNDED = 9


class PaymentProcessor(PaymentProcessorBase):
    BACKEND = 'getpaid.backends.moip'
    BACKEND_NAME = 'Moip'
    BACKEND_ACCEPTED_CURRENCY = ('BRL', )

    _SEND_INSTRUCTION_PAGE = '/ws/alpha/EnviarInstrucao/Unica'
    _RUN_INSTRUCTION_PAGE = 'Instrucao.do?token='
    _ITEM_DATA_REQUIRED_FIELDS = ('id', 'description', 'quantity', 'value')

    _USER_DATA_TO_MOIP = {
        'name': 'Nome',  # Nome completo do cliente.
        'address': 'Logradouro',  # Logradouro do cliente (ex: Rua, Av, etc.)
        'address_number': 'Numero',  # Nº do imóvel do cliente (ex: 12)
        'address_complement': 'Complemento',  # Complemento (ex: Sala 109 ou Casa 1)
        'address_zip_code': 'CEP',  # O CEP de 8 dígitos do cliente. Somente números (ex: 22345678)
        'address_quarter': 'Bairro',  # Bairro do cliente
        'address_city': 'Cidade',  # Cidade do cliente (ex: São Paulo)
        'address_state': 'Estado',  # Estado do cliente (SP) no formato duas letras
        'phone': 'TelefoneFixo',  # Telefone fixo do cliente
        'email': 'Email',  # E-mail do cliente
    }

    def get_gateway_url(self, request):
        if PaymentProcessor.get_backend_setting('testing', False):
            gateway_url = "https://desenvolvedor.moip.com.br/sandbox"
        else:
            gateway_url = "https://www.moip.com.br"

        xml_body = etree.Element("EnviarInstrucao")
        xml_instruction = etree.SubElement(xml_body, "InstrucaoUnica")

        etree.SubElement(xml_instruction, "Razao").text = self.get_order_description(self.payment, self.payment.order)

        xml_values = etree.SubElement(xml_instruction, "Valores")
        etree.SubElement(xml_values, "Valor", moeda=self.payment.currency).text = str(self.payment.amount)

        etree.SubElement(xml_instruction, "IdProprio").text = "%s-%s" % (str(self.payment.id), str(time.time()))
        etree.SubElement(xml_instruction, "URLRetorno").text = PaymentProcessor._get_view_full_url(request, 'getpaid-moip-success', args=(self.payment.id,))
        etree.SubElement(xml_instruction, "URLNotificacao").text = PaymentProcessor._get_view_full_url(request, 'getpaid-moip-notifications')

        # collect customer data
        customer_info = {}
        user_data_query.send(sender=None, order=self.payment.order, user_data=customer_info)

        if customer_info:
            xml_buyer = etree.SubElement(xml_instruction, "Pagador")

            for field in ('name', 'email'):
                if field in customer_info and field in ('name', 'email'):
                    etree.SubElement(xml_buyer, self._USER_DATA_TO_MOIP[field]).text = customer_info[field]

            xml_buyer_address = etree.SubElement(xml_buyer, "EnderecoCobranca")
            for field in self._USER_DATA_TO_MOIP:
                if field in customer_info and field not in ('name', 'email'):
                    etree.SubElement(xml_buyer_address, self._USER_DATA_TO_MOIP[field]).text = customer_info[field]

        payment_full_url = "%s%s" % (gateway_url, self._SEND_INSTRUCTION_PAGE)
        user = PaymentProcessor.get_backend_setting('token')
        pwd = PaymentProcessor.get_backend_setting('key')
        contents = etree.tostring(xml_body, encoding='utf-8')

        response = requests.post(payment_full_url, auth=(user, pwd), data=contents).text
        moip_payment_token = etree.XML(response)[0][2].text

        return "%s/%s%s " % (gateway_url, self._RUN_INSTRUCTION_PAGE, moip_payment_token), 'GET', {}

    @staticmethod
    def process_notification(params):
        Payment = get_model('getpaid', 'Payment')
        try:
            payment = Payment.objects.get(pk=int(params["id"].split("-")[0]))
        except Payment.DoesNotExist:
            logger.error('Payment does not exist with pk=%d' % params["id"])
            return

        status_code = int(params["status"])
        if status_code in (MoipTransactionStatus.AUTHORIZED,
                           MoipTransactionStatus.AVAILABLE):
            payment.amount_paid = Decimal(params["amount"])
            payment.paid_on = datetime.datetime.utcnow().replace(tzinfo=utc)
            payment.change_status('paid')
        elif status_code in (MoipTransactionStatus.CANCELED,
                             MoipTransactionStatus.REFUNDED,
                             MoipTransactionStatus.CHARGEBACK):
            payment.change_status('failed')

    @staticmethod
    def _get_view_full_url(request, view_name, args=None):
        url = reverse(view_name, args=args)
        return 'http://%s%s' % (request.get_host(), url)
