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

    public static String urlGetSubObjDoi = "https://sparql.soilwise-he.containers.wur.nl/sparql/?default-graph-uri=https%3A%2F%2Fsoilwise-he.github.io%2Fsoil-health&query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0ASELECT+%3Fsub+%3Fobj+WHERE+%7B%0D%0A++%3Fsub+%3Fpred+%3Fobj+.%0D%0AFILTER+regex%28%3Fpred%2C+%22ProjectPublication%22%2C+%22i%22%29%0D%0A%7D%0D%0A%0D%0A&format=application%2Fsparql-results%2Bjson&timeout=0&signal_void=on";
    // get Cordis DOIs from virtuoso
    public static String urlGetSubObjTitle = "https://sparql.soilwise-he.containers.wur.nl/sparql/?default-graph-uri=https%3A%2F%2Fsoilwise-he.github.io%2Fsoil-health&query=PREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20eurio%3A%3Chttp%3A%2F%2Fdata.europa.eu%2Fs66%23%3E%0APREFIX%20dcterms%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0APREFIX%20datacite%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fspar%2Fdatacite%2F%3E%0Aselect%20%20%20%3Fsub%20%3Fpred%20%3Fobj%0AWHERE%20%7B%0A%20%20%3Fsub%20%3Fpred%20%3Fobj%0AFILTER%20(%3Fpred%3D%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2Ftitle%3E)%0A%7D&&format=application%2Fsparql-results%2Bjson&timeout=0&signal_void=on";
    // get Cordis titles from virtuoso, BOTH projects and projectPublications (results)

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

                    JSONObject doiresult = new JSONObject(getHTTPResult(urlGetSubObjDoi));

                    System.out.println(dbwriter.loadDOIs(doiresult));
                }
//            else if (args[0].equalsIgnoreCase("hash") ) {
//
//                System.out.println(dbwriter.hashDOIs() );
//            }
                else if (args[0].equalsIgnoreCase("title")) {
                    JSONObject titleresult = new JSONObject(getHTTPResult(urlGetSubObjTitle));

                    System.out.println(dbwriter.setTitles(titleresult));
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
