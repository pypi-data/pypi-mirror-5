# -*- coding: utf-8 -*-
#
# PySPED - Python libraries to deal with Brazil's SPED Project
#
# Copyright (C) 2010-2012
# Copyright (C) Aristides Caldeira <aristides.caldeira at tauga.com.br>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# PySPED - Bibliotecas Python para o
#          SPED - Sistema Público de Escrituração Digital
#
# Copyright (C) 2010-2012
# Copyright (C) Aristides Caldeira <aristides.caldeira arroba tauga.com.br>
#
# Este programa é um software livre: você pode redistribuir e/ou modificar
# este programa sob os termos da licença GNU Affero General Public License,
# publicada pela Free Software Foundation, em sua versão 3 ou, de acordo
# com sua opção, qualquer versão posterior.
#
# Este programa é distribuido na esperança de que venha a ser útil,
# porém SEM QUAISQUER GARANTIAS, nem mesmo a garantia implícita de
# COMERCIABILIDADE ou ADEQUAÇÃO A UMA FINALIDADE ESPECÍFICA. Veja a
# GNU Affero General Public License para mais detalhes.
#
# Você deve ter recebido uma cópia da GNU Affero General Public License
# juntamente com este programa. Caso esse não seja o caso, acesse:
# <http://www.gnu.org/licenses/>
#

from __future__ import division, print_function, unicode_literals

import os
from pysped.xml_sped import *
from pysped.nfe.leiaute import ESQUEMA_ATUAL_VERSAO_3 as ESQUEMA_ATUAL
from pysped.nfe.leiaute import ProtNFe_300
from pysped.nfe.leiaute import ProcEventoCancNFe_100, ProcEventoCCe_100
from pysped.nfe.leiaute import ProcEventoConfRecebimento_100, ProcEvento_100
from pysped.nfe.leiaute import conssitnfe_201

DIRNAME = os.path.dirname(__file__)


class ConsSitNFe(conssitnfe_201.ConsSitNFe):
    def __init__(self):
        super(ConsSitNFe, self).__init__()
        self.versao = TagDecimal(nome='consSitNFe', codigo='EP01', propriedade='versao', namespace=NAMESPACE_NFE, valor='3.10', raiz='/')
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'consSitNFe_v3.10.xsd'


class RetConsSitNFe(conssitnfe_201.RetConsSitNFe):
    def __init__(self):
        super(RetConsSitNFe, self).__init__()
        self.versao     = TagDecimal(nome='retConsSitNFe', codigo='ER01', propriedade='versao', namespace=NAMESPACE_NFE, valor='3.10', raiz='/')
        self.caminho_esquema = os.path.join(DIRNAME, 'schema', ESQUEMA_ATUAL + '/')
        self.arquivo_esquema = 'retConsSitNFe_v3.10.xsd'

    def set_xml(self, arquivo):
        if self._le_xml(arquivo):
            self.versao.xml  = arquivo
            self.tpAmb.xml     = arquivo
            self.verAplic.xml  = arquivo
            self.cStat.xml     = arquivo
            self.xMotivo.xml   = arquivo
            self.cUF.xml       = arquivo
            self.chNFe.xml     = arquivo

            if self._le_noh('//retConsSitNFe/protNFe') is not None:
                self.protNFe = ProtNFe_300()
                self.protNFe.xml = arquivo

            #if self._le_noh('//retConsSitNFe/retCancNFe') is not None:
                #self.retCancNFe = RetCancNFe_200()
                #self.retCancNFe.xml = arquivo

            if self._le_nohs('//retConsSitNFe/procEventoNFe') is not None:
                self.procEventoNFe = self.le_grupo('//retConsSitNFe/procEventoNFe')
