import sys

sys.path.insert(0, ".")
from fastapi_app.core.security import verify_token

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzY3ODI2NTU4fQ.d7TTxogi3CorAgaoWBE4h2N1APGOJ7fzwehtvqAgunI"
result = verify_token(token)
print("Result:", result)
if result:
    print("Payload:", result)
else:
    print("Token invalid")
