#coding: utf-8
from collections import OrderedDict


class Dicionario(OrderedDict):
    """
    Dicionário especializado que permite acesso de chaves como propriedades.
    Adicionalmente, se uma chave já foi atribuída, transforma o valor em uma
    lista e acumula os valores.
    """
    def __getattr__(self, nome):
        if nome in self:
            return self[nome]
        raise AttributeError("%r sem atributo %r" %
                             (type(self).__name__, nome))
