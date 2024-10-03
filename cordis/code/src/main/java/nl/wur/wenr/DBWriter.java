package nl.wur.wenr;

import nl.wur.wenr.persistency.DBConnection;
import nl.wur.wenr.persistency.WrapResultSet;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.FileWriter;
import java.sql.Connection;
import java.sql.SQLException;


public class DBWriter {
    String result;
    private String eurioIndentifier;

    private DBConnection db;

    private Connection con;
    private String doiURI;
    FileWriter fw ;

    public DBWriter() throws Exception {
        //DBConnection.setupDatabaseParameters("virtuoso.jdbc4.Driver", "dba", "secret", "jdbc:virtuoso://localhost:1111");
        String username = System.getenv("POSTGRES_USERNAME");
        if(username == null || username.length()==0) {
            username = "XXXX" ;
        }
        String password = System.getenv("POSTGRES_PASSWORD");
        if(password == null || password.length()==0) {
            password = "XXXX" ;
        }
        String connecturi = System.getenv("POSTGRES_DB");
        if(connecturi == null || connecturi.length()==0) {
            connecturi = "jdbc:postgresql://host:port/database?currentschema=harvester" ; 
        }
        DBConnection.setupDatabaseParameters("org.postgresql.Driver", username, password, connecturi);
        db = DBConnection.instance();

    }

    public int setTitles(JSONObject identifierlist) throws Exception {
        int ret = 0;

        JSONArray bindingsarray = identifierlist.getJSONObject("results").getJSONArray("bindings");

        if (bindingsarray != null) {


            result = "";
            try {
                try {
                    con = db.getConnection();

                    for (int i = 0; i < bindingsarray.length(); i++) {


                        eurioIndentifier = bindingsarray.getJSONObject(i).getJSONObject("sub").getString("value");
                        String objResult =  bindingsarray.getJSONObject(i).getJSONObject("obj").getString("value");


                        if(eurioIndentifier.contains("s66/resource/result") ) {
                        // the project publication is allready there
                            String resultobject= db.executeStringResultStatement(con, "select resultobject from harvest.items where uri = ? and itemtype= ? and source = ? "
                                    , new Object[] { eurioIndentifier, "publication", "CORDIS" } );
                            String hash = calculateMD5(resultobject + objResult.toLowerCase());

                            db.executeVoid(con, "update harvest.items set title = ?, hash = ? where uri = ? and itemtype= ? and source = ? "
                                    , new Object[] { objResult, hash, eurioIndentifier, "publication", "CORDIS" } );

                        }
                        else if(eurioIndentifier.contains("s66/resource/project") ) {
                        // the project could be new
                            long existing = db.executeLongResultStatement(con, "select count(*) from harvest.items where uri = ? and itemtype= ? and source = ? "
                                    , new Object[] { eurioIndentifier, "project", "CORDIS" } );

                            if( existing > 0 ) {
                                db.executeVoid(con, "update harvest.items set title = ? where uri = ? and itemtype= ? and source = ? "
                                        , new Object[]{objResult, eurioIndentifier, "project", "CORDIS"});
                            }
                            else {
                                db.executeVoid(con, "insert into harvest.items(identifier,  resultobject, title, uri, itemtype, insert_date, source, identifiertype) VALUES(?, ?, ?, ?, ?, now(), ?, ? ) "
                                        , new Object[] { eurioIndentifier.substring( eurioIndentifier.lastIndexOf('/')+1 ), "", objResult, eurioIndentifier, "project", "CORDIS", "cordis" } );

                                ret += 1;

                            }

                        }


                        if (DBWrite.loglevel >= 1 && (i % 100 == 0)) {
                            System.out.println(i);
                        }
                    }

                } catch (Exception e) {
                    System.out.println(e.getMessage());
                }
            } finally {
                if (!con.isClosed()) {
                    con.close();
                }
            }
        }

        if (DBWrite.loglevel >= 4) {
            System.out.println(result);
        }

        return ret; // bindingsarray.length();
    }

