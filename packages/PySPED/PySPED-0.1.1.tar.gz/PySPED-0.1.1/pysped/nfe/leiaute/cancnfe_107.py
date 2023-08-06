# -*- coding: utf-8 -*-
#
# PySPED - Python libraries to deal with Brazil's SPED Project
#
# Copyright (C) 2010-2012
# Copyright (C) Aristides Caldeira <aristides.caldeira at tauga.com.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2.1 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# PySPED - Bibliotecas Python para o
#          SPED - Sistema Público de Escrituração Digital
#
# Copyright (C) 2010-2012
# Copyright (C) Aristides Caldeira <aristides.caldeira arroba tauga.com.br>
#
# Este programa é um software livre: você pode redistribuir e/ou modificar
# este programa sob os termos da licença GNU Library General Public License,
# publicada pela Free Software Foundation, em sua versão 2.1 ou, de acordo
# com sua opção, qualquer versão posterior.
#
# Este programa é distribuido na esperança de que venha a ser útil,
# porém SEM QUAISQUER GARANTIAS, nem mesmo a garantia implícita de
# COMERCIABILIDADE ou ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA. Veja a
# GNU Library General Public License para mais detalhes.
#
# Você deve ter recebido uma cópia da GNU Library General Public License
# juntamente com este programa. Caso esse não seja o caso, acesse:
# <http://www.gnu.org/licenses/>
#

from __future__ import division, print_function, unicode_literals

from pysped.xml_sped import (ABERTURA, NAMESPACE_NFE, Signature,
                             TagCaracter, TagDataHora, TagDecimal,
                             TagInteiro, XMLNFe)
from pysped.nfe.leiaute import ESQUEMA_ATUAL_VERSAO_1 as ESQUEMA_ATUAL
import os


DIRNAME = os.path.dirname(__file__)


class InfCancEnviado(XMLNFe):
    def __init__(self):
        super(InfCancEnviado, self).__init__()
        self.Id    = TagCaracter(nome='infCanc', codigo='CP03', tamanho=[46, 46]    , raiz='//cancNFe', propriedade='Id')
        self.tpAmb = TagInteiro(nome='tpAmb'   , codigo='CP05', tamanho=[ 1,  1, 1] , raiz='//cancNFe/infCanc', valor=2)
        self.xServ = TagCaracter(nome='xServ'  , codigo='CP06', tamanho=[ 8,  8]    , raiz='//cancNFe/infCanc', valor='CANCELAR')
        self.chNFe = TagCaracter(nome='chNFe'   , codigo='CP07', tamanho=[44, 44, 44], raiz='//cancNFe/infCanc')
        self.nProt = TagCaracter(nome='nProt'   , codigo='CP08', tamanho=[15, 15, 15], raiz='//cancNFe/infCanc')
        self.xJust = TagCaracter(nome='xJust'  , codigo='CP09', tamanho=[15, 255]   , raiz='//cancNFe/infCanc')

    def get_xml(self):
        xml = XMLNFe.get_xml(self)

        self.Id.valor = 'ID' + self.chNFe.valor

        xml += self.Id.xml
        xml += self.tpAmb.xml
        xml += self.xServ.xml
        xml += self.chNFe.xml
        xml += self.nProt.xml
        xml += self.xJust.xml
        xml += '</infCanc>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.Id.xml    = arquivo
            self.tpAmb.xml = arquivo
            self.xServ.xml = arquivo
            self.chNFe.xml = arquivo
            self.nProt.xml = arquivo
            self.xJust.xml = arquivo

    xml = property(get_xml, set_xml)


class CancNFe(XMLNFe):
    def __init__(self):
        super(CancNFe, self).__init__()
        self.versao    = TagDecimal(nome='cancNFe', codigo='CP01', propriedade='versao', namespace=NAMESPACE_NFE, valor='1.07', raiz='/')
        self.infCanc   = InfCancEnviado()
        self.Signature = Signature()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema/', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'cancNFe_v1.07.xsd'

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.infCanc.xml

        #
        # Define a URI a ser assinada
        #
        self.Signature.URI = '#' + self.infCanc.Id.valor

        xml += self.Signature.xml
        xml += '</cancNFe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.infCanc.xml = arquivo
            self.Signature.xml = self._le_noh('//cancNFe/sig:Signature')

    xml = property(get_xml, set_xml)


