package nl.wur.wenr.xml;


import java.io.IOException;
import java.io.OutputStream;

public class StringOutputStream extends OutputStream {

    /**
     * where to output
     */
    StringBuffer buffer;

    /**
     * default constructor: to a string
     */
    public StringOutputStream() {
        buffer = new StringBuffer(2048);
    }

    /**
     * or fix the buffer size
     */
    public StringOutputStream(int size) {
        buffer = new StringBuffer(size);
    }

    /**
     * or takes the buffer directly
     */
    public StringOutputStream(StringBuffer buf) {
        if (buf != null)
            buffer = buf;
        else
            buffer = new StringBuffer(2048);
    }

    /**
     * implements the stream: writes the byte to the string buffer
     */
    public void write(int b) {
        buffer.append((char) b);
    }

    /**
     * returns the written string
     */
    public String toString() {
        return buffer.toString();
    }

    /**
     * forward StringBuffer functions
     */
    public int length() {
        return buffer.length();
    }

    public void setLength(int l) {
        buffer.setLength(l);
    }
}
