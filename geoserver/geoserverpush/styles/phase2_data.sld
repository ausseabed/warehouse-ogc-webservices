<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor version="1.0.0"
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
 xmlns="http://www.opengis.net/sld"
 xmlns:ogc="http://www.opengis.net/ogc"
 xmlns:xlink="http://www.w3.org/1999/xlink"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- a Named Layer is the basic building block of an SLD document -->
  <NamedLayer>
    <Name>phase2_data</Name>
    <UserStyle>
    <!-- Styles can have names, titles and abstracts -->
      <Title>Phase 2 Data</Title>
      <Abstract>A generic colour ramp used for phase 2 data</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- A FeatureTypeStyle for rendering rasters -->
      <FeatureTypeStyle>
        <Rule>
          <Name>phase2_data_rule</Name>
          <RasterSymbolizer>
            <Opacity>1.0</Opacity>
            <ColorMap type="ramp">
              <ColorMapEntry color="#000000" quantity="0" label="No Data" opacity="0"/><!-- transparent-->
              <ColorMapEntry color="#6B0000" label="" opacity="1.0" quantity="1"/>
              <ColorMapEntry color="#F2A72E" label="" opacity="1.0" quantity="127"/>
              <ColorMapEntry color="#FFFF80" label="" opacity="1.0" quantity="255"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>