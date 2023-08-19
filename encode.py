import jwt

# Your claims (payload)
claims = {
    "sub": "1234567890",
    "name": "John Doe",
    "iat": 1516239022
}

# Load your private key
with open('private.pem', 'r') as f:
    private_key = f.read()

# Encode the JWT
encoded_jwt = jwt.encode(claims, private_key, algorithm='ES256')

print(encoded_jwt)