# Description
Generate random data in the shape of registered models based on OpenAPI spec.

A URI that points to an openapi spec is passed in the request. Models are generated and stored. Requests referencing the stored spec result in random data in the shape of the desired models returned.
# Registering an API Spec
Registration occurs by sending a POST request that contains a URI in the request body that points to the API spec. The response includes an id that can be used in future requests. See example below
POST https://rando-kt57zxudja-uk.a.run.app/spec/
# Generating Random data
Random data in the shape of models contained in a registered spec can be generated by sending a request referencing a registered spec.
GET https://rando-kt57zxudja-uk.a.run.app/spec/<spec_id>/. See example below
## Limiting Models
Random data can be limited by passing the desired models in query params. See example below
# Tokens
In order to limit use (and cost) each request requires a token supplied in the X-Request-Token header. Each token allows 10 spec registrations and 100 random data generations. Email me for a token (morgan at americancheese dot dev)
# Notes
Mostly untested, highly experimental. May become unavailable if costs get too high, or something breaks and I don’t have time to fix. Please email any issues you come across.
Supports OpenAPI v3
# Examples
## Register a new API spec
```
morgan@LAPTOP-O1G4SPR0:~$ curl \
--header "Content-Type: application/json"   \
--header "X-Request-Token:123" \
--request POST   \
--data '{"url":"https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore.yaml"}' 
https://rando-kt57zxudja-uk.a.run.app/spec/
{"spec_id":"deab595fb4554cb8986402f2a796fd60"}
```
## Generate random data for specific models in the spec
```
morgan@LAPTOP-O1G4SPR0:~$ curl -X GET \
--header "X-Request-Token:123" \ "https://rando-kt57zxudja-uk.a.run.app/specs/ee9098fe94434b3b8918a12ef2b4d6cb/?models=Error&models=Pet"
{"Error":{"code":856,"message":"wKraVZmWdaFplQZJTKLt"},"Pet":{"id":4764,"name":"avAjktqwaOGBJHfVIJqw","tag":"bAlwMxmSZWikCzFvptVe"}}
```
## Generate random data for all models in the spec
```
morgan@LAPTOP-O1G4SPR0:~$ curl -X GET \
--header "X-Request-Token:123" \
"https://rando-kt57zxudja-uk.a.run.app"
{"Error":{"code":6797,"message":"ZIUVPWUxPenWvXZDZFqc"},"Pet":{"id":4729,"name":"oHPuHQmJNIPBCimtcdzM","tag":"iThYlkviWRLsMnevwAta"},"Pets":[{"id":1317,"name":"ecCsRPiNmgzNboUGjMgx","tag":"BVMONPriVmjNzaIiFGGz"},{"id":3566,"name":"cjNUbPdbSASXFrqVThYK","tag":"QSzeVGhunJJoTlKSUXFr"},{"id":8011,"name":"VphNHwmTjGLSiLqToEQg","tag":"pLOaxfgjMJRzEhIMoRMD"},{"id":3759,"name":"ILWwHPUsEukQDCCSNfrn","tag":"sdbvCcdDUtwJixACFrGt"},{"id":8676,"name":"FWHmairxNiErJGJOWbgb","tag":"HLTSZzMpCKolaRSsyiJn"},{"id":7780,"name":"LmZJBzeLRIAfpMvCgkRR","tag":"MxFMyfmLXWUNjRNcEGjH"},{"id":2363,"name":"xPvmtJBKLlnltdEWLRsp","tag":"PNcJNiiALwJFKZPxAuDj"},{"id":5996,"name":"OLvchEjxQwDHgPGaSXry","tag":"cTsOftkWuHKhFJZhZrWr"},{"id":2706,"name":"cCRSTloGnbyCjhtqVGRD","tag":"pHhvTiQGrIBpNMRTpgtZ"},{"id":2328,"name":"vQXxtoxQidjjziKeYGvv","tag":"JaJCKlpuSKeDPQYPSIUF"},{"id":7515,"name":"iFWRNcDVGmecNMRwWjhQ","tag":"TjSCuIvcniGQHHWyUJqR"},{"id":6926,"name":"kiGaMruHowqDuITqEeps","tag":"xnoNKEZhdxeEbvRpqxis"},{"id":739,"name":"eiLBkRuTnpctOsJfQvEA","tag":"pZTItUtCljJOIbAxNAkj"},{"id":1842,"name":"hzBSPEprbryxKgOuIvyy","tag":"LlbkfQeaXamDpbBofxhT"},{"id":4107,"name":"cOEuLPyDFNVRozqcpnTk","tag":"YEEOrhvRvJbReCcRpWcn"},{"id":4586,"name":"wWDZWZnqJCnmFhoJmngE","tag":"JLydWnwfHwVwiOZylGEG"},{"id":725,"name":"kVobnYSguHewzcJItCtk","tag":"xebENHOFNXnOrnfvjmJn"},{"id":2757,"name":"cRBVlilMswqRzXDZnuuE","tag":"cfcEzCYNrrwqtunretnC"},{"id":6511,"name":"hkkcwMfCrUZAavOQRCsS","tag":"qnGPPxcHBuFwGhshFEfL"},{"id":2620,"name":"dSgrnBzCJVdjPxpftrXz","tag":"lDsoZacIBcddquOsPTyO"}
..
```
# Known Issues
Slow registration - Registration generates a model by reading in the content, writing out to the file system, then loading by importing as module, kinda slow.
Run on max_instance=1 Cloud Run, modules are cached to in-memory file system, which may exhaust all memory in the container, causing crash.
Does not work on really large specs, causes crash due to memory exhaustion
# Future Work
- Register webhook for periodic instances
- Generate N number of instances
- Ability to edit spec
- Endpoint to accept spec
- Support other types of spec
- Speed improvements
- Security improvements
- Support other output formats
- Register static values (instead of random)
