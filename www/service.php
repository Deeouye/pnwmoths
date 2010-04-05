<?php
require_once 'bootstrap.php';

function getSamples($species, $options) {
    $sampleOptions = array(
        "filters" => array(),
        "species" => $species
    );
    $allowedFilters = array("elevation", "date");

    foreach ($allowedFilters as $allowedFilter) {
        if (array_key_exists($allowedFilter, $options)) {
            $value = $options[$allowedFilter];
            if ($value != "") {
                $sampleOptions["filters"][$allowedFilter] = $value;
            }
        }
    }

    return PNWMoths_Model_SpeciesSample::getData($sampleOptions);
}

function getPhenology($species) {
    $phenology = PNWMoths_Model_Phenology::getData(
        array("species" => $species)
    );
    return array_values($phenology);
}

function getMap($species) {
    return PNWMoths_Model_Map::getData(
        array(
            "species" => $species
        )
    );
}

if (array_key_exists("method", $_GET) && array_key_exists("species", $_GET)) {
    $species = $_GET["species"];
    unset($_GET["species"]);
    $method = $_GET["method"];
    unset($_GET["method"]);

    $options = $_GET;

    switch ($method) {
        case 'getPhenology':
            $data = getPhenology($species);
            break;
        case 'getMap':
            $data = getMap($species);
            break;
        case 'getSamples':
            $data = getSamples($species, $options);
            break;
        default:
            break;
    }

    if (isset($data)) {
        header("Content-type: text/plain");
        echo Zend_Json::encode($data);
    }
}
?>