import pkcs11
from pkcs11 import KeyType, ObjectClass
from pkcs11.exceptions import NoSuchKey

# Ruta al módulo PKCS#11 de SoftHSM2 (ajusta la ruta según donde esté instalado)
PKCS11_LIB_PATH = r"C:\SoftHSM2\lib\softhsm2.dll"  # Verifica la ruta en Windows

# Inicializa la librería PKCS#11
lib = pkcs11.lib(PKCS11_LIB_PATH)

def get_key_from_token(key_label, user_pin="1234"):
    """
    Abre el token, se autentica con el PIN de usuario y busca una clave (secret key)
    con el label dado.
    Devuelve la clave en formato hexadecimal o None si no se encuentra.
    """
    slots = lib.get_slots(token_present=True)
    if not slots:
        raise Exception("No hay tokens disponibles en SoftHSM")
    slot = slots[0]
    with slot.open(user_pin=user_pin) as session:
        try:
            key = session.get_key(object_class=ObjectClass.SECRET_KEY, label=key_label)
            key_value = key[0].get_value()
            return key_value.hex().upper()
        except NoSuchKey:
            return None


