<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>ausseabed_bathymetry</Name>
    <UserStyle>
      <Title>Bathymetry Coverages (boundaries)</Title>
      <Abstract>A sample style that draws a polygon</Abstract>
      <FeatureTypeStyle>
        <Rule>
          <Name>rule1</Name>
          <Title>Bathymetry Coverages (boundaries)</Title>
          <Abstract>A polygon with a purple fill</Abstract>
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#8856a7</CssParameter>
              <CssParameter name="fill-opacity">0.5</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="fill">#FFFFFF</CssParameter>
              <CssParameter name="stroke-width">0.5</CssParameter>
            </Stroke> 
          </PolygonSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