    public int loadDOIs(JSONObject doilist) throws Exception {
        int ret = 1;

        JSONArray bindingsarray = doilist.getJSONObject("results").getJSONArray("bindings");

        if (bindingsarray != null) {


            result = "";
            try {
                try {
                    con = db.getConnection();

                    for (int i = 0; i < bindingsarray.length(); i++) {

//                        if ((i >= (pageSize * (pageNum - 1))) && (i < (pageSize * pageNum))) {
                            eurioIndentifier = bindingsarray.getJSONObject(i).getJSONObject("obj").getString("value");
                            loadOneDOI(
                                    bindingsarray.getJSONObject(i).getJSONObject("sub").getString("value"));


//                        }
                        if (DBWrite.loglevel >= 1 && (i % 100 == 0)) {
                            System.out.println(i);
                        }

                    }

                } catch (Exception e) {
                    System.out.println(e.getMessage());
                }
            } finally {
                if (!con.isClosed()) {
                    con.close();
                }
            }
        }

        if (DBWrite.loglevel >= 4) {
            System.out.println(result);
        }

        return bindingsarray.length();
    }

    private void loadOneDOI(String doi_uri)  {
//        String do_these_dois = "@10.1029/2019jg005511#@10.1038/s41467-019-13361-5#@10.5281/zenodo.6913303#@10.5281/zenodo.6912948#@10.5281/zenodo.6907266#@10.1016/j.agee.2022.107867#@10.1016/j.biocon.2022.109475#@10.1016/j.agsy.2021.103251#@10.5281/zenodo.6918749#@10.5281/zenodo.6921427#@10.5281/zenodo.6907243#@10.5281/zenodo.4884673#@10.5281/zenodo.6907367#@10.5281/zenodo.6921248#@10.5281/zenodo.6921102#@10.5281/zenodo.6912908#@10.5281/zenodo.6921504#@10.5281/zenodo.6913278#@10.5281/zenodo.6918597#@10.5281/zenodo.6922621#@10.5281/zenodo.6921010#@10.5281/zenodo.6920909#@10.5281/zenodo.6907391#@10.5281/zenodo.6923496#@10.5281/zenodo.6918779#@10.3390/agronomy10101535#@10.5281/zenodo.6907313#@10.5281/zenodo.6920841#@10.5281/zenodo.6907365#@10.5281/zenodo.6907081#@10.5281/zenodo.6907345#@10.5281/zenodo.6906867#@10.5281/zenodo.6907562#@10.5281/zenodo.6918843#@10.5281/zenodo.6921607#@10.1016/j.csbj.2021.04.023#@10.1039/d2np00011c#@10.1080/17445647.2022.2088305#@10.1038/s41598-023-31334-z#@10.12688/openreseurope.13135.2#@10.3390/en15072683#";
//
//        if(do_these_dois.contains("@" + doi + "#")) {
            String doi = doi_uri.replace("https://doi.org/","");
             String requestOpenaire = "https://api.openaire.eu/search/researchProducts?format=json&doi=" + doi;

            String openAireObjectValue;

            if (DBWrite.loglevel >= 3) {

                System.out.println("Query openaire for subj: " + eurioIndentifier + ". Request: " + requestOpenaire);
            }

            String opaire = DBWrite.getHTTPResult(requestOpenaire);


        try {  // add record if needed

            long existing = db.executeLongResultStatement(con, "select count(*) from harvest.items where uri = ? and itemtype= ? and source = ? "
                    , new Object[] { eurioIndentifier, "publication", "CORDIS" } );

            if( existing == 0 ) {

                db.executeVoid(con, "insert into harvest.items(identifier, resultobject, uri, itemtype, insert_date, source, identifiertype, resulttype) VALUES(?, ?, ?, ?, now(), ?,?, ? ) "
                        , new Object[]{ eurioIndentifier.substring(eurioIndentifier.lastIndexOf('/') + 1), doi, eurioIndentifier, "publication", "CORDIS", "cordis", "doi"});
            }
            //System.out.println(eurioIndentifier.substring( eurioIndentifier.lastIndexOf('/')+1 ));
        }

        catch(Exception e) {
            System.out.println(e.getMessage());
        }

            if (opaire != null) {

                JSONObject openaireresult = new JSONObject(opaire);

                if (DBWrite.loglevel >= 4) {

                    System.out.println("With request: " + openaireresult.toString());
                }

                JSONObject resultsObj = openaireresult.getJSONObject("response").optJSONObject("results");
                if (resultsObj != null && !JSONObject.NULL.equals(resultsObj)) {
                    JSONObject oafresult = resultsObj.getJSONArray("result").getJSONObject(0)
                            .getJSONObject("metadata")
                            .getJSONObject("oaf:entity")
                            .getJSONObject("oaf:result");



                    if (DBWrite.loglevel >= 4) {
                        System.out.println(oafresult);
                    }
                    try {  // REPLACE

                        db.executeVoid(con, "update harvest.items set identifier=?, resultobject=?, itemtype=?, identifiertype=?, resulttype=? where uri=? "
                                , new Object[] { doi, oafresult, "publication", "doi", "oaf", eurioIndentifier } );

                    }
                    catch(Exception e) {
                        System.out.println(e.getMessage());
                    }

                }
            }
//        }
    }


