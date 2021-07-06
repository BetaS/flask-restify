# flask-restify
Flask + Swagger UI helper for restful api server

## Setup

1. Install via pip (`pip install flask-restify`)
2. or via git (`git clone "https://github.com/BetaS/flask-restify"`)
3. Check availability in your project like below
```python
from flask_restify.api import BaseAPI


class API(BaseAPI):
    pass


api = API("My First Restful API", "Lorem ipsum dolor sit amet, consectetur adipiscing elit..", "1.0.0")


if __name__ == '__main__':
    server = api.init_server(DevelopmentConfig)
    server.run("0.0.0.0", 5000, use_reloader=False)
```


# Contact
- Minsu (Eric) Kim
- Linked In: https://www.linkedin.com/in/k09089/
- E-MAIL: thou1999@gmail.com