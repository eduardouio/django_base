# Importaciones diferidas: este paquete se carga al configurar el logging,
# antes de que las apps de Django estén listas, por lo que no debe importar
# modelos al inicio. `from common import BaseModel` sigue funcionando.


def __getattr__(name):
    if name == 'BaseModel':
        from .BaseModel import BaseModel
        return BaseModel
    if name == 'EmailBackEndAuth':
        from .EmailBackEndAuth import EmailBackEndAuth
        return EmailBackEndAuth
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
