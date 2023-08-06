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

from pysped.xml_sped import (ABERTURA, NAMESPACE_CTE, Signature, TagCaracter,
                             TagDataHora, TagDecimal, TagInteiro, XMLNFe)
from pysped.cte.leiaute import ESQUEMA_ATUAL_VERSAO_104 as ESQUEMA_ATUAL
import os


DIRNAME = os.path.dirname(__file__)


class InfInutEnviado(XMLNFe):
    def __init__(self):
        super(InfInutEnviado, self).__init__()
        self.Id     = TagCaracter(nome='infInut', codigo='DP03', tamanho=[41, 41] , raiz='//inutCTe', propriedade='Id')
        self.tpAmb  = TagInteiro(nome='tpAmb'   , codigo='DP05', tamanho=[1, 1, 1], raiz='//inutCTe/infInut', valor=2)
        self.xServ  = TagCaracter(nome='xServ'  , codigo='DP06', tamanho=[10, 10] , raiz='//inutCTe/infInut', valor='INUTILIZAR')
        self.cUF    = TagInteiro(nome='cUF'     , codigo='DP07', tamanho=[2, 2, 2], raiz='//inutCTe/infInut')
        self.ano    = TagCaracter(nome='ano'    , codigo='DP08', tamanho=[2, 2]   , raiz='//inutCTe/infInut')
        self.CNPJ   = TagCaracter(nome='CNPJ'   , codigo='DP09', tamanho=[3, 14]  , raiz='//inutCTe/infInut')
        self.mod    = TagInteiro(nome='mod'     , codigo='DP10', tamanho=[2, 2, 2], raiz='//inutCTe/infInut', valor=55)
        self.serie  = TagInteiro(nome='serie'   , codigo='DP11', tamanho=[1, 3]   , raiz='//inutCTe/infInut')
        self.nCTIni = TagInteiro(nome='nCTIni'  , codigo='DP12', tamanho=[1, 9]   , raiz='//inutCTe/infInut')
        self.nCTFin = TagInteiro(nome='nCTFin'  , codigo='DP13', tamanho=[1, 9]   , raiz='//inutCTe/infInut')
        self.xJust  = TagCaracter(nome='xJust'  , codigo='DP14', tamanho=[15, 255], raiz='//inutCTe/infInut')

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += self.Id.xml
        xml += self.tpAmb.xml
        xml += self.xServ.xml
        xml += self.cUF.xml
        xml += self.ano.xml
        xml += self.CNPJ.xml
        xml += self.mod.xml
        xml += self.serie.xml
        xml += self.nCTIni.xml
        xml += self.nCTFin.xml
        xml += self.xJust.xml
        xml += '</infInut>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.Id.xml     = arquivo
            self.tpAmb.xml  = arquivo
            self.xServ.xml  = arquivo
            self.cUF.xml    = arquivo
            self.ano.xml    = arquivo
            self.CNPJ.xml   = arquivo
            self.mod.xml    = arquivo
            self.serie.xml  = arquivo
            self.nCTIni.xml = arquivo
            self.nCTFin.xml = arquivo
            self.xJust.xml  = arquivo

    xml = property(get_xml, set_xml)


class InutCTe(XMLNFe):
    def __init__(self):
        super(InutCTe, self).__init__()
        self.versao  = TagDecimal(nome='inutCTe', codigo='DP01', propriedade='versao', namespace=NAMESPACE_CTE, valor='1.04', raiz='/')
        self.infInut = InfInutEnviado()
        self.Signature = Signature()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'inutCte_v1.04.xsd'

        self.chave = ''

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.infInut.xml

        #
        # Define a URI a ser assinada
        #
        self.Signature.URI = '#' + self.infInut.Id.valor

        xml += self.Signature.xml
        xml += '</inutCTe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.infInut.xml   = arquivo
            self.Signature.xml = self._le_noh('//inutCTe/sig:Signature')

    xml = property(get_xml, set_xml)

    def monta_chave(self):
        chave = unicode(self.infInut.cUF.valor).zfill(2)
        #chave += self.infInut.ano.valor.zfill(2)
        chave += self.infInut.CNPJ.valor.zfill(14)
        chave += unicode(self.infInut.mod.valor).zfill(2)
        chave += unicode(self.infInut.serie.valor).zfill(3)
        chave += unicode(self.infInut.nCTIni.valor).zfill(9)
        chave += unicode(self.infInut.nCTFin.valor).zfill(9)

        self.chave = chave
        return chave

    def gera_nova_chave(self):
        chave = self.monta_chave()

        #
        # Define o Id
        #
        self.infInut.Id.valor = 'ID' + chave


