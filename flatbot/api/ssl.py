import os
import ssl
import base64
from cryptography import fernet


def ssl_context():
    # Set up SSL for HTTPS.
    cert_path = os.path.join(SSL_PATH, 'cert.pem')
    key_path = os.path.join(SSL_PATH, 'private.pem')
    dh_path = os.path.join(SSL_PATH, 'dhparam.pem')

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(cert_path, key_path)

    cipher_suite = ('ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:'
                    'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:'
                    'ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:'
                    'DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384')
    ssl_context.set_ciphers(cipher_suite)

    ssl_context.load_dh_params(dh_path)
    ssl_context.set_ecdh_curve('prime256v1')

    ssl_context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    ssl_context.options |= ssl.OP_SINGLE_DH_USE | ssl.OP_SINGLE_ECDH_USE

    return ssl_context