    public long queryDOIsOpenAire()  {
        long cnt = 0;

        cnt = queryDOIs("select uri, identifier as doi, source from harvest.items where turtle IS NULL and resulttype != 'oaf' and identifiertype = ?"
                , new Object[] {  "doi" } );
        return cnt;
    }

    public long queryDOIsCORDIS()  {
        long cnt = 0;

        cnt = queryDOIs("select uri, resultobject as doi, source from harvest.items where upper(source) = ? and resulttype = ?"
                , new Object[] {  "CORDIS", "doi" } );

        return cnt;
    }

    public long queryDOIs(String statement, Object[] parameters)  {
        // enrich from OpenAire
        long cnt = 0;
        try {


            WrapResultSet rs= db.executeQuery( statement, parameters );

            con = db.getConnection();

            try {
                while (rs.next()) {

                    result = "";
                    String doi = rs.getString("doi");
                    String uri = rs.getString("uri");
                    String source = rs.getString("source");

                    queryOneDOI(source, uri, doi);

                    cnt++;

                    if (DBWrite.loglevel >= 1 && (cnt % 100 == 0)) {
                        System.out.println(cnt);
                    }
                }
            }
            finally {
                rs.close();
            }
        }
        catch(Exception e) {
            System.out.println(e.getMessage());

        }

        return cnt;

    }