class InfCancRecebido(XMLNFe):
    def __init__(self):
        super(InfCancRecebido, self).__init__()
        self.Id       = TagCaracter(nome='infCanc' , codigo='CR03' , tamanho=[17, 17]    , raiz='//retCancNFe', propriedade='Id', obrigatorio=False)
        self.tpAmb    = TagInteiro(nome='tpAmb'    , codigo='CR05' , tamanho=[1, 1, 1]   , raiz='//retCancNFe/infCanc', valor=2)
        self.verAplic = TagCaracter(nome='verAplic', codigo='CR06' , tamanho=[1, 20]     , raiz='//retCancNFe/infCanc')
        self.cStat    = TagCaracter(nome='cStat'    , codigo='CR07' , tamanho=[3, 3, 3]   , raiz='//retCancNFe/infCanc')
        self.xMotivo  = TagCaracter(nome='xMotivo' , codigo='CR08' , tamanho=[1, 255]    , raiz='//retCancNFe/infCanc')
        self.cUF      = TagInteiro(nome='cUF'      , codigo='CR08a', tamanho=[2, 2, 2]   , raiz='//retCancNFe/infCanc')
        self.chNFe    = TagCaracter(nome='chNFe'    , codigo='CR09' , tamanho=[44, 44, 44], raiz='//retcancNFe/infCanc', obrigatorio=False)
        self.dhRecbto = TagDataHora(nome='dhRecbto', codigo='CR10' ,                       raiz='//retCancNFe/infCanc', obrigatorio=False)
        self.nProt    = TagCaracter(nome='nProt'    , codigo='CR11' , tamanho=[15, 15, 15], raiz='//retCancNFe/infCanc', obrigatorio=False)

    def get_xml(self):
        xml = XMLNFe.get_xml(self)

        if self.Id.xml:
            xml += self.Id.xml
        else:
            xml += '<infCanc>'

        xml += self.tpAmb.xml
        xml += self.verAplic.xml
        xml += self.cStat.xml
        xml += self.xMotivo.xml
        xml += self.cUF.xml
        xml += self.chNFe.xml
        xml += self.dhRecbto.xml
        xml += self.nProt.xml
        xml += '</infCanc>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.Id.xml       = arquivo
            self.tpAmb.xml    = arquivo
            self.verAplic.xml = arquivo
            self.cStat.xml    = arquivo
            self.xMotivo.xml  = arquivo
            self.cUF.xml      = arquivo
            self.chNFe.xml    = arquivo
            self.dhRecbto.xml = arquivo
            self.nProt.xml    = arquivo

    xml = property(get_xml, set_xml)


class RetCancNFe(XMLNFe):
    def __init__(self):
        super(RetCancNFe, self).__init__()
        self.versao = TagDecimal(nome='retCancNFe', codigo='CR01', propriedade='versao', namespace=NAMESPACE_NFE, valor='1.07', raiz='/')
        self.infCanc = InfCancRecebido()
        self.Signature = Signature()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'retCancNFe_v1.07.xsd'

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.infCanc.xml

        if len(self.Signature.URI) and (self.Signature.URI.strip() != '#'):
            xml += self.Signature.xml

        xml += '</retCancNFe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.infCanc.xml   = arquivo
            self.Signature.xml = self._le_noh('//retCancNFe/sig:Signature')

    xml = property(get_xml, set_xml)

    def protocolo_formatado(self):
        if not self.infCanc.nProt.valor:
            return ''

        formatado = self.infCanc.nProt.valor
        formatado += ' - '
        formatado += self.infCanc.dhRecbto.formato_danfe()
        return formatado


class ProcCancNFe(XMLNFe):
    def __init__(self):
        super(ProcCancNFe, self).__init__()
        #
        # Atenção --- a tag procCancNFe tem que começar com letra minúscula, para
        # poder validar no XSD.
        #
        self.versao = TagDecimal(nome='procCancNFe', propriedade='versao', namespace=NAMESPACE_NFE, valor='1.07', raiz='/')
        self.cancNFe = CancNFe()
        self.retCancNFe = RetCancNFe()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'procCancNFe_v1.07.xsd'

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.cancNFe.xml.replace(ABERTURA, '')
        xml += self.retCancNFe.xml.replace(ABERTURA, '')
        xml += '</procCancNFe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.cancNFe.xml = arquivo
            self.retCancNFe.xml = arquivo

    xml = property(get_xml, set_xml)
