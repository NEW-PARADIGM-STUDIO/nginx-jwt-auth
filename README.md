# nginx-jwt-auth
This project implements a simple JWT validation endpoint meant to be used with NGINX's [subrequest authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-subrequest-authentication/), and specifically work well with the Kubernetes [NGINX Ingress Controller](https://github.com/kubernetes/ingress-nginx) external auth annotations.

It validates a JWT token passed in the `Authorization` header against a configured public key, and further validates that the JWT contains appropriate claims.

## Based on

- https://github.com/carlpett/nginx-subrequest-auth-jwt
- https://github.com/ovidiubuligan/nginx-subrequest-auth-jwt
- https://github.com/FactFiber/devspace-nginx-auth-jwt


# Configuration

Using environemnt variables:

1. JWKS_PATH: Path to a file containing an EC Public Key. This allows you to retrieve JWKS from a local file instead of a remote URL. For example: JWKS_PATH=/path/to/ecPublicKey.pem
2. JWKS_URL: URL pointing to your JWKS. For example: JWKS_URL=https://example.com/.well-known/jwks.json
3. PORT: The port on which the server will run. For example: PORT=8080

If both JWKS_PATH and JWKS_URL are provided, the system will prioritize JWKS_PATH over JWKS_URL.

### Query string
In query string mode, the allowed claims are passed via query string parameters to the /validate endpoint. For example, with `/validate?claims_group=developers&claims_group=administrators&claims_location=hq`, the token claims must **both** have a `group` claim of **either** `developers` or `administrators`, **and** a `location` claim of `hq`.

Each claim must be prefixed with `claims_`. Giving the same claim multiple time results in any value being accepted.
Claims prefixed with `claims_regexp_` can have regexes, their compiled versions are cached for performance reasons.

In this mode, in contrast to static mode, only a single set of acceptable claims can be passed at a time (but different NGINX server blocks can pass different sets).

If no claims are passed in this mode, the request will be denied.

# NGINX Ingress Controller integration
To use with the NGINX Ingress Controller, first create a deployment and a service for this endpoint. See the [kubernetes/](kubernetes/) directory for example manifests. Then on the ingress object you wish to authenticate, add this annotation for a server in static claims source mode:

```yaml
nginx.ingress.kubernetes.io/auth-url: http://token-validator.default.svc.cluster.local/validate
```

Or, in query string mode:

```yaml
nginx.ingress.kubernetes.io/auth-url: http://token-validator.default.svc.cluster.local/validate?claims_group=developers
```

Change the url to match the name of the service and namespace you chose when deploying. All requests will now have their JWTs validated before getting passed to the upstream service.

# Metrics
This endpoint exposes [Prometheus](https://prometheus.io) metrics on `/metrics`:

- `http_requests_total{status="<status>"}` number of requests handled, by status code (counter)
- `nginx_subrequest_auth_jwt_token_validation_time_seconds` number of seconds spent validating tokens (histogram)

# Response headers

To include fields from claims in response headers, use the `responseHeaders` configuration section. It should consist of a map
of response header to claim name. Headers will be included with
base64 encoding of the claim. If the actual claim is a string,
this will be directly encoded. If the claim is an array of strings,
this will first be json encoded, then base64 encoded.

Response headers can also be configured via the query. Use a query
parameter of the form `headers_foo=bar` to encode claims "bar"
in response header "foo".

# generate a private key for a curve
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem

# generate corresponding public key
openssl ec -in private-key.pem -pubout -out public-key.pem

# fetch matchmaker
http.request(`http://matchmaker`, { 'Authorization': 'Bearer ' + jwt }).on('response', (response) => response.pipe(res))