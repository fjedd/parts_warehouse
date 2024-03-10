# PartsWarehouse API


Technologies: `Python 3.12 Fastapi 0.110 MongoDB`
API used for parts management featuring CRUD operations on parts and categories

Logic requirements:
Parts:
- Ensure that a part cannot be assigned to a base category.

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
![image](https://github.com/fjedd/parts_warehouse/assets/74370972/b606830f-5d0f-441c-95d5-904a981c1f58)
