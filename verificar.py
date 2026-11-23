"""Prueba las respuestas del servidor DNS de esta práctica."""

from dnslib import DNSRecord, QTYPE, RCODE

SERVIDOR = "127.0.0.1"
PUERTO = 5300
CASOS = (
    ("servidor.lab.test.", "A", "NOERROR", "192.0.2.10"),
    ("10.2.0.192.in-addr.arpa.", "PTR", "NOERROR", "servidor.lab.test."),
    ("inexistente.lab.test.", "A", "NXDOMAIN", None),
)


def verificar():
    print(f"Servidor consultado: {SERVIDOR}:{PUERTO} (UDP)")
    aprobadas = 0

    for nombre, tipo, estado_esperado, valor_esperado in CASOS:
        consulta = DNSRecord.question(nombre, tipo)
        consulta.header.rd = 0
        respuesta = DNSRecord.parse(consulta.send(SERVIDOR, PUERTO, timeout=2))
        estado = RCODE[respuesta.header.rcode]
        registros = [
            (str(registro.rname), QTYPE[registro.rtype], str(registro.rdata))
            for registro in respuesta.rr
        ]
        esperados = [] if valor_esperado is None else [(nombre, tipo, valor_esperado)]
        coincide = (
            respuesta.header.id == consulta.header.id
            and respuesta.header.qr == 1
            and estado == estado_esperado
            and registros == esperados
        )
        aprobadas += int(coincide)
        resultado = "OK" if coincide else "ERROR"
        detalle = ", ".join(valor for _, _, valor in registros) or "sin registros"
        print(f"[{resultado}] {tipo:<3} {nombre:<26} {estado:<8} {detalle}")

    print(f"Pruebas correctas: {aprobadas}/{len(CASOS)}")
    return 0 if aprobadas == len(CASOS) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(verificar())
    except OSError as error:
        raise SystemExit(
            f"Consulta fallida: {error}. Verifica que el servidor local esté iniciado."
        ) from error
