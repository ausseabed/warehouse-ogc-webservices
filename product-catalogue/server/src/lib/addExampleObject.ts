import { ProductEntry } from './entity/product-entry';

export function addExampleObject () {
    const productEntry = new ProductEntry();
    productEntry.id = 1;
    productEntry.gazeteerName = "Beagle Commonwealth Marine Reserve";
    productEntry.year = "2018";
    productEntry.UUID = "GA-0364";
    productEntry.resolution = "1m";
    productEntry.srs = "EPSG:32755";
    productEntry.metadataPersistentId = "";
    productEntry.l3ProductTifLocation = "s3://bathymetry-survey-288871573946-beagle-grid0/GA-0364_BlueFin_MB/BlueFin_2018-172_1m_Overlay.tif";
    productEntry.l0CoverageLocation = "s3://bathymetry-survey-288871573946/L0Coverage/coverage.shp";
    productEntry.l3CoverageLocation = "s3://bathymetry-survey-288871573946-beagle-grid0/GA-0364_BlueFin_MB/BlueFin_2018-172_1m.shp";
    productEntry.hillshadeLocation = "s3://bathymetry-survey-288871573946-beagle-grid0/GA-0364_BlueFin_MB/BlueFin_2018-172_1m_HS.tif";
    return (productEntry);
}

export function addExampleObject2 () {
    const productEntry = new ProductEntry();
    productEntry.id = 2;
    productEntry.gazeteerName = "Wilsons Promontory Marine National Park";
    productEntry.year = "2013";
    productEntry.UUID = "68f44afd-78d0-412f-bf9c-9c9fdbe43968";
    productEntry.resolution = "1m";
    productEntry.srs = "EPSG:28355";
    productEntry.metadataPersistentId = "";
    productEntry.l3ProductTifLocation = "s3://ausseabed-public-bathymetry-nonprod/L3/68f44afd-78d0-412f-bf9c-9c9fdbe43968/01_Bathy_Overlay.tif";
    productEntry.l0CoverageLocation = "s3://ausseabed-public-bathymetry-nonprod/L0/68f44afd-78d0-412f-bf9c-9c9fdbe43968/Beagle Commonwealth Marine Reserve 2018 Coverage.shp";
    productEntry.l3CoverageLocation = "s3://ausseabed-public-bathymetry-nonprod/L3/68f44afd-78d0-412f-bf9c-9c9fdbe43968/01_Bathy_Overlay.shp";
    productEntry.hillshadeLocation = "s3://ausseabed-public-bathymetry-nonprod/L3/68f44afd-78d0-412f-bf9c-9c9fdbe43968/01_Bathy_HS.tif";
    return (productEntry);
}
