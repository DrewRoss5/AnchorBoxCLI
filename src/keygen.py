import sys
import os

from Crypto.PublicKey import RSA

def main():
    if len(sys.argv) != 2:
        print('Error: this script accepts exactly one argument for key path.')
        sys.exit(1)
    key_path = sys.argv[1]
    os.makedirs(key_path, exist_ok=True)
    with open(f'{key_path}/pub.pem', 'wb') as pub_f, open(f'{key_path}/prv.pem', 'wb') as prv_f:
        rsa_key = RSA.generate(4096)
        pub_f.write(rsa_key.public_key().export_key('PEM'))
        prv_f.write(rsa_key.export_key('PEM'))
    print('Keys generated successfully')

if __name__ == '__main__':
    main()
    sys.exit(1)