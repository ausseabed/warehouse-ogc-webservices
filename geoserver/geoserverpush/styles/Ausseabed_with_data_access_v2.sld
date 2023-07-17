<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>Bathymetry_byDataAccess</sld:Name>
    <sld:UserStyle>
      <sld:Name>Bathymetry_byDataAccess</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>Bathymetry with online access</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsLike wildCard="%" singleChar="_" escape="\">
              <ogc:PropertyName>BATHY_URL</ogc:PropertyName>
              <ogc:Literal>http%</ogc:Literal>
            </ogc:PropertyIsLike>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#9152e0</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Bathymetry with online access</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsLike wildCard="%" singleChar="_" escape="\">
              <ogc:PropertyName>BATHY_URL</ogc:PropertyName>
              <ogc:Literal>File%</ogc:Literal>
            </ogc:PropertyIsLike>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#9152e0</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Bathymetry without online access</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsLike wildCard="%" singleChar="_" escape="\">
              <ogc:PropertyName>BATHY_URL</ogc:PropertyName>
              <ogc:Literal>N/A</ogc:Literal>
            </ogc:PropertyIsLike>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#cdcdcd</sld:CssParameter>
            </sld:Fill>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
