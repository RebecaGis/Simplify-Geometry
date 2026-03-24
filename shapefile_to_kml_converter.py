import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import fiona
import tempfile
import os
import zipfile
from pathlib import Path
import warnings
from shapely.ops import transform

# Configuração de ambiente para restauração de SHX
os.environ['SHAPE_RESTORE_SHX'] = 'YES'

# Habilitar drivers de KML
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(page_title="Shapefile para KML", page_icon="🗺️", layout="wide")

# CSS ATUALIZADO
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #1f77b4; text-align: center; margin-bottom: 2rem; font-weight: bold; }
    
    /* Novo estilo para o quadro informativo */
    .info-box { 
        padding: 15px; 
        background-color: #e3f2fd; /* Azul bem claro */
        border-left: 5px solid #2196f3; /* Barra lateral azul */
        border-radius: 8px; 
        margin: 15px 0;
        color: #0d47a1; /* Texto em azul escuro para contraste */
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .stButton > button { width: 100%; background-color: #1f77b4; color: white; font-weight: bold; height: 3rem; }
    .stButton > button:hover { background-color: #1565c0; border-color: #1565c0; }
</style>
""", unsafe_allow_html=True)

class ShapefileToKMLConverter:
    def __init__(self, tolerance=0.001, preserve_topology=True):
        self.tolerance = tolerance
        self.preserve_topology = preserve_topology
        
    def get_geometry_info(self, gdf):
        try:
            exploded_gdf = gdf.explode(index_parts=False)
            total_vertices = 0
            for geom in exploded_gdf.geometry:
                if geom is None or geom.is_empty: continue
                if hasattr(geom, 'exterior'):
                    total_vertices += len(geom.exterior.coords)
                    for interior in geom.interiors: total_vertices += len(interior.coords)
                elif hasattr(geom, 'coords'):
                    total_vertices += len(geom.coords)
            return {
                'total_features': len(gdf),
                'total_vertices': total_vertices,
                'invalid_geometries': int((~gdf.geometry.is_valid).sum()),
                'geometry_types': gdf.geometry.geom_type.unique().tolist()
            }
        except Exception:
            return {'total_features': len(gdf), 'total_vertices': 0, 'invalid_geometries': 0, 'geometry_types': []}

    def convert(self, gdf, output_path, simplify=True):
        if gdf.crs is None: gdf.set_crs("EPSG:4326", inplace=True)
        elif gdf.crs != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
        gdf['geometry'] = gdf['geometry'].buffer(0) 
        if simplify and self.tolerance > 0:
            gdf['geometry'] = gdf['geometry'].simplify(self.tolerance, self.preserve_topology)
        gdf['geometry'] = gdf['geometry'].map(lambda g: transform(lambda x, y, z=None: (x, y), g) if g else None)
        gdf.to_file(output_path, driver='KML')
        return output_path

def main():
    st.markdown('<h1 class="main-header">Shapefile to KML Converter - Simplify Geometry</h1>', unsafe_allow_html=True)
    
    # Quadro informativo com o novo CSS
    st.markdown("""
    <div class="info-box">
        <strong>📋 Formatos aceitos e dicas:</strong><br>
        • Envie um arquivo <b>.zip</b> contendo (shp, dbf, shx, prj) ou selecione os arquivos individuais juntos.<br>
        • A tolerância de <b>0.0001</b> é ideal para preservar detalhes de manchas de inundação.<br>
        • Certifique-se de que o Shapefile não possui geometrias corrompidas antes do upload.
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ Opções")
        do_simplify = st.checkbox("Simplificar Geometria", value=True)
        tol = st.slider("Tolerância", 0.0, 0.01, 0.001, step=0.0001, format="%.4f") if do_simplify else 0.0

    files = st.file_uploader("Upload de arquivos", type=['zip', 'shp', 'dbf', 'shx', 'prj'], accept_multiple_files=True)

    if files:
        with tempfile.TemporaryDirectory() as temp_dir:
            for f in files:
                path = os.path.join(temp_dir, f.name)
                with open(path, "wb") as buffer: buffer.write(f.getbuffer())
                if f.name.endswith('.zip'):
                    with zipfile.ZipFile(path, 'r') as z: z.extractall(temp_dir)
            
            shp_list = list(Path(temp_dir).rglob("*.shp"))
            if not shp_list:
                st.warning("Aguardando arquivo .shp...")
                return
            
            try:
                gdf = gpd.read_file(str(shp_list[0]))
                conv = ShapefileToKMLConverter(tolerance=tol)
                info = conv.get_geometry_info(gdf)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Objetos", info['total_features'])
                c2.metric("Vértices", f"{info['total_vertices']:,}")
                c3.metric("Geometria", ", ".join(info['geometry_types']))

                if st.button("🪄 Converter e Gerar Download"):
                    out_kml = os.path.join(temp_dir, "output.kml")
                    conv.convert(gdf, out_kml, simplify=do_simplify)
                    with open(out_kml, "rb") as k:
                        st.download_button(label="📥 Baixar KML", data=k, file_name=f"{shp_list[0].stem}.kml", mime="application/vnd.google-earth.kml+xml")
                    st.success("Conversão concluída!")
            except Exception as e:
                st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()