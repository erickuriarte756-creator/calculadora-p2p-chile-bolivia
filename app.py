import streamlit as st
import requests
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Calculadora P2P: Chile ↔ Bolivia",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Calculadora P2P: Chile ↔️ Bolivia")
st.write("Datos en tiempo real desde **CriptoYa** (Binance P2P)")

def obtener_datos_completos():
    """Obtiene los precios actuales según la nueva lógica solicitada"""
    resultados = {"clp": None, "bob": None, "time": None}
    
    try:
        volumen = 100.0   # Volumen de referencia en USDT

        # 1. CHILE → Vender USDT y recibir CLP  (usamos BID)
        url_clp = f"https://criptoya.com/api/binancep2p/USDT/CLP/{volumen}"
        r_clp = requests.get(url_clp, timeout=12)
        r_clp.raise_for_status()
        data_clp = r_clp.json()
        
        resultados["clp"] = float(data_clp["bid"])   # ← Precio que RECIBES en CLP por 1 USDT al vender

        # 2. BOLIVIA → Comprar USDT pagando con BOB  (usamos ASK)
        url_bob = f"https://criptoya.com/api/binancep2p/USDT/BOB/{volumen}"
        r_bob = requests.get(url_bob, timeout=12)
        r_bob.raise_for_status()
        data_bob = r_bob.json()
        
        resultados["bob"] = float(data_bob["ask"])   # ← Precio que PAGAS en BOB por 1 USDT al comprar
        resultados["time"] = data_bob.get("time")

        return resultados

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error de conexión con la API: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        st.error(f"❌ Error al procesar los datos: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error inesperado: {e}")
        return None


# Cargar datos
datos = obtener_datos_completos()

if datos and datos["clp"] and datos["bob"]:
    p_clp = datos["clp"]   # Precio BID CLP (venta de USDT en Chile)
    p_bob = datos["bob"]   # Precio ASK BOB (compra de USDT en Bolivia)

    # Mostrar precios actuales
    col1, col2 = st.columns(2)
    col1.metric(
        label="🇨🇱 Chile - Vender USDT",
        value=f"{p_clp:,.2f} CLP",
        help="Precio que recibes en CLP por vender 1 USDT"
    )
    col2.metric(
        label="🇧🇴 Bolivia - Comprar USDT",
        value=f"{p_bob:,.2f} BOB",
        help="Precio que pagas en BOB por comprar 1 USDT"
    )

    st.divider()

    # Entrada del usuario (siempre en CLP)
    monto_clp = st.number_input(
        "Cantidad a enviar desde Chile (CLP):",
        min_value=10_000,
        value=500_000,
        step=10_000,
        format="%d"
    )

    # Cálculo: CLP → USDT → BOB
    usdt_netos = monto_clp / p_clp          # Vendes CLP → obtienes USDT
    total_bob = usdt_netos * p_bob          # Compras BOB con esos USDT

    # Resultado principal
    st.success(f"### Recibirás en Bolivia: **{total_bob:,.2f} BOB**")

    # Detalles del cálculo
    with st.expander("Ver detalle del cálculo"):
        st.write(f"1. Vendes **{monto_clp:,.0f} CLP** en Chile y recibes **{usdt_netos:,.4f} USDT**")
        st.write(f"2. Con esos USDT compras en Bolivia pagando **{p_bob:,.2f} BOB** por USDT")
        st.write(f"**Tipo de cambio efectivo:** 1 BOB ≈ **{(p_clp / p_bob):,.2f} CLP**")

    if datos["time"]:
        ultimo_update = datetime.fromtimestamp(datos["time"]).strftime("%H:%M:%S")
        st.caption(f"Última actualización: {ultimo_update}")

else:
    st.warning("No se pudo obtener la información automática. Verifica tu internet.")

# Botón de actualizar
if st.button("🔄 Actualizar Precios Ahora"):
    st.rerun()

st.caption("Nota: Los precios corresponden al mejor anuncio disponible en Binance P2P según CriptoYa. "
           "No incluye comisiones de transferencia, retiro o spreads adicionales.")

st.markdown("---")
st.markdown("Calculadora P2P Chile → Bolivia | Venta en CLP → Compra en BOB")