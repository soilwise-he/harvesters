package nl.wur.wenr.persistency;

import java.sql.*;

public class WrapResultSet {

	private ResultSet resultset;
	
	private Connection connection;
	
	public boolean next() throws SQLException {
		return resultset.next();
	}
	
	public boolean isLast() throws SQLException {
		return resultset.isLast();
	}
	
	public boolean isFirst() throws SQLException {
		return resultset.isFirst();
	}
	
	public Clob getClob(String aFieldName) throws Exception {
		return resultset.getClob(aFieldName);
	}

	public Clob getClob(int aIndex) throws Exception {
		return resultset.getClob(aIndex);
	}
	
	public Date getDate(String aFieldName) throws Exception {
		return resultset.getDate(aFieldName);
	}

	public Date getDate(int aIndex) throws Exception {
		return resultset.getDate(aIndex);
	}
	
	public Timestamp getTimestamp(String aFieldName) throws Exception {
		return resultset.getTimestamp(aFieldName);
	}

	public Timestamp getTimestamp(int aIndex) throws Exception {
		return resultset.getTimestamp(aIndex);
	}
	
	public Object getObject(String aFieldName) throws Exception {
		return resultset.getObject(aFieldName) ;
	}
	
	public Object getObject(int aColumnIndex) throws Exception {
		return resultset.getObject(aColumnIndex) ;
	}
	
	public String getString(String aFieldName) throws Exception {
		return resultset.getString(aFieldName);
	}

	public String getString(int aIndex) throws Exception {
		return resultset.getString(aIndex);
	}

	public String getColumnName(int aIndex) throws Exception {
		return resultset.getMetaData().getColumnName(aIndex);
	}

	public int getColumnType(int aIndex) throws Exception {
		return resultset.getMetaData().getColumnType(aIndex);
	}

	public double getDouble(String aFieldName) throws Exception {
		return resultset.getDouble(aFieldName);
	}

	public double getDouble(int i) throws Exception {
		return resultset.getDouble(i);
	}

	public double getFloat(String aFieldName) throws Exception {
		return resultset.getFloat(aFieldName);
	}

	public double getFloat(int i) throws Exception {
		return resultset.getFloat(i);
	}
	
	public int getByte(String aFieldName) throws Exception {
		return resultset.getByte(aFieldName);
	}
	
	public int getByte(int aColumnIndex) throws Exception {
		return resultset.getByte(aColumnIndex);
	}
	
	public int getInt(String aFieldName) throws Exception {
		return resultset.getInt(aFieldName);
	}
	
	public int getInt(int aColumnIndex) throws Exception {
		return resultset.getInt(aColumnIndex);
	}
	
	public int getNumber(String aFieldName) throws Exception {
		String s = resultset.getString(aFieldName);

		return Integer.parseInt(resultset.getString(aFieldName) ) ;
	}
	
	public int getNumber(int aColumnIndex) throws Exception {
		return Integer.parseInt(resultset.getString(aColumnIndex) ) ;
	}
	
	public long getLong(String aFieldName) throws Exception {
		return resultset.getLong(aFieldName);
	}
	
	public long getLong(int aColumnIndex) throws Exception {
		return resultset.getLong(aColumnIndex);
	}
	
	public int getColumnCount() throws Exception {
		return resultset.getMetaData().getColumnCount();
	}
	
	protected void finalize() throws Throwable {
		super.finalize();
		connection.close();
	}
	
	public void close() throws Exception {
		resultset.close();
		connection.close();
	}

	public Connection getConnection() {
		return connection;
	}

	public void setConnection(Connection connection) {
		this.connection = connection;
	}

	public ResultSet getResultset() {
		return resultset;
	}

	public void setResultset(ResultSet resultset) {
		this.resultset = resultset;
	}
}