class InfInutRecebido(XMLNFe):
    def __init__(self):
        super(InfInutRecebido, self).__init__()
        self.Id       = TagCaracter(nome='infInut' , codigo='DR03', tamanho=[17, 17]    , raiz='//retInutCTe', propriedade='Id', obrigatorio=False)
        self.tpAmb    = TagInteiro(nome='tpAmb'    , codigo='DR05', tamanho=[1, 1, 1]   , raiz='//retInutCTe/infInut', valor=2)
        self.verAplic = TagCaracter(nome='verAplic', codigo='DR06', tamanho=[1, 20]     , raiz='//retInutCTe/infInut')
        self.cStat    = TagCaracter(nome='cStat'   , codigo='DR07', tamanho=[3, 3, 3]   , raiz='//retInutCTe/infInut')
        self.xMotivo  = TagCaracter(nome='xMotivo' , codigo='DR08', tamanho=[1, 255]    , raiz='//retInutCTe/infInut')
        self.cUF      = TagInteiro(nome='cUF'      , codigo='DR09', tamanho=[2, 2, 2]   , raiz='//retInutCTe/infInut')
        self.ano      = TagCaracter(nome='ano'     , codigo='DR10', tamanho=[2, 2]      , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.CNPJ     = TagCaracter(nome='CNPJ'    , codigo='DR11', tamanho=[3, 14]     , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.mod      = TagInteiro(nome='mod'      , codigo='DR12', tamanho=[2, 2, 2]   , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.serie    = TagInteiro(nome='serie'    , codigo='DR13', tamanho=[1, 3]      , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.nCTIni   = TagInteiro(nome='nCTIni'   , codigo='DR14', tamanho=[1, 9]      , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.nCTFin   = TagInteiro(nome='nCTFin'   , codigo='DR15', tamanho=[1, 9]      , raiz='//retInutCTe/infInut', obrigatorio=False)
        self.dhRecbto = TagDataHora(nome='dhRecbto', codigo='DR16',                       raiz='//retInutCTe/infInut', obrigatorio=False)
        self.nProt    = TagInteiro(nome='nProt'    , codigo='DR17', tamanho=[15, 15, 15], raiz='//retInutCTe/infInut', obrigatorio=False)

    def get_xml(self):
        xml = XMLNFe.get_xml(self)

        if self.Id.xml:
            xml += self.Id.xml
        else:
            xml += '<infInut>'

        xml += self.tpAmb.xml
        xml += self.verAplic.xml
        xml += self.cStat.xml
        xml += self.xMotivo.xml
        xml += self.cUF.xml
        xml += self.ano.xml
        xml += self.CNPJ.xml
        xml += self.mod.xml
        xml += self.serie.xml
        xml += self.nCTIni.xml
        xml += self.nCTFin.xml
        xml += self.dhRecbto.xml
        xml += self.nProt.xml
        xml += '</infInut>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.Id.xml       = arquivo
            self.tpAmb.xml    = arquivo
            self.verAplic.xml = arquivo
            self.cStat.xml    = arquivo
            self.xMotivo.xml  = arquivo
            self.cUF.xml      = arquivo
            self.ano.xml      = arquivo
            self.CNPJ.xml     = arquivo
            self.mod.xml      = arquivo
            self.serie.xml    = arquivo
            self.nCTIni.xml   = arquivo
            self.nCTFin.xml   = arquivo
            self.dhRecbto.xml = arquivo
            self.nProt.xml    = arquivo

    xml = property(get_xml, set_xml)


class RetInutCTe(XMLNFe):
    def __init__(self):
        super(RetInutCTe, self).__init__()
        self.versao = TagDecimal(nome='retInutCTe', codigo='DR01', propriedade='versao', namespace=NAMESPACE_CTE, valor='1.04', raiz='/')
        self.infInut = InfInutRecebido()
        self.Signature = Signature()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'retInutCte_v1.04.xsd'

        self.chave = ''

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.infInut.xml

        if len(self.Signature.URI) and (self.Signature.URI.strip() != '#'):
            xml += self.Signature.xml

        xml += '</retInutCTe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.infInut.xml   = arquivo
            self.Signature.xml = self._le_noh('//retInutCTe/sig:Signature')

    xml = property(get_xml, set_xml)

    def monta_chave(self):
        chave = unicode(self.infInut.cUF.valor).zfill(2)
        #chave += self.infInut.ano.valor.zfill(2)
        chave += self.infInut.CNPJ.valor.zfill(14)
        chave += unicode(self.infInut.mod.valor).zfill(2)
        chave += unicode(self.infInut.serie.valor).zfill(3)
        chave += unicode(self.infInut.nNFIni.valor).zfill(9)
        chave += unicode(self.infInut.nNFFin.valor).zfill(9)

        self.chave = chave
        return chave


class ProcInutCTe(XMLNFe):
    def __init__(self):
        super(ProcInutCTe, self).__init__()
        #
        # Atenção --- a tag procInutCTe tem que começar com letra minúscula, para
        # poder validar no XSD.
        #
        self.versao = TagDecimal(nome='procInutCTe', propriedade='versao', namespace=NAMESPACE_CTE, valor='1.04', raiz='/')
        self.inutCTe = InutCTe()
        self.retInutCTe = RetInutCTe()
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'procInutCte_v1.04.xsd'

    def get_xml(self):
        xml = XMLNFe.get_xml(self)
        xml += ABERTURA
        xml += self.versao.xml
        xml += self.inutCTe.xml.replace(ABERTURA, '')
        xml += self.retInutCTe.xml.replace(ABERTURA, '')
        xml += '</procInutCTe>'
        return xml

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.inutCTe.xml    = arquivo
            self.retInutCTe.xml = arquivo

    xml = property(get_xml, set_xml)
