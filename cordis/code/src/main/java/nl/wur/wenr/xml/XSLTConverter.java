package nl.wur.wenr.xml;


import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.StringReader;
import java.net.URL;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;

import javax.xml.transform.TransformerConfigurationException;
import javax.xml.transform.TransformerException;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

public class XSLTConverter  {

    // Global value so it can be ref'd by the tree-adapter
    // static Document document;

    private static DocumentBuilder builder;

    public XSLTConverter() throws Exception {
        super();

        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

        builder = factory.newDocumentBuilder();
    }

    /**
     * Create a DOM document from an XML string
     * @param aXMLString
     * @return Document
     * @throws ParserConfigurationException
     * @throws SAXException
     * @throws IOException
     */
    protected static Document createDOMDocument(String aXMLString) throws ParserConfigurationException, SAXException, IOException {
        Document document = builder.parse(new InputSource(new StringReader(aXMLString)));
        return document;
    }

    public String transformXSLTFromString(String aXMLInputString, String aXSLTStyleSheet) throws Exception {

        ByteArrayInputStream stylesheet = new ByteArrayInputStream(aXSLTStyleSheet.getBytes("UTF-8"));
        StreamSource source = new StreamSource(	stylesheet ) ;
        return transform(aXMLInputString, source);
    }

    public String transformXSLTFromFile(String aXMLInputString, String aXSLTStyleSheetFileName) throws Exception {

        File stylesheet = new File(aXSLTStyleSheetFileName);
        StreamSource source = new StreamSource(stylesheet);
        return transform(aXMLInputString, source);
    }

    public String transformXSLTFromURL(String aXMLInputString, String aXSLTStyleSheetURL) throws Exception {

        URL stylesheet = new URL(aXSLTStyleSheetURL);
        StreamSource source = new StreamSource( new InputStreamReader(stylesheet.openStream()) );
        return transform(aXMLInputString, source);
    }

    public String transform(String aXMLInputString, StreamSource aXSLTStreamSource) throws Exception {

        String result = "";

        try {
            Document document = createDOMDocument(aXMLInputString);

            // Use a Transformer for output
            TransformerFactory tFactory = TransformerFactory.newInstance();
            Transformer transformer = tFactory.newTransformer(aXSLTStreamSource);

            OutputStream outputstream = new StringOutputStream();

            DOMSource source = new DOMSource(document);
            StreamResult streamResult = new StreamResult(outputstream);
            transformer.transform(source, streamResult);

            result = outputstream.toString();

        } catch (TransformerConfigurationException tce) {
            // Error generated by the parser
            System.out.println("\n** Transformer Factory error");
            System.out.println("   " + tce.getMessage());

            // Use the contained exception, if any
            Throwable x = tce;
            if (tce.getException() != null)
                x = tce.getException();
            x.printStackTrace();

        } catch (TransformerException te) {
            // Error generated by the parser
            System.out.println("\n** Transformation error");
            System.out.println("   " + te.getMessage());

            // Use the contained exception, if any
            Throwable x = te;
            if (te.getException() != null)
                x = te.getException();
            x.printStackTrace();

        } catch (SAXException sxe) {
            // Error generated by this application
            // (or a parser-initialization error)
            Exception x = sxe;
            if (sxe.getException() != null)
                x = sxe.getException();
            x.printStackTrace();

        } catch (ParserConfigurationException pce) {
            // Parser with specified options can't be built
            pce.printStackTrace();

        } catch (IOException ioe) {
            // I/O error
            ioe.printStackTrace();
        }

        return result;
    }

}

