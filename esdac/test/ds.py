import html5lib
from bs4 import BeautifulSoup
from pyRdfa import pyRdfa
from dotenv import load_dotenv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DC, DCAT, DCTERMS, SKOS, SDO, FOAF
import sys,time,hashlib,os
sys.path.append('../utils')
from database import insertRecord, dbQuery

# Load environment variables from .env file
load_dotenv()

rid="http://example.com/foo"
ttl=""
res='''

    <section id="block-system-main" class="block block-system clearfix">

      
  <form action="/content/european-soil-database-v20-vector-and-attribute-data" method="post" id="test-dataset-entityform-edit-form--2" accept-charset="UTF-8"><div><div class="panel-flexible panels-flexible-8 clearfix" >
<div class="panel-flexible-inside panels-flexible-8-inside">
<div class="panels-flexible-row panels-flexible-row-8-3 panels-flexible-row-first clearfix ">
  <div class="inside panels-flexible-row-inside panels-flexible-row-8-3-inside panels-flexible-row-inside-first clearfix">
<div class="panels-flexible-region panels-flexible-region-8-top_abstract panels-flexible-region-first panels-flexible-region-last top-dataset-abstract">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-top_abstract-inside panels-flexible-region-inside-first panels-flexible-region-inside-last">
<div class="panel-pane pane-entity-field pane-node-field-data-abstract-plaintext"  >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-abstract-plaintext field-type-text-long field-label-hidden"><div class="field-items"><div class="field-item even" property="dct:description">This database (2004) is the only harmonized soil database for Europe, extending also to Eurasia. It contains a soil geographical database SGDBE (polygons) to which a number of essential soil attributes are attached, and an associate database PTRDB, with attributes which values have been derived through pedotransfer rules. Also part of the database is the Soil Profile Analytical Database, that contains measured and estimated soil profiles for Europe.</div></div></div>  </div>

  
  </div>
  </div>
</div>
  </div>
</div>
<div class="panels-flexible-row panels-flexible-row-8-main-row clearfix">
  <div class="inside panels-flexible-row-inside panels-flexible-row-8-main-row-inside clearfix">
<div class="panels-flexible-region panels-flexible-region-8-center panels-flexible-region-first">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-center-inside panels-flexible-region-inside-first">
<div class="panel-pane pane-views pane-datasets-image"  >
  
      
  
  <div class="pane-content">
    <div class="view view-datasets-image view-id-datasets_image view-display-id-default view-dom-id-7623ced5a5d27ce3fb4badf0062ff25a">
        
  
  
      <div class="view-content">
        <div class="views-row views-row-1 views-row-odd views-row-first views-row-last">
      
  <div>        <img typeof="foaf:Image" src="https://esdac.jrc.ec.europa.eu/public_path//styles/medium/public/datainventoryitem_img/Data_Esdbv2.png?itok=Eg01rVeu" width="220" height="157" alt="European Soil Database v2.0 (vector and attribute data)" title="European Soil Database v2.0 (vector and attribute data)" />  </div>  </div>
    </div>
  
  
  
  
  
  
</div>  </div>

  
  </div>
  </div>
</div>
<div class="panels-flexible-region panels-flexible-region-8-nodeview_body ">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-nodeview_body-inside">
<div class="panel-pane pane-entity-field pane-node-field-data-resource-type"  >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-resource-type field-type-taxonomy-term-reference field-label-inline clearfix"><div class="field-label">Resource Type:&nbsp;</div><div class="field-items"><div class="field-item even" rel=""><a href="/resource-type/datasets" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">Datasets</a></div><div class="field-item odd" rel=""><a href="/resource-type/european-soil-database-soil-properties" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">European Soil Database &amp; soil properties</a></div></div></div>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-registration-req"  >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-registration-req field-type-list-boolean field-label-inline clearfix"><div class="field-label">Registration is requested:&nbsp;</div><div class="field-items"><div class="field-item even" property="">Yes</div></div></div>  </div>

  
  </div>
  </div>
</div>
<div class="panels-flexible-region panels-flexible-region-8-tags panels-flexible-region-last ">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-tags-inside panels-flexible-region-inside-last">
<div class="panel-pane pane-entity-field pane-node-field-data-publisher"  >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-publisher field-type-text field-label-inline clearfix"><div class="field-label">Publisher:&nbsp;</div><div class="field-items"><div class="field-item even">European Commission –- DG JRC</div></div></div>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-publication-year"  >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-publication-year field-type-datetime field-label-inline clearfix"><div class="field-label">Year:&nbsp;</div><div class="field-items"><div class="field-item even" property=""><span class="date-display-single" property="" datatype="xsd:dateTime" content="2001-01-01T00:00:00+01:00">2001</span></div></div></div>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-scale"  >
  
      
  
  <div class="pane-content">
      </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-keywords"  id="node_detail_keywords" >
  
      
  
  <div class="pane-content">
    <div class="field field-name-field-data-keywords field-type-taxonomy-term-reference field-label-inline clearfix"><div class="field-label">Keywords:&nbsp;</div><div class="field-items"><div class="field-item even" rel=""><a href="/tags/european-soil-database-soil-geographical-database-eurasia-sgdbe-soils-land-management-european" typeof="skos:Concept" property="rdfs:label skos:prefLabel" datatype="">European Soil Database; Soil Geographical Database of Eurasia; SGDBE; Soils; Land Management; European soil bureau network;</a></div></div></div>  </div>

  
  </div>
  </div>
</div>
  </div>
</div>
<div class="panels-flexible-row panels-flexible-row-8-1 clearfix ">
  <div class="inside panels-flexible-row-inside panels-flexible-row-8-1-inside clearfix">
<div class="panels-flexible-region panels-flexible-region-8-description panels-flexible-region-first panels-flexible-region-last ">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-description-inside panels-flexible-region-inside-first panels-flexible-region-inside-last">
<div id="tabs-0-description"><ul><li class="first"><a href="#tabs-0-description-1">Description</a></li>
<li class="last"><a href="#tabs-0-description-2">Request Form</a></li>
</ul><div id="tabs-0-description-1"><div class="panel-pane pane-entity-field pane-node-body"  id="node_detail_body" >
  
      
  
  <div class="pane-content">
    <div class="field field-name-body field-type-text-with-summary field-label-hidden"><div class="field-items"><div class="field-item even" property="dct:description"><p align="justify">The European Soil Databases (ESDB), distribution version v2.0 is freely available to the public after user registration. Please note that the spatial data are in <strong>vector</strong> format.</p>
<p align="justify">Documention for this database can be found in the following material :</p>
<ul>
<li><a href="/ESDB_Archive/ESDBv2/index.htm" target="_blank">Documentation for ESDB v2.0 </a>taken from the ESDB v2.0 CD-ROM .</li>
<li>A number of <a href="/content/legend-files">Legend Files</a> (LYR or AVL format) applicable to the data from the European Soil Databases are available for download. These files can be applied to the vector based soil data and to the Raster files as well.</li>
<li><a href="/ESDB_Archive/eusoils_docs/other/PTRDBprojRepFinal3.pdf">A Geographical Knowledge Database on Soil Properties for Environmental Studies</a>: More documentation on the Pedo-transfer rules/attributes of the European Soil Database.</li>
<li>All the attribute codes per paramenter in the<a href="http://esdac.jrc.ec.europa.eu/ESDB_Archive/ESDBv2/popup/sg_attr.htm"> SGDBE Attributes</a> and all the attribute codes per <a href="https://esdac.jrc.ec.europa.eu/content/ptrdb-attributes" target="_blank">PTRDB Attributes</a><br />&nbsp;</li>
</ul>
<p>Note that on the basis of the vector data, a number of rasters have been derived, one for each attribute in the database; these raster have been put together in a dataset calles ESDB v2 Raster Library 1kmx1km (<a href="https://esdac.jrc.ec.europa.eu/content/european-soil-database-v2-raster-library-1kmx1km">https://esdac.jrc.ec.europa.eu/content/european-soil-database-v2-raster-...</a>). Also this dataset vcan be accessed after registration.</p>
<p><img alt="Raster Library 1kmx1km" src="/public_path/shared_folder/dataset/Esdac_EU_soilMap.gif" style="width: 500px; height: 353px;" /></p>
<h4>Access to the data:</h4>
<p align="justify">In order to obtain access to these databases : Fill in the online form; after which you will receive further instructions how to download the data.</p>
<p align="justify"><strong>References regarding the data:</strong></p>
<ol>
<li>For ESDB v2.0: &ldquo;The European Soil Database distribution version 2.0, European Commission and the European Soil Bureau Network, CD-ROM, EUR 19945 EN, 2004&quot;.</li>
<li>Panagos Panos. The European soil database (2006) GEO: connexion, 5 (7), pp. 32-33.</li>
</ol>
<p align="justify">Spatial reference system: All data are in the standard GISCO Lambert Azimuth co-ordinate system, documented in the <a href="/node/34761">GISCO Database Manual</a>, in Chapter 3 &quot;Main characteristics of the GISCO reference database&quot; under &quot;Spatial Reference System&quot; &nbsp;</p>
<p align="justify">&nbsp;</p>
</div></div></div>  </div>

  
  </div>
</div><div id="tabs-0-description-2"><div class="panel-pane pane-form"  id="dataset_download_form" >
  
      
  
  <div class="pane-content">
    <input type="hidden" name="form_build_id" value="form-ydbOEHiVPQ6iH92OsMz2p1HqwVMawxA7rfIqYqmpOos" />
<input type="hidden" name="form_id" value="test_dataset_entityform_edit_form" />
<div class="required-fields group-form-group1 field-group-div"><div class="field-type-email field-name-field-form-email field-widget-email-textfield form-wrapper form-group" id="edit-field-form-email--2"><div id="field-form-email-add-more-wrapper--2"><div class="text-full-wrapper"><div class="form-type-textfield form-item-field-form-email-und-0-email form-item form-group">
  <label for="edit-field-form-email-und-0-email--2">email <span class="form-required" title="This field is required.">*</span></label>
 <input class="form-control form-text required" type="text" id="edit-field-form-email-und-0-email--2" name="field_form_email[und][0][email]" value="" size="60" maxlength="128" />
</div>
</div></div></div><div class="field-type-text field-name-field-form-firstlast-name field-widget-text-textfield form-wrapper form-group" id="edit-field-form-firstlast-name--2"><div id="field-form-firstlast-name-add-more-wrapper--2"><div class="form-type-textfield form-item-field-form-firstlast-name-und-0-value form-item form-group">
  <label for="edit-field-form-firstlast-name-und-0-value--2">First and Last Name <span class="form-required" title="This field is required.">*</span></label>
 <input class="text-full form-control form-text required" type="text" id="edit-field-form-firstlast-name-und-0-value--2" name="field_form_firstlast_name[und][0][value]" value="" size="60" maxlength="255" />
</div>
</div></div><div class="field-type-text field-name-field-form-organisation field-widget-text-textfield form-wrapper form-group" id="edit-field-form-organisation--2"><div id="field-form-organisation-add-more-wrapper--2"><div class="form-type-textfield form-item-field-form-organisation-und-0-value form-item form-group">
  <label for="edit-field-form-organisation-und-0-value--2">Organisation <span class="form-required" title="This field is required.">*</span></label>
 <input class="text-full form-control form-text required" type="text" id="edit-field-form-organisation-und-0-value--2" name="field_form_organisation[und][0][value]" value="" size="60" maxlength="255" />
</div>
</div></div></div><div class="required-fields group-form-group2 field-group-div"><div class="field-type-taxonomy-term-reference field-name-field-form-type-of-org field-widget-options-buttons form-wrapper form-group" id="edit-field-form-type-of-org--2"><div class="form-type-radios form-item-field-form-type-of-org-und form-item form-group">
  <label for="edit-field-form-type-of-org-und--2">Type of Organisation <span class="form-required" title="This field is required.">*</span></label>
 <div id="edit-field-form-type-of-org-und--2" class="form-radios"><div class="form-type-radio form-item-field-form-type-of-org-und form-item radio">
 <input type="radio" id="edit-field-form-type-of-org-und-607--2" name="field_form_type_of_org[und]" value="607" class="form-radio" />  <label for="edit-field-form-type-of-org-und-607--2">Private Company </label>

</div>
<div class="form-type-radio form-item-field-form-type-of-org-und form-item radio">
 <input type="radio" id="edit-field-form-type-of-org-und-608--2" name="field_form_type_of_org[und]" value="608" class="form-radio" />  <label for="edit-field-form-type-of-org-und-608--2">Research Organization </label>

</div>
<div class="form-type-radio form-item-field-form-type-of-org-und form-item radio">
 <input type="radio" id="edit-field-form-type-of-org-und-609--2" name="field_form_type_of_org[und]" value="609" class="form-radio" />  <label for="edit-field-form-type-of-org-und-609--2">University </label>

</div>
<div class="form-type-radio form-item-field-form-type-of-org-und form-item radio">
 <input type="radio" id="edit-field-form-type-of-org-und-610--2" name="field_form_type_of_org[und]" value="610" class="form-radio" />  <label for="edit-field-form-type-of-org-und-610--2">Public Administration (Ministries, Agencies, Municipalities, ...) </label>

</div>
<div class="form-type-radio form-item-field-form-type-of-org-und form-item radio">
 <input type="radio" id="edit-field-form-type-of-org-und-611--2" name="field_form_type_of_org[und]" value="611" class="form-radio" />  <label for="edit-field-form-type-of-org-und-611--2">Other (specify) </label>

</div>
</div>
</div>
</div><div class="field-type-text field-name-field-form-other-org field-widget-text-textfield form-wrapper form-group" id="edit-field-form-other-org--2"><div id="field-form-other-org-add-more-wrapper--2"><div class="form-type-textfield form-item-field-form-other-org-und-0-value form-item form-group">
  <label for="edit-field-form-other-org-und-0-value--2">Other Org. <span class="form-required" title="This field is required.">*</span></label>
 <input class="text-full form-control form-text required" type="text" id="edit-field-form-other-org-und-0-value--2" name="field_form_other_org[und][0][value]" value="" size="60" maxlength="255" />
</div>
</div></div><div class="field-type-country field-name-field-form-country field-widget-options-select form-wrapper form-group" id="edit-field-form-country--2"><div class="form-type-select form-item-field-form-country-und form-item form-group">
  <label for="edit-field-form-country-und--2">Country <span class="form-required" title="This field is required.">*</span></label>
 <select class="form-control chosen-disable form-select required" id="edit-field-form-country-und--2" name="field_form_country[und]"><option value="_none">- Select a value -</option><option value="AF">Afghanistan</option><option value="AX">Aland Islands</option><option value="AL">Albania</option><option value="DZ">Algeria</option><option value="AS">American Samoa</option><option value="AD">Andorra</option><option value="AO">Angola</option><option value="AI">Anguilla</option><option value="AQ">Antarctica</option><option value="AG">Antigua and Barbuda</option><option value="AR">Argentina</option><option value="AM">Armenia</option><option value="AW">Aruba</option><option value="AU">Australia</option><option value="AT">Austria</option><option value="AZ">Azerbaijan</option><option value="BS">Bahamas</option><option value="BH">Bahrain</option><option value="BD">Bangladesh</option><option value="BB">Barbados</option><option value="BY">Belarus</option><option value="BE">Belgium</option><option value="BZ">Belize</option><option value="BJ">Benin</option><option value="BM">Bermuda</option><option value="BT">Bhutan</option><option value="BO">Bolivia</option><option value="BA">Bosnia and Herzegovina</option><option value="BW">Botswana</option><option value="BV">Bouvet Island</option><option value="BR">Brazil</option><option value="IO">British Indian Ocean Territory</option><option value="VG">British Virgin Islands</option><option value="BN">Brunei</option><option value="BG">Bulgaria</option><option value="BF">Burkina Faso</option><option value="BI">Burundi</option><option value="KH">Cambodia</option><option value="CM">Cameroon</option><option value="CA">Canada</option><option value="CV">Cape Verde</option><option value="BQ">Caribbean Netherlands</option><option value="KY">Cayman Islands</option><option value="CF">Central African Republic</option><option value="TD">Chad</option><option value="CL">Chile</option><option value="CN">China</option><option value="CX">Christmas Island</option><option value="CC">Cocos (Keeling) Islands</option><option value="CO">Colombia</option><option value="KM">Comoros</option><option value="CG">Congo (Brazzaville)</option><option value="CD">Congo (Kinshasa)</option><option value="CK">Cook Islands</option><option value="CR">Costa Rica</option><option value="HR">Croatia</option><option value="CU">Cuba</option><option value="CW">Curaçao</option><option value="CY">Cyprus</option><option value="CZ">Czech Republic</option><option value="DK">Denmark</option><option value="DJ">Djibouti</option><option value="DM">Dominica</option><option value="DO">Dominican Republic</option><option value="EC">Ecuador</option><option value="EG">Egypt</option><option value="SV">El Salvador</option><option value="GQ">Equatorial Guinea</option><option value="ER">Eritrea</option><option value="EE">Estonia</option><option value="ET">Ethiopia</option><option value="FK">Falkland Islands</option><option value="FO">Faroe Islands</option><option value="FJ">Fiji</option><option value="FI">Finland</option><option value="FR">France</option><option value="GF">French Guiana</option><option value="PF">French Polynesia</option><option value="TF">French Southern Territories</option><option value="GA">Gabon</option><option value="GM">Gambia</option><option value="GE">Georgia</option><option value="DE">Germany</option><option value="GH">Ghana</option><option value="GI">Gibraltar</option><option value="GR">Greece</option><option value="GL">Greenland</option><option value="GD">Grenada</option><option value="GP">Guadeloupe</option><option value="GU">Guam</option><option value="GT">Guatemala</option><option value="GG">Guernsey</option><option value="GN">Guinea</option><option value="GW">Guinea-Bissau</option><option value="GY">Guyana</option><option value="HT">Haiti</option><option value="HM">Heard Island and McDonald Islands</option><option value="HN">Honduras</option><option value="HK">Hong Kong S.A.R., China</option><option value="HU">Hungary</option><option value="IS">Iceland</option><option value="IN">India</option><option value="ID">Indonesia</option><option value="IR">Iran</option><option value="IQ">Iraq</option><option value="IE">Ireland</option><option value="IM">Isle of Man</option><option value="IL">Israel</option><option value="IT">Italy</option><option value="CI">Ivory Coast</option><option value="JM">Jamaica</option><option value="JP">Japan</option><option value="JE">Jersey</option><option value="JO">Jordan</option><option value="KZ">Kazakhstan</option><option value="KE">Kenya</option><option value="KI">Kiribati</option><option value="KW">Kuwait</option><option value="KG">Kyrgyzstan</option><option value="LA">Laos</option><option value="LV">Latvia</option><option value="LB">Lebanon</option><option value="LS">Lesotho</option><option value="LR">Liberia</option><option value="LY">Libya</option><option value="LI">Liechtenstein</option><option value="LT">Lithuania</option><option value="LU">Luxembourg</option><option value="MO">Macao S.A.R., China</option><option value="MK">Macedonia</option><option value="MG">Madagascar</option><option value="MW">Malawi</option><option value="MY">Malaysia</option><option value="MV">Maldives</option><option value="ML">Mali</option><option value="MT">Malta</option><option value="MH">Marshall Islands</option><option value="MQ">Martinique</option><option value="MR">Mauritania</option><option value="MU">Mauritius</option><option value="YT">Mayotte</option><option value="MX">Mexico</option><option value="FM">Micronesia</option><option value="MD">Moldova</option><option value="MC">Monaco</option><option value="MN">Mongolia</option><option value="ME">Montenegro</option><option value="MS">Montserrat</option><option value="MA">Morocco</option><option value="MZ">Mozambique</option><option value="MM">Myanmar</option><option value="NA">Namibia</option><option value="NR">Nauru</option><option value="NP">Nepal</option><option value="NL">Netherlands</option><option value="AN">Netherlands Antilles</option><option value="NC">New Caledonia</option><option value="NZ">New Zealand</option><option value="NI">Nicaragua</option><option value="NE">Niger</option><option value="NG">Nigeria</option><option value="NU">Niue</option><option value="NF">Norfolk Island</option><option value="MP">Northern Mariana Islands</option><option value="KP">North Korea</option><option value="NO">Norway</option><option value="OM">Oman</option><option value="PK">Pakistan</option><option value="PW">Palau</option><option value="PS">Palestinian Territory</option><option value="PA">Panama</option><option value="PG">Papua New Guinea</option><option value="PY">Paraguay</option><option value="PE">Peru</option><option value="PH">Philippines</option><option value="PN">Pitcairn</option><option value="PL">Poland</option><option value="PT">Portugal</option><option value="PR">Puerto Rico</option><option value="QA">Qatar</option><option value="RE">Reunion</option><option value="RO">Romania</option><option value="RU">Russia</option><option value="RW">Rwanda</option><option value="BL">Saint Barthélemy</option><option value="SH">Saint Helena</option><option value="KN">Saint Kitts and Nevis</option><option value="LC">Saint Lucia</option><option value="MF">Saint Martin (French part)</option><option value="PM">Saint Pierre and Miquelon</option><option value="VC">Saint Vincent and the Grenadines</option><option value="WS">Samoa</option><option value="SM">San Marino</option><option value="ST">Sao Tome and Principe</option><option value="SA">Saudi Arabia</option><option value="SN">Senegal</option><option value="RS">Serbia</option><option value="SC">Seychelles</option><option value="SL">Sierra Leone</option><option value="SG">Singapore</option><option value="SX">Sint Maarten</option><option value="SK">Slovakia</option><option value="SI">Slovenia</option><option value="SB">Solomon Islands</option><option value="SO">Somalia</option><option value="ZA">South Africa</option><option value="GS">South Georgia and the South Sandwich Islands</option><option value="KR">South Korea</option><option value="SS">South Sudan</option><option value="ES">Spain</option><option value="LK">Sri Lanka</option><option value="SD">Sudan</option><option value="SR">Suriname</option><option value="SJ">Svalbard and Jan Mayen</option><option value="SZ">Swaziland</option><option value="SE">Sweden</option><option value="CH">Switzerland</option><option value="SY">Syria</option><option value="TJ">Tajikistan</option><option value="TZ">Tanzania</option><option value="TH">Thailand</option><option value="TL">Timor-Leste</option><option value="TG">Togo</option><option value="TK">Tokelau</option><option value="TO">Tonga</option><option value="TT">Trinidad and Tobago</option><option value="TN">Tunisia</option><option value="TR">Turkey</option><option value="TM">Turkmenistan</option><option value="TC">Turks and Caicos Islands</option><option value="TV">Tuvalu</option><option value="VI">U.S. Virgin Islands</option><option value="UG">Uganda</option><option value="UA">Ukraine</option><option value="AE">United Arab Emirates</option><option value="GB">United Kingdom</option><option value="US">United States</option><option value="UM">United States Minor Outlying Islands</option><option value="UY">Uruguay</option><option value="UZ">Uzbekistan</option><option value="VU">Vanuatu</option><option value="VA">Vatican</option><option value="VE">Venezuela</option><option value="VN">Vietnam</option><option value="WF">Wallis and Futuna</option><option value="EH">Western Sahara</option><option value="YE">Yemen</option><option value="ZM">Zambia</option><option value="ZW">Zimbabwe</option></select>
</div>
</div></div><div class="field-type-text field-name-field-form-purpose field-widget-text-textfield form-wrapper form-group" id="edit-field-form-purpose--2"><div id="field-form-purpose-add-more-wrapper--2"><div class="form-type-textfield form-item-field-form-purpose-und-0-value form-item form-group">
  <label for="edit-field-form-purpose-und-0-value--2">Purpose for which the data will be used (min 30 characters) <span class="form-required" title="This field is required.">*</span></label>
 <input class="text-full form-control form-text required" type="text" id="edit-field-form-purpose-und-0-value--2" name="field_form_purpose[und][0][value]" value="" size="60" maxlength="1000" />
</div>
</div></div><div class="field-type-list-boolean field-name-field-subscribe-to-esdac-monthly field-widget-options-onoff form-wrapper form-group" id="edit-field-subscribe-to-esdac-monthly--2"><div class="form-type-checkbox form-item-field-subscribe-to-esdac-monthly-und form-item checkbox">
 <input type="checkbox" id="edit-field-subscribe-to-esdac-monthly-und--2" name="field_subscribe_to_esdac_monthly[und]" value="1" class="form-checkbox" />  <label for="edit-field-subscribe-to-esdac-monthly-und--2">Subscribe to ESDAC Monthly newsletter </label>

<p class="help-block">Subscribe to ESDAC Monthly newsletter</p>
</div>
</div><div class="field-type-list-boolean field-name-field-form-accept field-widget-options-onoff form-wrapper form-group" id="edit-field-form-accept--2"><div class="form-type-checkbox form-item-field-form-accept-und form-item checkbox">
 <input type="checkbox" id="edit-field-form-accept-und--2" name="field_form_accept[und]" value="1" class="form-checkbox required" />  <label for="edit-field-form-accept-und--2">Accept <span class="form-required" title="This field is required.">*</span></label>

<p class="help-block">By sending these data, you declare that you have read &amp; accept the notification below and that your personal data will be handled by the JRC only for statistical purposes (conform to <a href="/public_path/shared_folder/Contact-list-Privacy-Statement-ESDAC-2020-03-10-final.pdf" target="blank">privacy statement</a>). </p>
</div>
</div><div class="form-actions form-wrapper form-group" id="edit-actions--2"><div class="captcha"><input type="hidden" name="captcha_sid" value="38905853" />
<input type="hidden" name="captcha_token" value="8f77a4d7158b27d4b77cc6b522f92daa" />
<img typeof="foaf:Image" src="/image_captcha?sid=38905853&amp;ts=1721037656" width="180" height="60" alt="Image CAPTCHA" title="Image CAPTCHA" /><div class="form-type-textfield form-item-captcha-response form-item form-group">
  <label for="edit-captcha-response--2">What code is in the image? <span class="form-required" title="This field is required.">*</span></label>
 <input class="form-control form-text required" type="text" id="edit-captcha-response--2" name="captcha_response" value="" size="15" maxlength="128" />
<p class="help-block">Enter the characters shown in the image.</p>
</div>
</div><button class="btn btn-primary form-submit" id="edit-submit--2" name="op" value="Submit" type="submit">Submit</button>
</div>  </div>

  
  </div>
</div></div>  </div>
</div>
  </div>
</div>
<div class="panels-flexible-row panels-flexible-row-8-2 panels-flexible-row-last clearfix ">
  <div class="inside panels-flexible-row-inside panels-flexible-row-8-2-inside panels-flexible-row-inside-last clearfix">
<div class="panels-flexible-region panels-flexible-region-8-resource_detail_footer panels-flexible-region-first panels-flexible-region-last ">
  <div class="inside panels-flexible-region-inside panels-flexible-region-8-resource_detail_footer-inside panels-flexible-region-inside-first panels-flexible-region-inside-last">
<div class="panel-pane pane-custom pane-1"  >
  
      
  
  <div class="pane-content">
    <i class="fa fa-question-circle fa-2x" aria-hidden="true"></i> For any problem / question / comment on this dataset, please contact 
<a href="mailto:ec-esdac@ec.europa.eu,marc.van-liedekerke@ec.europa.eu,panos.panagos@ec.europa.eu?subject=Dataset Help Desk - ID 1 - European Soil Database v2.0 (vector and attribute data)">ec-esdac@ec.europa.eu</a>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-dataset-notification"  >
  
        <h2 class="pane-title">
      Notification:    </h2>
    
  
  <div class="pane-content">
    <div class="field field-name-field-data-dataset-notification field-type-text-with-summary field-label-hidden"><div class="field-items"><div class="field-item even" property=""><ol>
<li>The data have been prepared for use by the Land Resource Management Unit (Institute for Environment &amp; Sustainability) of the Joint Research Centre (JRC) of the European Commission.</li>
<li>The ESDB data were developed in collaboration with the European Soil Bureau Network, which holds a joint copyright to the data with the European Commission. The DG-JRC, on behalf of the Commission, and the European Soil Bureau Network, does not accept any liability whatsoever for any error, missing data or omissions in the data, or for any loss or damage arising from its use. The DG JRC, on behalf of the Commission, agrees to provide the data free of charge but is not bound to justify the content and values contained in the databases.</li>
<li>The permission to use the data specified above is granted on condition that, under no circumstances are these data passed to third parties. Moreover they must not be used in any way for commercial gain or for purposes other than those specified above.</li>
<li>The user agrees to:<br />&nbsp;&nbsp;&nbsp;a) Make proper reference to the source of the data when disseminating the results to which this agreement relates;<br />&nbsp;&nbsp;&nbsp;b) Participate in the verification of the data (e.g. by noting and reporting any errors or omissions discovered to the JRC).</li>
</ol>
</div></div></div>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-entity-field pane-node-field-data-dataset-references"  >
  
        <h2 class="pane-title">
      Reference of source (Citations) :    </h2>
    
  
  <div class="pane-content">
    <div class="field field-name-field-data-dataset-references field-type-text-with-summary field-label-hidden"><div class="field-items"><div class="field-item even" property=""><ol>
<li>Panagos Panos. The European soil database (2006) GEO: connexion, 5 (7), pp. 32-33.</li>
<li>For ESDB v2.0: The European Soil Database distribution version 2.0, European Commission and the European Soil Bureau Network, CD-ROM, EUR 19945 EN, 2004.</li>
</ol>
<p align="justify">&nbsp;</p>
</div></div></div>  </div>

  
  </div>
<div class="panel-separator"></div><div class="panel-pane pane-custom pane-2"  >
  
        <h2 class="pane-title">
      When making reference to the ESDAC    </h2>
    
  
  <div class="pane-content">
    <ul>
<li>Panagos, P., Van Liedekerke, M., Borrelli, P., Köninger, J., Ballabio, C., Orgiazzi, A., Lugato, E., Liakos, L., Hervas, J., Jones, A.&nbsp; Montanarella, L. 2022. <a href="https://bsssjournals.onlinelibrary.wiley.com/doi/full/10.1111/ejss.13315" target="_blank">European Soil Data Centre 2.0: Soil data and knowledge in support of the EU policies</a>. European Journal of Soil Science, 73(6), e13315. DOI: 10.1111/ejss.13315</li>
<li>Panagos P., Van Liedekerke M., Jones A., Montanarella L., &ldquo;European Soil Data Centre: Response to European policy support and public data requirements&rdquo;; (2012) Land Use Policy, 29 (2), pp. 329-338. doi:10.1016/j.landusepol.2011.07.003</li>
<li>European Soil Data Centre (ESDAC), esdac.jrc.ec.europa.eu, European Commission, Joint Research Centre</li>
</ul>
  </div>

  
  </div>
  </div>
</div>
  </div>
</div>
</div>
</div>
</div></form>
</section> '''

