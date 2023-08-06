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

#
# Versão 1.00, usada até abril/2010
#
from pysped.nfe.leiaute import ESQUEMA_ATUAL_VERSAO_1 as ESQUEMA_ATUAL

#
# Envelopes SOAP
#
from pysped.nfe.leiaute.soap_100 import SOAPEnvio as SOAPEnvio_110
from pysped.nfe.leiaute.soap_100 import SOAPRetorno as SOAPRetorno_110

#
# Emissão de NF-e
#
from pysped.nfe.leiaute.nfe_110 import NFe as NFe_110
from pysped.nfe.leiaute.nfe_110 import NFRef as NFRef_110
from pysped.nfe.leiaute.nfe_110 import Det as Det_110
from pysped.nfe.leiaute.nfe_110 import DI as DI_110
from pysped.nfe.leiaute.nfe_110 import Adi as Adi_110
from pysped.nfe.leiaute.nfe_110 import Med as Med_110
from pysped.nfe.leiaute.nfe_110 import Arma as Arma_110
from pysped.nfe.leiaute.nfe_110 import Reboque as Reboque_110
from pysped.nfe.leiaute.nfe_110 import Vol as Vol_110
from pysped.nfe.leiaute.nfe_110 import Lacres as Lacres_110
from pysped.nfe.leiaute.nfe_110 import Dup as Dup_110
from pysped.nfe.leiaute.nfe_110 import ObsCont as ObsCont_110
from pysped.nfe.leiaute.nfe_110 import ObsFisco as ObsFisco_110
from pysped.nfe.leiaute.nfe_110 import ProcRef as ProcRef_110

#
# Envio de lote de NF-e
#
from pysped.nfe.leiaute.envinfe_110 import EnviNFe as EnviNFe_110
from pysped.nfe.leiaute.envinfe_110 import RetEnviNFe as RetEnviNFe_110

#
# Consulta do recibo do lote de NF-e
#
from pysped.nfe.leiaute.consrecinfe_110 import ConsReciNFe as ConsReciNFe_110
from pysped.nfe.leiaute.consrecinfe_110 import RetConsReciNFe as RetConsReciNFe_110
from pysped.nfe.leiaute.consrecinfe_110 import ProtNFe as ProtNFe_110
from pysped.nfe.leiaute.consrecinfe_110 import ProcNFe as ProcNFe_110

#
# Cancelamento de NF-e
#
from pysped.nfe.leiaute.cancnfe_107 import CancNFe as CancNFe_107
from pysped.nfe.leiaute.cancnfe_107 import RetCancNFe as RetCancNFe_107
from pysped.nfe.leiaute.cancnfe_107 import ProcCancNFe as ProcCancNFe_107

#
# Inutilização de NF-e
#
from pysped.nfe.leiaute.inutnfe_107 import InutNFe as InutNFe_107
from pysped.nfe.leiaute.inutnfe_107 import RetInutNFe as RetInutNFe_107
from pysped.nfe.leiaute.inutnfe_107 import ProcInutNFe as ProcInutNFe_107

#
# Consulta a situação de NF-e
#
from pysped.nfe.leiaute.conssitnfe_107 import ConsSitNFe as ConsSitNFe_107
from pysped.nfe.leiaute.conssitnfe_107 import RetConsSitNFe as RetConsSitNFe_107

#
# Consulta a situação do serviço
#
from pysped.nfe.leiaute.consstatserv_107 import ConsStatServ as ConsStatServ_107
from pysped.nfe.leiaute.consstatserv_107 import RetConsStatServ as RetConsStatServ_107

#
# Consulta cadastro
#
from pysped.nfe.leiaute.conscad_101 import ConsCad as ConsCad_101
from pysped.nfe.leiaute.conscad_101 import RetConsCad as RetConsCad_101

# Pyflakes

Adi_110
Arma_110
CancNFe_107
ConsCad_101
ConsReciNFe_110
ConsSitNFe_107
ConsStatServ_107
DI_110
Det_110
Dup_110
ESQUEMA_ATUAL
EnviNFe_110
InutNFe_107
Lacres_110
Med_110
NFRef_110
NFe_110
ObsCont_110
ObsFisco_110
ProcCancNFe_107
ProcInutNFe_107
ProcNFe_110
ProcRef_110
ProtNFe_110
Reboque_110
RetCancNFe_107
RetConsCad_101
RetConsReciNFe_110
RetConsSitNFe_107
RetConsStatServ_107
RetEnviNFe_110
RetInutNFe_107
SOAPEnvio_110
SOAPRetorno_110
Vol_110