    private void queryOneDOI(String source, String uri, String doi)  {
//        String do_these_dois = "@10.1029/2019jg005511#@10.1038/s41467-019-13361-5#@10.5281/zenodo.6913303#@10.5281/zenodo.6912948#@10.5281/zenodo.6907266#@10.1016/j.agee.2022.107867#@10.1016/j.biocon.2022.109475#@10.1016/j.agsy.2021.103251#@10.5281/zenodo.6918749#@10.5281/zenodo.6921427#@10.5281/zenodo.6907243#@10.5281/zenodo.4884673#@10.5281/zenodo.6907367#@10.5281/zenodo.6921248#@10.5281/zenodo.6921102#@10.5281/zenodo.6912908#@10.5281/zenodo.6921504#@10.5281/zenodo.6913278#@10.5281/zenodo.6918597#@10.5281/zenodo.6922621#@10.5281/zenodo.6921010#@10.5281/zenodo.6920909#@10.5281/zenodo.6907391#@10.5281/zenodo.6923496#@10.5281/zenodo.6918779#@10.3390/agronomy10101535#@10.5281/zenodo.6907313#@10.5281/zenodo.6920841#@10.5281/zenodo.6907365#@10.5281/zenodo.6907081#@10.5281/zenodo.6907345#@10.5281/zenodo.6906867#@10.5281/zenodo.6907562#@10.5281/zenodo.6918843#@10.5281/zenodo.6921607#@10.1016/j.csbj.2021.04.023#@10.1039/d2np00011c#@10.1080/17445647.2022.2088305#@10.1038/s41598-023-31334-z#@10.12688/openreseurope.13135.2#@10.3390/en15072683#";
//
//        if(do_these_dois.contains("@" + doi + "#")) {
        String requestOpenaire = "https://api.openaire.eu/search/researchProducts?format=json&doi=" + doi;

        String openAireObjectValue;

        if (DBWrite.loglevel >= 2) {

            System.out.println("Query openaire for subj: " + uri + ". Request: " + requestOpenaire);
        }

        String opaire = DBWrite.getHTTPResult(requestOpenaire);

//        try {  // replace existing record
//            db.executeVoid(con, "delete from harvest.items where uri=? and source=? "
//                    , new Object[] { eurioIndentifier, "CORDIS" } );
//
//
//            db.executeVoid(con, "insert into harvest.items(identifier, resultobject, uri, itemtype, insert_date, source, identifiertype, resulttype) VALUES(?, ?, ?, ?, now(), ?,?, ? ) "
//                    , new Object[] { eurioIndentifier.substring( eurioIndentifier.lastIndexOf('/')+1 ), doi,  eurioIndentifier, "publication", "CORDIS", "cordis", "doi" } );
//            //System.out.println(eurioIndentifier.substring( eurioIndentifier.lastIndexOf('/')+1 ));
//        }
//
//        catch(Exception e) {
//            System.out.println(e.getMessage());
//        }

        if (opaire != null) {

            if (DBWrite.loglevel >= 2) {

                System.out.println("Length openaireresult: " + opaire.length());
            }

            JSONObject openaireresult = new JSONObject(opaire);

            if (DBWrite.loglevel >= 4) {

                System.out.println("With result: " + openaireresult.toString());
            }

            JSONObject resultsObj = openaireresult.getJSONObject("response").optJSONObject("results");
            if (resultsObj != null && !JSONObject.NULL.equals(resultsObj)) {
                JSONObject oafresult = resultsObj.getJSONArray("result").getJSONObject(0)
                        .getJSONObject("metadata")
                        .getJSONObject("oaf:entity")
                        .getJSONObject("oaf:result");



                if (DBWrite.loglevel >= 4) {
                    System.out.println(oafresult);
                }
                try {  // REPLACE
                    db.executeVoid(con, "update harvest.items set identifier=?, resultobject=?, identifiertype=?, resulttype=?, turtle=NULL where uri=? and source=? "
                            , new Object[] { doi, oafresult, "doi", "oaf", uri, source } );

                }
                catch(Exception e) {
                    System.out.println(e.getMessage());
                }

            }
        }
//        }
    }
//    public long hashDOIs()  {
//        long cnt = 0;
//        try {
//
//
//            WrapResultSet rs= db.executeQuery( "select identifier, identifiertype, resultobject, title, hash from harvest.items where upper(source) = ? and resulttype = ?", new Object[] {  "CORDIS", "oaf" }  );
//
//            con = db.getConnection();
//            db.executeVoid(con, "delete from harvest.item_duplicates where upper(source) = ?", new Object[] { "CORDIS" });
//
//            try {
//                int i = 0;
//                while (rs.next()) {
//
//                    result = "";
//                    String doi = rs.getString("identifier");
//                    String idtype = rs.getString("identifiertype");
//                    String oldhash = rs.getString("hash");
//                    String newhash = calculateMD5(rs.getString("resultobject")+rs.getString("title").toLowerCase()) ;  // +rs.getString("title").toLowerCase()
//
//                    if(newhash != null && (oldhash == null || ! oldhash.equalsIgnoreCase(newhash))) {
//
//                        try {
//
//                            db.executeVoid(con, "update harvest.items set hash = ? where identifier = ? and upper(source) = ? and resulttype = ?", new Object[] {newhash, doi, "CORDIS", "oaf"});
//
//                        }
//                        catch (Exception e) {
//                            db.executeVoid(con, "update harvest.items set hash = NULL where identifier = ? and upper(source) = ? and resulttype = ?", new Object[] {doi, "CORDIS", "oaf"});
//                            db.executeVoid(con, "INSERT INTO harvest.cordis_duplicates select * from (identifier, identifiertype, source, hash) VALUES(?, ?, ?, ?)", new Object[] {doi, idtype, "CORDIS", newhash });
//
//                        }
//                    }
//                    i++;
//
//                    if (DBWrite.loglevel >= 1 && (i % 100 == 0)) {
//                        System.out.println(i);
//                    }
//                }
//                cnt = i;
//            }
//            finally {
//                rs.close();
//            }
//        }
//        catch(Exception e) {
//            System.out.println(e.getMessage());
//
//        }
//
//        return cnt;
//
//    }

public long turtleDOIs()  {
    long cnt = 0;
    try {
//            writeHeaderURI("<http://data.europa.eu/s66#>");
//            writeHeaderLiteral("<http://purl.org/dc/terms/>");

            WrapResultSet rs= db.executeQuery( "select identifier, resultobject, source from harvest.items where turtle IS NULL and resulttype = ?"
                    , new Object[] {  "oaf" }  );

            con = db.getConnection();

            try {
                int i = 0;
                while (rs.next()) {

                     result = "";
                     String doi = rs.getString("identifier");
                     doiURI = "https://doi.org/" + doi;
                     String source = rs.getString("source");

                     cnt += turtleOneDOI(source, doi, rs.getString("resultobject"));
                     // handleOneDOI fills result with turtle-lines

                    db.executeVoid(con, "update harvest.items set turtle = ? where identifier = ? and upper(source) = ? and resulttype = ?", new Object[] { result, doi,  source, "oaf" }  );

                     i++;

                    if (DBWrite.loglevel >= 1 && (i % 100 == 0)) {
                        System.out.println(i);
                    }
                }

            }
            finally {
                rs.close();
            }
    }
    catch(Exception e) {
        System.out.println(e.getMessage());

    }

    return cnt;

}

