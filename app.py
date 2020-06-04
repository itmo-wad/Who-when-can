from main import app


if __name__ == '__main__':
    context = ('ssl/server.crt', 'ssl/server.key')#certificate and key files
    app.run(host="0.0.0.0",port="443", ssl_context=context)
