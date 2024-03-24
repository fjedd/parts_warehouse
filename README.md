# PartsWarehouse API


Technologies: `Python 3.12 Fastapi 0.110 MongoDB`
API used for parts management featuring CRUD operations on parts and categories with JWT authentication

**API logic:**

Parts:
- Ensure that a part cannot be assigned to a base category
- Category needs to exist

Categories:
- Ensure that a category cannot be modified if there are parts assigned to it.
- Ensure that a parent category cannot be removed if it has child categories with parts assigned.

### Preparing project

- Copy `.env.dev` to `.env` (and change configuration if necessary)
- Execute `docker-compose build`
- Execute `docker-compose up -d`

API is available at http://localhost:8080

### Testing
To run tests execute `docker-compose exec app pytest`


Manual testing can be done using Swagger http://localhost:8080/docs# or with Postman/curl

Available endpoints:

![image](https://github.com/fjedd/parts_warehouse/assets/74370972/9eba3647-9bd6-4437-af5f-2e1a90561a51)

*Note that endpoints with* 🔓 *require authorization with `Authorization` header*

![image](https://github.com/fjedd/parts_warehouse/assets/74370972/66468339-8d9a-406b-bf6a-0f37405b07db)

*You can create new user and generate JWT token using `/auth` endpoints*


## Example usage

1. Create new user
```
curl -X 'POST' \
  'http://localhost:8080/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "test",
  "email": "test@test.com",
  "password": "test"
}'
```

2. Generate token
```
curl -X 'POST' \
  'http://localhost:8080/auth/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=test&password=test'
```
3. Manage CRUD operations using available endpoints and suitable methods (look at scheme) e.g.:
Create base category,
```
curl -X 'POST' \
  'http://localhost:8080/categories/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {YOUR TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "test",
}'
```
subcategory,
```
curl -X 'POST' \
  'http://localhost:8080/categories/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {YOUR TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "subtest",
  "parent_name": "test"
}'
```
and part
```
curl -X 'POST' \
  'http://localhost:8080/parts/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {YOUR TOKEN}' \
  -H 'Content-Type: application/json' \
  -d '{
  "serial_number": "string",
  "name": "string",
  "description": "string",
  "category": "subtest",
  "quantity": 0,
  "price": 0,
  "location": {
    "room": "string",
    "bookcase": "string",
    "shelf": "string",
    "cubicle": "string",
    "column": "string",
    "row": "string"
  }
}'
```
update part
```
curl -X 'PUT' \
  'http://localhost:8080/parts/{CREATED PART ID}' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {YOUR TOKEN}}' \
  -H 'Content-Type: application/json' \
  -d '{
  "price": 20,
  "location": {
    "room": "new"
  }
}'
```
etc