    private String cleanValue(String value) {
        value = value.replace('\\',' ');
        value = value.replaceAll("[\\p{Cntrl}&&[^\r\n\t]]", "");
        value = value.replace('"','\'');
        //all non-ascii characters: value = value.replaceAll("[^\\x00-\\x7F]", "*");
        return value;
    }

    private int turtleOneDOI(String source, String doi, String oafresultstring)  {
        String resultString = "";
        String predicate ;
        int resultint = 0;
        if (oafresultstring != null && oafresultstring.length() > 0) {
            resultint = 1;
            JSONObject oafresult = new JSONObject(oafresultstring);

            predicate = "creator";
                // special handling because of ranking and @orcid

                if (oafresult.keySet().contains(predicate)) {
                    Object objPredicate = oafresult.get(predicate);

                    if (JSONObject.NULL.equals(objPredicate)) {
                        resultString = "";
                        writeTripleLiteral(doiURI, predicate, resultString);
                    } else if (objPredicate instanceof JSONObject) {

                        resultString = cleanValue(oafresult.getJSONObject(predicate).get("$").toString());
                        writeTripleLiteral(doiURI, predicate, resultString);
                        //writeTripleHTML(doiURI, App.predicate, openAireObjectValue);
                    } else if (objPredicate instanceof JSONArray) {
                        JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                        for (int i = 0; i < arrPredicate.length(); i++) {
                            String addString = cleanValue(arrPredicate.getJSONObject(i).get("$").toString());
                            String orcid="";
                            if (arrPredicate.getJSONObject(i).keySet().contains("@orcid")) {
                                orcid = arrPredicate.getJSONObject(i).get("@orcid").toString();
                            }
                            if (orcid != null && orcid.length() > 0 ) {
                            // separate entries for every orcid
                                writeTripleLiteral(doiURI, predicate, "https://orcid.org/" + orcid);
                            }
                            String rank = "0";
                            if (arrPredicate.getJSONObject(i).keySet().contains("@rank")) {
                                rank = arrPredicate.getJSONObject(i).get("@rank").toString();
                            }
                            if (rank.equals("1")) {
                                // first authors in front
                                resultString = addString + ", " + resultString;
                            } else {
                                resultString = resultString + addString + ", ";
                            }
                        }
                        // outside for-loop: one element with all authors listed
                        writeTripleLiteral(doiURI, predicate, resultString);
                    }
                }
            predicate = "collectedfrom";
                // special handling because of multiple separate entrances
            writeTripleLiteral(doiURI, "isReferencedBy", source);
            writeTripleLiteral(doiURI, "isReferencedBy", "OpenAire");
                if (oafresult.keySet().contains(predicate)) {
                    Object objPredicate = oafresult.get(predicate);

                    if (JSONObject.NULL.equals(objPredicate)) {
                        resultString = "";
                        writeTripleLiteral(doiURI, "isReferencedBy", resultString);
                    } else if (objPredicate instanceof JSONObject) {

                        resultString = cleanValue(oafresult.getJSONObject(predicate).get("@name").toString());
                        writeTripleLiteral(doiURI, "isReferencedBy", resultString);
                    } else if (objPredicate instanceof JSONArray) {
                        JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                        for (int i = 0; i < arrPredicate.length(); i++) {
                            // write separate Turtle for every element
                            resultString = cleanValue(arrPredicate.getJSONObject(i).get("@name").toString());
                            writeTripleLiteral(doiURI, "isReferencedBy", resultString);
                        }

                    }
                }
            predicate = "journal";
            // special handling because of multiple separate entrances

            if (oafresult.keySet().contains(predicate)) {
                Object objPredicate = oafresult.get(predicate);

                if (JSONObject.NULL.equals(objPredicate)) {
                    resultString = "";
                    writeTripleLiteral(doiURI, "isPartOf", resultString);
                } else if (objPredicate instanceof JSONObject) {
                    String jrnl = "";
                    try {
                        jrnl = oafresult.getJSONObject(predicate).get("$").toString();
                    }
                    catch (Exception e) {
                        jrnl = "";
                    }
                    resultString = cleanValue(jrnl);
                    writeTripleLiteral(doiURI, "isPartOf", resultString);
                } else if (objPredicate instanceof JSONArray) {
                    JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                    for (int i = 0; i < arrPredicate.length(); i++) {
                        String jrnl = "";
                        try {
                            jrnl = arrPredicate.getJSONObject(i).get("$").toString();
                        }
                        catch (Exception e) {
                            jrnl = "";
                        }
                        resultString = cleanValue(jrnl);
                        // write separate Turtle for every element
                        resultString = cleanValue(jrnl);
                        writeTripleLiteral(doiURI, "isPartOf", resultString);
                    }

                }
            }
            predicate = "bestaccessright";
                // special handling because of multiple separate entrances

                if (oafresult.keySet().contains(predicate)) {
                    Object objPredicate = oafresult.get(predicate);

                    if (JSONObject.NULL.equals(objPredicate)) {
                        resultString = "";
                        writeTripleLiteral(doiURI, "license", resultString);
                    } else if (objPredicate instanceof JSONObject) {

                        resultString = cleanValue(resultString = oafresult.getJSONObject(predicate).get("@classname").toString());
                        writeTripleLiteral(doiURI, "license", resultString);
                    } else if (objPredicate instanceof JSONArray) {
                        JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                        for (int i = 0; i < arrPredicate.length(); i++) {
                            // write separate Turtle for every element
                            resultString = cleanValue(arrPredicate.getJSONObject(i).get("@classname").toString());
                            writeTripleLiteral(doiURI, "license", resultString);
                        }

                    }
                }
            predicate = "description";
                // concatenated multiple descriptions
                if (oafresult.keySet().contains(predicate)) {
                    Object objPredicate = oafresult.get(predicate);

                    if (JSONObject.NULL.equals(objPredicate)) {
                        resultString = "";
                        writeTripleLiteral(doiURI, predicate, resultString);
                    } else if (objPredicate instanceof JSONObject) {

                        resultString = cleanValue(oafresult.getJSONObject(predicate).get("$").toString());
                        writeTripleLiteral(doiURI, predicate, resultString.replace('"','\''));
                    } else if (objPredicate instanceof JSONArray) {
                        JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                        for (int i = 0; i < arrPredicate.length(); i++) {
                            // write separate Turtle for every element
                            resultString = resultString + cleanValue(arrPredicate.getJSONObject(i).get("$").toString()) + " ";
                            writeTripleLiteral(doiURI, predicate, resultString.replace('"','\''));
                        }
                    }
                }
            predicate = "subject";
                if (oafresult.keySet().contains(predicate)) {
                    Object objPredicate = oafresult.get(predicate);

                    if (JSONObject.NULL.equals(objPredicate)) {
                        resultString = "";
                        writeTripleLiteral(doiURI, predicate, resultString);
                    } else if (objPredicate instanceof JSONObject) {

                        JSONObject resultObj = oafresult.getJSONObject(predicate);
                        if (resultObj != null  && resultObj.has("$") ) {
                            resultString = cleanValue(resultObj.get("$").toString());
                            writeTripleLiteral(doiURI, predicate, resultString);
                        }
                    } else if (objPredicate instanceof JSONArray) {
                        JSONArray arrPredicate = oafresult.getJSONArray(predicate);
                        for (int i = 0; i < arrPredicate.length(); i++) {
                            // inside for-loop: write separate Turtle for every element
                            JSONObject jsonObj = arrPredicate.getJSONObject(i);
                            if (jsonObj != null && jsonObj.has("$")) {
                                resultString = cleanValue(jsonObj.get("$").toString());
                                writeTripleLiteral(doiURI, predicate, resultString);
                            }
                        }
                    }
                }
            }
        return resultint;
    }

