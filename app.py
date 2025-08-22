import streamlit as st
import mysql.connector
from datetime import datetime
import os

# Configuración de la página
st.set_page_config(
    page_title="Safety Walk - Formulario SST",
    page_icon="🦺",
    layout="wide"
)

# Credenciales de login
LOGIN_USER = "JMC_SST"
LOGIN_PASSWORD = "1019060017"

# Función de autenticación
def check_login():
    """Verificar si el usuario está logueado"""
    return st.session_state.get("logged_in", False)

def login_form():
    """Mostrar formulario de login"""
    st.title("🔐 Acceso al Sistema")
    st.markdown("### Safety Walk - Sistema SST")
    st.markdown("---")
    
    # Centrar el formulario de login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
            submit_button = st.form_submit_button("🚀 Ingresar", use_container_width=True)
            
            if submit_button:
                if username == LOGIN_USER and password == LOGIN_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("✅ Login exitoso!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    # Información adicional
    st.markdown("---")
    st.info("📞 **Soporte Técnico:** Contacte al administrador del sistema para acceso")

# Configuración de base de datos
@st.cache_resource
def init_connection():
    """Inicializar conexión a MySQL"""
    try:
        connection = mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=int(st.secrets["DB_PORT"]),
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
            charset="utf8mb4"
        )
        return connection
    except Exception as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

def guardar_formulario(datos):
    """Guardar formulario en MySQL"""
    connection = init_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO formulario (
            `1_1_Uso_correcto_EPP_dotacion`,
            `1_2_Cumple_normas_SST`,
            `1_3_Reporta_actos_inseguras`,
            `1_4_Certificado_equipos`,
            evaluador,
            area_evaluada,
            turno
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, datos)
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        st.error(f"Error guardando datos: {e}")
        return False

def logout():
    """Cerrar sesión"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

def main_app():
    """Aplicación principal del formulario"""
    # Header con logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🦺 Safety Walk - Formulario SST")
    with col2:
        st.write(f"👤 **Usuario:** {st.session_state.username}")
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            logout()
    
    st.markdown("---")

    # Información del evaluador
    st.header("📋 Información del Evaluador")
    col1, col2, col3 = st.columns(3)

    with col1:
        evaluador = st.text_input("👤 Nombre del Evaluador", placeholder="Ingrese su nombre")

    with col2:
        area_evaluada = st.text_input("🏢 Área Evaluada", placeholder="Ej: Almacén Principal")

    with col3:
        turno = st.selectbox("⏰ Turno", ["MAÑANA", "TARDE", "NOCHE"])

    st.markdown("---")

    # Formulario principal
    st.header("✅ Preguntas de Evaluación")

    # Pregunta 1.1
    st.subheader("1.1 Elementos de Protección Personal")
    st.write("**¿Los colaboradores directos y de aliados hace uso correcto de los elementos de protección personal y dotación requerida?**")
    respuesta_1_1 = st.radio(
        "Seleccione una opción:",
        ["SI", "NO", "N/A"],
        key="q1_1",
        horizontal=True
    )
    observaciones_1_1 = st.text_area("Observaciones (opcional):", key="obs_1_1", height=80)

    st.markdown("---")

    # Pregunta 1.2  
    st.subheader("1.2 Normas y Procedimientos SST")
    st.write("**¿Los colaboradores directos y de aliados cumple las normas, procedimientos y reglamentos de SST?**")
    respuesta_1_2 = st.radio(
        "Seleccione una opción:",
        ["SI", "NO", "N/A"],
        key="q1_2",
        horizontal=True
    )
    observaciones_1_2 = st.text_area("Observaciones (opcional):", key="obs_1_2", height=80)

    st.markdown("---")

    # Pregunta 1.3
    st.subheader("1.3 Reporte de Actos Inseguros")
    st.write("**¿El personal reporta Actos y condiciones inseguras cuando se presentan a: Coordinadores SST o a la Brigada de emergencias del Cedi?**")
    respuesta_1_3 = st.radio(
        "Seleccione una opción:",
        ["SI", "NO", "N/A"],
        key="q1_3",
        horizontal=True
    )
    observaciones_1_3 = st.text_area("Observaciones (opcional):", key="obs_1_3", height=80)

    st.markdown("---")

    # Pregunta 1.4
    st.subheader("1.4 Certificados de Equipos")
    st.write("**¿Los colaboradores directos y de aliados cuentan con el certificado vigente para realizar labores de manejo de equipos (Single/double pallet, montacargas y contrabalanceado) se valida que el personal porte el brazalete asignado?**")
    respuesta_1_4 = st.radio(
        "Seleccione una opción:",
        ["SI", "NO", "N/A"],
        key="q1_4",
        horizontal=True
    )
    observaciones_1_4 = st.text_area("Observaciones (opcional):", key="obs_1_4", height=80)

    st.markdown("---")

    # Botón de envío
    if st.button("💾 Guardar Evaluación", type="primary", use_container_width=True):
        # Validaciones
        if not evaluador:
            st.error("❌ Por favor ingrese el nombre del evaluador")
        elif not area_evaluada:
            st.error("❌ Por favor ingrese el área evaluada")
        else:
            # Preparar datos para guardar
            # Combinar respuesta + observaciones si existen
            datos_1_1 = respuesta_1_1 + (f" - {observaciones_1_1}" if observaciones_1_1 else "")
            datos_1_2 = respuesta_1_2 + (f" - {observaciones_1_2}" if observaciones_1_2 else "")
            datos_1_3 = respuesta_1_3 + (f" - {observaciones_1_3}" if observaciones_1_3 else "")
            datos_1_4 = respuesta_1_4 + (f" - {observaciones_1_4}" if observaciones_1_4 else "")
            
            datos = (
                datos_1_1,
                datos_1_2, 
                datos_1_3,
                datos_1_4,
                evaluador,
                area_evaluada,
                turno
            )
            
            # Guardar en base de datos
            if guardar_formulario(datos):
                st.success("✅ Evaluación guardada exitosamente!")
                st.balloons()
                
                # Mostrar resumen
                with st.expander("📊 Resumen de la Evaluación"):
                    st.write(f"**Evaluador:** {evaluador}")
                    st.write(f"**Área:** {area_evaluada}")
                    st.write(f"**Turno:** {turno}")
                    st.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Usuario del Sistema:** {st.session_state.username}")
                    st.write("**Respuestas:**")
                    st.write(f"- EPP: {respuesta_1_1}")
                    st.write(f"- Normas SST: {respuesta_1_2}")
                    st.write(f"- Reportes: {respuesta_1_3}")
                    st.write(f"- Certificados: {respuesta_1_4}")
            else:
                st.error("❌ Error al guardar la evaluación. Intente nuevamente.")

    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Información")
        st.write("**Safety Walk - Sistema SST**")
        st.write("Formulario para evaluación de seguridad y salud en el trabajo")
        st.write(f"**Usuario:** {st.session_state.username}")
        
        st.markdown("---")
        st.subheader("📞 Contacto")
        st.write("Coordinación SST")
        st.write("Brigada de Emergencias")
        
        # Estadísticas básicas (opcional)
        st.markdown("---")
        st.subheader("📈 Estado de la Aplicación")
        if init_connection():
            st.success("✅ Conectado a la base de datos")
        else:
            st.error("❌ Error de conexión")

# Lógica principal de la aplicación
if __name__ == "__main__":
    # Verificar si está logueado
    if not check_login():
        login_form()
    else:
        main_app()
