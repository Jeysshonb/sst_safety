import streamlit as st
import mysql.connector
from datetime import datetime
import pandas as pd
from io import BytesIO
import os

# Configuración de la página
st.set_page_config(
    page_title="Safety Walk - Sistema SST",
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
            port=int(st.secrets.get("DB_PORT", 3306)),
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
        record_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return record_id
        
    except Exception as e:
        st.error(f"Error guardando datos: {e}")
        return False

def buscar_por_id(record_id):
    """Buscar registro por ID"""
    connection = init_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM formulario WHERE id = %s"
        cursor.execute(query, (record_id,))
        result = cursor.fetchone()
        
        if result:
            columns = [desc[0] for desc in cursor.description]
            record = dict(zip(columns, result))
            cursor.close()
            connection.close()
            return record
        else:
            cursor.close()
            connection.close()
            return None
            
    except Exception as e:
        st.error(f"Error buscando registro: {e}")
        return None

def actualizar_registro(record_id, datos):
    """Actualizar registro existente"""
    connection = init_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        update_query = """
        UPDATE formulario SET
            `1_1_Uso_correcto_EPP_dotacion` = %s,
            `1_2_Cumple_normas_SST` = %s,
            `1_3_Reporta_actos_inseguras` = %s,
            `1_4_Certificado_equipos` = %s,
            evaluador = %s,
            area_evaluada = %s,
            turno = %s
        WHERE id = %s
        """
        
        cursor.execute(update_query, datos + (record_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        st.error(f"Error actualizando registro: {e}")
        return False

def obtener_todos_registros():
    """Obtener todos los registros para exportar"""
    connection = init_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM formulario ORDER BY fecha_registro DESC"
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        connection.close()
        
        if results:
            df = pd.DataFrame(results, columns=columns)
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error obteniendo registros: {e}")
        return None

def to_excel(df):
    """Convertir DataFrame a Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Safety_Walk_Registros')
    return output.getvalue()

def logout():
    """Cerrar sesión"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()

def formulario_tab():
    """Tab del formulario principal"""
    st.header("📝 Nuevo Formulario")
    
    # Información del evaluador
    st.subheader("📋 Información del Evaluador")
    col1, col2, col3 = st.columns(3)

    with col1:
        evaluador = st.text_input("👤 Nombre del Evaluador", placeholder="Ingrese su nombre")

    with col2:
        area_evaluada = st.text_input("🏢 Área Evaluada", placeholder="Ej: Almacén Principal")

    with col3:
        turno = st.selectbox("⏰ Turno", ["MAÑANA", "TARDE", "NOCHE"])

    st.markdown("---")

    # Formulario principal
    st.subheader("✅ Preguntas de Evaluación")

    # Pregunta 1.1
    st.write("**1.1 ¿Los colaboradores directos y de aliados hace uso correcto de los elementos de protección personal y dotación requerida?**")
    respuesta_1_1 = st.radio("Seleccione una opción:", ["SI", "NO", "N/A"], key="q1_1", horizontal=True)
    observaciones_1_1 = st.text_area("Observaciones (opcional):", key="obs_1_1", height=60)

    st.markdown("---")

    # Pregunta 1.2  
    st.write("**1.2 ¿Los colaboradores directos y de aliados cumple las normas, procedimientos y reglamentos de SST?**")
    respuesta_1_2 = st.radio("Seleccione una opción:", ["SI", "NO", "N/A"], key="q1_2", horizontal=True)
    observaciones_1_2 = st.text_area("Observaciones (opcional):", key="obs_1_2", height=60)

    st.markdown("---")

    # Pregunta 1.3
    st.write("**1.3 ¿El personal reporta Actos y condiciones inseguras cuando se presentan a: Coordinadores SST o a la Brigada de emergencias del Cedi?**")
    respuesta_1_3 = st.radio("Seleccione una opción:", ["SI", "NO", "N/A"], key="q1_3", horizontal=True)
    observaciones_1_3 = st.text_area("Observaciones (opcional):", key="obs_1_3", height=60)

    st.markdown("---")

    # Pregunta 1.4
    st.write("**1.4 ¿Los colaboradores directos y de aliados cuentan con el certificado vigente para realizar labores de manejo de equipos (Single/double pallet, montacargas y contrabalanceado) se valida que el personal porte el brazalete asignado?**")
    respuesta_1_4 = st.radio("Seleccione una opción:", ["SI", "NO", "N/A"], key="q1_4", horizontal=True)
    observaciones_1_4 = st.text_area("Observaciones (opcional):", key="obs_1_4", height=60)

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
            datos_1_1 = respuesta_1_1 + (f" - {observaciones_1_1}" if observaciones_1_1 else "")
            datos_1_2 = respuesta_1_2 + (f" - {observaciones_1_2}" if observaciones_1_2 else "")
            datos_1_3 = respuesta_1_3 + (f" - {observaciones_1_3}" if observaciones_1_3 else "")
            datos_1_4 = respuesta_1_4 + (f" - {observaciones_1_4}" if observaciones_1_4 else "")
            
            datos = (datos_1_1, datos_1_2, datos_1_3, datos_1_4, evaluador, area_evaluada, turno)
            
            # Guardar en base de datos
            record_id = guardar_formulario(datos)
            if record_id:
                st.success(f"✅ Evaluación guardada exitosamente! ID: {record_id}")
                st.balloons()
                
                # Mostrar resumen
                with st.expander("📊 Resumen de la Evaluación"):
                    st.write(f"**ID:** {record_id}")
                    st.write(f"**Evaluador:** {evaluador}")
                    st.write(f"**Área:** {area_evaluada}")
                    st.write(f"**Turno:** {turno}")
                    st.write(f"**Usuario del Sistema:** {st.session_state.username}")
                    st.write("**Respuestas:** " + f"EPP: {respuesta_1_1}, SST: {respuesta_1_2}, Reportes: {respuesta_1_3}, Certificados: {respuesta_1_4}")
            else:
                st.error("❌ Error al guardar la evaluación. Intente nuevamente.")

def buscar_tab():
    """Tab para buscar y editar registros"""
    st.header("🔍 Buscar y Editar Registros")
    
    # Buscar por ID
    col1, col2 = st.columns([2, 1])
    with col1:
        search_id = st.number_input("🔢 Ingrese el ID del registro:", min_value=1, step=1, value=None)
    with col2:
        search_button = st.button("🔍 Buscar", type="primary")
    
    if search_button and search_id:
        record = buscar_por_id(search_id)
        
        if record:
            st.success(f"✅ Registro ID {search_id} encontrado!")
            st.markdown("---")
            
            # Mostrar información del registro
            st.subheader("📋 Información del Registro")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.write(f"**ID:** {record['id']}")
            with col2:
                st.write(f"**Fecha:** {record['fecha_registro']}")
            with col3:
                st.write(f"**Evaluador:** {record['evaluador']}")
            with col4:
                st.write(f"**Área:** {record['area_evaluada']}")
            
            st.markdown("---")
            
            # Formulario de edición
            st.subheader("✏️ Editar Registro")
            
            with st.form(f"edit_form_{search_id}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_evaluador = st.text_input("👤 Evaluador", value=record['evaluador'])
                with col2:
                    new_area = st.text_input("🏢 Área", value=record['area_evaluada'])
                with col3:
                    new_turno = st.selectbox("⏰ Turno", ["MAÑANA", "TARDE", "NOCHE"], 
                                           index=["MAÑANA", "TARDE", "NOCHE"].index(record['turno']) if record['turno'] in ["MAÑANA", "TARDE", "NOCHE"] else 0)
                
                st.markdown("**Respuestas actuales:**")
                
                # Extraer respuestas actuales (quitar observaciones para edición)
                current_1_1 = record['1_1_Uso_correcto_EPP_dotacion'].split(' - ')[0] if record['1_1_Uso_correcto_EPP_dotacion'] else "SI"
                current_1_2 = record['1_2_Cumple_normas_SST'].split(' - ')[0] if record['1_2_Cumple_normas_SST'] else "SI"
                current_1_3 = record['1_3_Reporta_actos_inseguras'].split(' - ')[0] if record['1_3_Reporta_actos_inseguras'] else "SI"
                current_1_4 = record['1_4_Certificado_equipos'].split(' - ')[0] if record['1_4_Certificado_equipos'] else "SI"
                
                new_resp_1_1 = st.radio("1.1 EPP:", ["SI", "NO", "N/A"], 
                                       index=["SI", "NO", "N/A"].index(current_1_1) if current_1_1 in ["SI", "NO", "N/A"] else 0,
                                       key=f"edit_q1_1_{search_id}")
                new_obs_1_1 = st.text_area("Observaciones 1.1:", height=50, key=f"edit_obs_1_1_{search_id}")
                
                new_resp_1_2 = st.radio("1.2 Normas SST:", ["SI", "NO", "N/A"],
                                       index=["SI", "NO", "N/A"].index(current_1_2) if current_1_2 in ["SI", "NO", "N/A"] else 0,
                                       key=f"edit_q1_2_{search_id}")
                new_obs_1_2 = st.text_area("Observaciones 1.2:", height=50, key=f"edit_obs_1_2_{search_id}")
                
                new_resp_1_3 = st.radio("1.3 Reportes:", ["SI", "NO", "N/A"],
                                       index=["SI", "NO", "N/A"].index(current_1_3) if current_1_3 in ["SI", "NO", "N/A"] else 0,
                                       key=f"edit_q1_3_{search_id}")
                new_obs_1_3 = st.text_area("Observaciones 1.3:", height=50, key=f"edit_obs_1_3_{search_id}")
                
                new_resp_1_4 = st.radio("1.4 Certificados:", ["SI", "NO", "N/A"],
                                       index=["SI", "NO", "N/A"].index(current_1_4) if current_1_4 in ["SI", "NO", "N/A"] else 0,
                                       key=f"edit_q1_4_{search_id}")
                new_obs_1_4 = st.text_area("Observaciones 1.4:", height=50, key=f"edit_obs_1_4_{search_id}")
                
                update_button = st.form_submit_button("💾 Actualizar Registro", type="primary")
                
                if update_button:
                    # Preparar datos actualizados
                    new_datos_1_1 = new_resp_1_1 + (f" - {new_obs_1_1}" if new_obs_1_1 else "")
                    new_datos_1_2 = new_resp_1_2 + (f" - {new_obs_1_2}" if new_obs_1_2 else "")
                    new_datos_1_3 = new_resp_1_3 + (f" - {new_obs_1_3}" if new_obs_1_3 else "")
                    new_datos_1_4 = new_resp_1_4 + (f" - {new_obs_1_4}" if new_obs_1_4 else "")
                    
                    new_datos = (new_datos_1_1, new_datos_1_2, new_datos_1_3, new_datos_1_4, new_evaluador, new_area, new_turno)
                    
                    if actualizar_registro(search_id, new_datos):
                        st.success(f"✅ Registro ID {search_id} actualizado exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar el registro.")
        else:
            st.error(f"❌ No se encontró un registro con ID {search_id}")

def exportar_tab():
    """Tab para exportar registros a Excel"""
    st.header("📊 Exportar Registros")
    
    st.write("Descarga todos los registros de Safety Walk en formato Excel.")
    
    if st.button("📥 Generar y Descargar Excel", type="primary"):
        df = obtener_todos_registros()
        
        if df is not None and not df.empty:
            # Renombrar columnas para Excel
            column_mapping = {
                'id': 'ID',
                'fecha_registro': 'Fecha de Registro',
                '1_1_Uso_correcto_EPP_dotacion': '1.1 EPP y Dotación',
                '1_2_Cumple_normas_SST': '1.2 Normas SST',
                '1_3_Reporta_actos_inseguras': '1.3 Reporta Actos Inseguros',
                '1_4_Certificado_equipos': '1.4 Certificados Equipos',
                'evaluador': 'Evaluador',
                'area_evaluada': 'Área Evaluada',
                'turno': 'Turno'
            }
            
            df_export = df.rename(columns=column_mapping)
            excel_file = to_excel(df_export)
            
            st.success(f"✅ Archivo Excel generado exitosamente! ({len(df)} registros)")
            
            st.download_button(
                label="📁 Descargar Excel",
                data=excel_file,
                file_name=f"safety_walk_registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("⚠️ No hay registros disponibles para exportar.")

def main_app():
    """Aplicación principal del formulario"""
    # Header con logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🦺 Safety Walk - Sistema SST")
    with col2:
        st.write(f"👤 **Usuario:** {st.session_state.username}")
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            logout()
    
    st.markdown("---")

    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📝 Nuevo Formulario", "🔍 Buscar/Editar", "📊 Exportar"])
    
    with tab1:
        formulario_tab()
    
    with tab2:
        buscar_tab()
    
    with tab3:
        exportar_tab()

    # Sidebar con información
    with st.sidebar:
        st.header("ℹ️ Información")
        st.write("**Safety Walk - Sistema SST**")
        st.write("Sistema completo para evaluación de seguridad y salud en el trabajo")
        st.write(f"**Usuario:** {st.session_state.username}")
        
        st.markdown("---")
        st.subheader("🛠️ Funcionalidades")
        st.write("✅ Crear evaluaciones")
        st.write("✅ Buscar por ID")
        st.write("✅ Editar registros")
        st.write("✅ Exportar a Excel")
        
        st.markdown("---")
        st.subheader("📞 Contacto")
        st.write("Coordinación SST")
        st.write("Brigada de Emergencias")
        
        # Estado de la aplicación
        st.markdown("---")
        st.subheader("📈 Estado")
        if init_connection():
            st.success("✅ Conectado a BD")
        else:
            st.error("❌ Sin conexión")

# Lógica principal de la aplicación
if __name__ == "__main__":
    # Verificar si está logueado
    if not check_login():
        login_form()
    else:
        main_app()