    private String calculateMD5(String inmd5) {
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5");
            byte[] array = md.digest(inmd5.getBytes());
            StringBuffer sb = new StringBuffer();
            for (int i = 0; i < array.length; ++i) {
                sb.append(Integer.toHexString((array[i] & 0xFF) | 0x100).substring(1,3));
            }
            return sb.toString();
        } catch (java.security.NoSuchAlgorithmException e) {
        }
        return null;
    }

    private void writeHeaderLiteral(String url) {
        result += "@prefix dct:	" +  url  + " .\n" ;
    }

    private void writeTripleLiteral(String sub, String pred, String obj) {
        // replace " by ' in content ?
        // String subId = sub.substring( sub.lastIndexOf('/')+1 ) ;

        result +=  "<" + sub + ">	dct:" + pred  + "	\"" + obj + "\" .\n";
    }

    private void writeHeaderURI(String url) {
        result += "@prefix eurio:	" +  url  + " .\n" ;
    }
    private void writeTripleURI(String sub, String pred, String obj) {
        // replace " by ' in content ?
        // String subId = sub.substring( sub.lastIndexOf('/')+1 ) ;

        result +=  "<" + sub + ">	eurio:" + pred  + "	<" + obj + "> .\n";
    }

    private void writeFooterTurtle() {
    }
}
