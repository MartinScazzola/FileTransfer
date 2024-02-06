# TP1 File Transfer

## Comandos

Para levantar el servidor

```py
python3 start_server.py -v -H 127.0.0.1 -p 65432 -pr {saw, sr} -s "path/server_files/"
```
Desde una nueva terminal para subir un archivo 

```py
python3 upload.py -v -H 127.0.0.1 -p 65432 -n filename -s "path/client_files/" -pr {saw, sr}
```

Desde una nueva terminal para descargar un archivo 

```py
python3 download.py -v -H 127.0.0.1 -p 65432 -n filename -d "path/client_files/" -pr {saw, sr}
```

## Para probar el packet loss usando Comcast

Pararse en el directorio '/go/pkg/mod/cache/download/github.com/tylertreat/comcast/@v/v1.0.1/github.com/tylertreat/comcast@v1.0.1' y ejecutar

```py
go run comcast.go --device=lo --packet-loss=10%
```

Para finalizar la perdida de paquetes ejecutar

```py
go run comcast.go --stop --device=lo
```



