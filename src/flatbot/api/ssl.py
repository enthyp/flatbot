import os
import ssl


def ssl_context(config):
    # Set up SSL for HTTPS.
    ssl_path = config.ssl_path

    cert_path, key_path, dh_path = map(
        lambda file: os.path.join(ssl_path, file),
        ['cert.pem', 'private.pem', 'dhparam.pem']
    )

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

