# Simplify Geometry · Shapefile para KML

<!-- project-badges:start -->
![Interface: Streamlit](https://img.shields.io/static/v1?label=Interface&message=Streamlit&color=FF4B4B&style=flat)
![Geoprocessamento: GeoPandas](https://img.shields.io/static/v1?label=Geoprocessamento&message=GeoPandas&color=139C5A&style=flat)
[![Autoria: Rebeca Diniz Moura](https://img.shields.io/static/v1?label=Autoria&message=Rebeca%20Diniz%20Moura&color=8b5cf6&style=flat)](https://github.com/RebecaGis)
<!-- project-badges:end -->


Aplicação Streamlit para converter Shapefile em KML, com opção de simplificar geometrias.

## Executar localmente

Com Python e as dependências geoespaciais do sistema disponíveis:

```bash
python -m pip install -r requirements.txt
streamlit run shapefile_to_kml_converter.py
```

Envie os componentes do Shapefile (`.shp`, `.dbf`, `.shx`, `.prj`) ou um ZIP contendo esses arquivos. Confira o sistema de referência e a tolerância de simplificação antes de usar os resultados.
