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

    public static String urlGetSubObjCordisTitle = "https://sparql.soilwise-he.containers.wur.nl/sparql/?default-graph-uri=https%3A%2F%2Fsoilwise-he.github.io%2Fsoil-health&query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+datacite%3A+%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdatacite%2F%3E%0D%0Aselect+++%3Fsub+%3Fobj+%3Ftitle%0D%0AWHERE%0D%0A%7B%0D%0A%3Fsub+%3Fpred+%3Fobj.%0D%0A%3Fobj+dcterms%3Atitle+%3Ftitle.%0D%0AFILTER+regex%28%3Fpred+%2C+%22ProjectPublication%22%2C+%22i%22%29%0D%0A%7D%0D%0A&format=application%2Fsparql-results%2Bjson&timeout=0&signal_void=on";

//    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
//    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
//    PREFIX eurio:<http://data.europa.eu/s66#>
//    PREFIX dcterms: <http://purl.org/dc/terms/>
//    select   ?sub ?title
//        WHERE
//    {
//            ?sub ?pred ?obj.
//            ?sub dcterms:title ?title.
//            FILTER regex(?sub , "s66/resource/project", "i")
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
//                    JSONObject titleresult = new JSONObject(getHTTPResult(urlGetSubObjCordisTitle));
//
//                    System.out.println(dbwriter.setCordisProjectTitles(titleresult));
                    System.out.println("TODO: setCordisProjectTitles");
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
