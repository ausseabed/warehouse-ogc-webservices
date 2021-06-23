<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
 xmlns="http://www.opengis.net/sld"
 xmlns:ogc="http://www.opengis.net/ogc"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>backscatter</Name>
    <UserStyle>
      <Title>Backscatter</Title>
      <Abstract></Abstract>
      <FeatureTypeStyle>
        <Rule>
          <Name>Colors</Name>
          <Title>Opaque Raster</Title>
          <Abstract>A raster with 100% opacity</Abstract>
          <RasterSymbolizer>
            <Opacity>1.0</Opacity>
            <ColorMap type="ramp">
              <ColorMapEntry color="#000000" quantity="-51" label="No Data" opacity="0"/><!-- transparent-->
              <ColorMapEntry color="#ffff80" quantity="-50" label="-50" opacity="1"/><!-- yellow -->
              <ColorMapEntry color="#f0a52e" quantity="-35" label="-35" opacity="1"/><!-- orange -->
              <ColorMapEntry color="#6b0000" quantity="-20" label="-20" opacity="1"/><!-- brown -->
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
