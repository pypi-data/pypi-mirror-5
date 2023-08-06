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

from os.path import abspath, dirname
from pysped.nfe import ProcessadorNFe


FILE_DIR = abspath(dirname(__file__))


if __name__ == '__main__':
    p = ProcessadorNFe()
    p.versao              = '2.00'
    p.estado              = 'SP'
    #p.certificado.arquivo = 'certificado.pfx'
    #p.certificado.senha   = 'senha'

    #
    # arquivo 'certificado_caminho.txt' deve conter o caminho para o 'certificado.pfx'
    #
    p.certificado.arquivo = open(FILE_DIR+'/certificado_caminho.txt').read().strip()

    #
    # arquivo 'certificado_senha.txt' deve conter a senha para o 'certificado.pfx'
    #
    p.certificado.senha   = open(FILE_DIR+'/certificado_senha.txt').read().strip()

    p.salva_arquivos      = True
    p.contingencia_SCAN   = False
    p.caminho = ''

    #
    # O retorno de cada webservice é um objeto
    # com as seguintes propriedades
    #  .webservice - o webservice que foi consultado
    #  .envio - o objeto da classe XMLNFE enviado
    #  .envio.original - o texto do xml (envelope SOAP) enviado ao webservice
    #  .resposta - o objeto da classe XMLNFE retornado
    #  .resposta.version - version da HTTPResponse
    #  .resposta.status - status da HTTPResponse
    #  .resposta.reason - reason da HTTPResponse
    #  .resposta.msg - msg da HTTPResponse
    #  .resposta.original - o texto do xml (SOAP) recebido do webservice
    #
    processo = p.desconhecer_operacao_evento(
        cnpj='34274233006488', # CNPJ do destinatário/gerador do evento
        chave_nfe='35100411111111111111551010000000271123456789',
        )

    print(processo)
    print()
    print(processo.envio.xml)
    print()
    print(processo.envio.original)
    print()
    print(processo.resposta.xml)
    print()
    print(processo.resposta.original)
    print()
    print(processo.resposta.reason)

    #
    # A resposta dos eventos contém ainda dois dicionários, cujas chaves são as
    # são as chaves das NF-es enviadas nos evento;
    #    . dic_retEvento - dicionário com os protocolos de cada evento
    #    . dic_procEvento - dicionário com os processos (evento + protocolo) de cada
    # evento
    #
    print()
    print(processo.resposta.dic_retEvento)
    print()
    print(processo.resposta.dic_procEvento)