s2 = BeautifulSoup(res, 'html.parser')

for t in s2.find_all("title"):
    ttl = t.text
for s in s2.find_all("section",{'id':'block-system-main'}):
    section = s.text

ds = {'relation':[],'subject':[],'source':[],'type':'Dataset','title':ttl}





for desc in s.find_all('div',{'property':"dct:description"}):
    ds['description'] = desc.text
for img in s.find_all('img',{'typeof':"foaf:Image"}):
    if not 'image_captcha' in img.get('src'):
        ds['thumbnailUrl'] = img.get('src')
for uc in s.find_all("div",{"class":"field-name-field-data-dataset-notification"}):
    ds['constraints'] = uc.text
for ref in s.find_all("div",{"class":"field-name-field-data-dataset-references"}):
    for ref2 in ref.find_all("li"):
        ds['source'].append(ref2.text)
for l in s.find_all('a',{'typeof':"skos:Concept"}):
    for kw in l.text.split('; '):
        ds['subject'].append(kw)
for dt in s.find_all("div",{"class":"field-name-field-data-publication-year"}):
    for d in dt.find_all("div",{"class":"field-item"}):
        ds['date'] = d.text
for ct in s.find_all("div",{"class":"field-name-field-data-publisher"}):
    for c in ct.find_all("div",{"class":"field-item"}):
        ds['publisher'] = c.text
print(ds)