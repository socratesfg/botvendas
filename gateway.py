import aiohttp
import ssl
import asyncio

EPAGUE_API_KEY = "epague_live_f7c649008aed017b5e3de6222d5853b7cde51f6a865f89b375418d8da217784d"
EPAGUE_URL = "https://epague.net/api/pix/create"

async def gerar_pix_cobranca(valor: float, descricao: str):
    """Gera uma cobrança Pix real usando a API da ePague."""
    
    headers = {
        "x-api-key": EPAGUE_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "amount": valor,
        "external_id": f"pedido_{int(valor * 100)}_{int(asyncio.get_event_loop().time())}"
    }

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(EPAGUE_URL, json=payload, headers=headers, ssl=ssl_context) as response:
                
                content_type = response.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    texto_resposta = await response.text()
                    print(f"Erro ePague (HTML retornado): {texto_resposta}")
                    return {"success": False, "error": "Servidor retornou HTML."}

                res_data = await response.json()

                if res_data.get("success") is True and "transaction" in res_data:
                    trx = res_data["transaction"]
                    txid = str(trx.get("id") or "epague_tx")
                    pix_copia_cola = trx.get("pix_copia_cola")
                    qr_code_base64 = trx.get("qr_code_base64")

                    return {
                        "success": True,
                        "txid": txid,
                        "pix_copia_cola": pix_copia_cola,
                        "qr_code_base64": qr_code_base64
                    }
                else:
                    print("Erro retornado pelo ePague:", res_data)
                    return {"success": False, "error": res_data}

    except Exception as e:
        print("Exceção na comunicação com o ePague:", e)
        return {"success": False, "error": str(e)}