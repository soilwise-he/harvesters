package nl.wur.wenr;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;

/**
 * Hello world!
 *
 */
public class DBWrite
{

    public static String urlGetSubObjDoiTitle = "https://sparql.soilwise-he.containers.wur.nl/sparql/?default-graph-uri=https%3A%2F%2Fsoilwise-he.github.io%2Fsoil-health&query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+datacite%3A+%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdatacite%2F%3E%0D%0Aselect+++%3Fsub+%3Fobj+%3Ftitle%0D%0AWHERE%0D%0A%7B%0D%0A%3Fsub+%3Fpred+%3Fobj.%0D%0A%3Fobj+dcterms%3Atitle+%3Ftitle.%0D%0AFILTER+regex%28%3Fpred+%2C+%22ProjectPublication%22%2C+%22i%22%29%0D%0A%7D%0D%0A&format=application%2Fsparql-results%2Bjson&timeout=0&signal_void=on";
// Query our Virtuoso
//    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
//    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
//    PREFIX eurio:<http://data.europa.eu/s66#>
//    PREFIX dcterms: <http://purl.org/dc/terms/>
//    PREFIX datacite: <http://purl.org/spar/datacite/>
//    select   ?sub ?obj ?title
//    WHERE
//    {
//            ?sub ?pred ?obj.
//            ?obj dcterms:title ?title.
//            FILTER regex(?pred , "ProjectPublication", "i")
//    }

   public static String urlGetSubObjCordisTitle = "https://cordis.europa.eu/datalab/sparql?query=PREFIX%20eurio%3A%20%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0ACONSTRUCT%20%7B%0A%20%20%3FidentifierURI%20dcterms%3Atitle%20%3Ftitle%0A%7D%0AWHERE%0A%7B%0A%20%20%3Fproject%20a%20eurio%3AProject.%0A%20%20%3Fproject%20eurio%3Atitle%20%3Ftitle.%0A%20%20%3Fproject%20eurio%3Aabstract%20%3Fabstract.%0A%20%20%3Fproject%20eurio%3Aidentifier%20%3Fidentifier.%0A%20%20BIND%28IRI%28CONCAT%28%22https%3A%2F%2Fcordis.europa.eu%2Fproject%2Fid%2F%22%2C%20%3Fidentifier%29%29%20AS%20%3FidentifierURI%29.%0A%20%20%3Fproject%20eurio%3AhasResult%20%3Fresult.%0A%20%20%3Fresult%20rdf%3Atype%20%3Ftype.%0A%20%20optional%20%7B%20%3Fresult%20eurio%3Adoi%20%3Fdoi%20%7D%20.%0A%20%20%3Fresult%20eurio%3Atitle%20%3Frestitle.%0A%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AProjectPublication%29%0A%23%20%20FILTER%20regex%28%3Ftype%2C%20eurio%3AJournalPaper%29%0A%20%20FILTER%20%28%28regex%28%3Fabstract%2C%20%22Soil%22%2C%20%22i%22%29%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%22676982%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%7C%7C%20%28%3Fidentifier%20%3D%20%22867468%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%29%20%7C%7C%20%28%3Fidentifier%20%3D%20%20%22101006717%22%5E%5E%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23Literal%3E%20%29%29%0A}&format=application%2Fsparql-results%2Bjson&timeout=0&signal_void=on";
// Query Cordis
//PREFIX eurio: <http://data.europa.eu/s66#>
//    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
//    PREFIX dcterms: <http://purl.org/dc/terms/>
//    CONSTRUCT {
//  ?project dcterms:title ?title
//    }
//    WHERE
//    {
//  ?project a eurio:Project.
//            ?project eurio:title ?title.
//            ?project eurio:url ?url.
//            ?project eurio:abstract ?abstract.
//  ?project eurio:identifier ?identifier.
//            ?project eurio:hasResult ?result.
//            ?result rdf:type ?type.
//            optional { ?result eurio:doi ?doi } .
//  ?result eurio:title ?restitle.
//            FILTER regex(?type, eurio:ProjectPublication)
//        FILTER regex(?abstract, "Soil", "i")
//    }


    public static int loglevel = 1;

    // public static String predicate = "";
// ALL:

    public static void main( String[] args )
    {

        System.out.println("args.length: " + args.length) ;

        if(args.length > 0) {
            try {
                DBWriter dbwriter = new DBWriter();

                if (args[0].equalsIgnoreCase("updatecordis")) {

                    System.out.println(args[0]);
                    System.out.println("Update count: " + dbwriter.queryDOIsCORDIS());

                }  if (args[0].equalsIgnoreCase("openairedoi")) {

                    System.out.println("DOI count: " + dbwriter.queryDOIsOpenAire());

                } else if (args[0].equalsIgnoreCase("turtle")) {

                    System.out.println("Turtle count: " + dbwriter.turtleDOIs());

                } else if (args[0].equalsIgnoreCase("cordis")) {

                    JSONObject doiresult = new JSONObject(getHTTPResult(urlGetSubObjDoiTitle));

                    System.out.println(dbwriter.loadDOIsCordis(doiresult));
                }
//            else if (args[0].equalsIgnoreCase("hash") ) {
//
//                System.out.println(dbwriter.hashDOIs() );
//            }
                else if (args[0].equalsIgnoreCase("title")) {
                    JSONObject titleresult = new JSONObject(getHTTPResult(urlGetSubObjCordisTitle));

                    System.out.println(dbwriter.setCordisProjectTitles(titleresult));

                }


            } catch (Exception e) {
                e.printStackTrace();
                System.out.println(e.getMessage());
            }
        }
        else {
            System.out.println("JAVA_HOME: " + System.getenv("JAVA_HOME"));
        }


    }

    public static String getHTTPResult(String urlString)  {
        // BY HTTP REQUESTS !
        String jsonstring = "";


        // String querystring = "" + URLEncoder.encode (jsonstring, StandardCharsets.UTF_8); ;

        String hostpath = "";

        try {
            URL url = new URL(urlString);

            if(loglevel >= 3) {
                System.out.println("Url: " + url);
            }

// Read all the text returned by the server
            BufferedReader in = new BufferedReader(new InputStreamReader(url.openStream()));
            String str;
            while ((str = in.readLine()) != null) {
                // str is one line of text; readLine() strips the newline character(s)
                jsonstring += str;
            }
            in.close();

            if(loglevel >= 4) {
                System.out.println("Get HTTP result: " + jsonstring);
            }

        }
        catch(Exception e) {

            jsonstring = null;
        }

        return jsonstring;
    }

}
