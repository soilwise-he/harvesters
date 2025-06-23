package nl.wur.wenr.persistency;

import org.apache.commons.dbcp.BasicDataSource;

import javax.sql.DataSource;
import java.sql.*;

public class DBConnection {
	
	public static Object[] noparameters = {}; 
	
	private static DataSource dataSource = null;

	protected static String databaseDriver;

	protected static String databaseURL;

	protected static String databasePassword;

	protected static String databaseUserName;

	public static DBConnection dbConnection;

	public DBConnection() throws Exception {
	}

	public static DBConnection instance() throws Exception {
		if (dbConnection == null) {
			dbConnection = new DBConnection();
			dbConnection.initConnectionCache();
		}

		return dbConnection;
	}

	public void initConnectionCache() throws Exception {
		if (dataSource != null) {
			shutdownDataSource(dataSource);

			dataSource = null;
		}

		dataSource = setupDataSource(this.databaseDriver,
				this.databaseUserName, this.databasePassword, this.databaseURL);

	}

	public static void setupDatabaseParameters(String driverClassName, String userName, String passWord, String connectURI) {
		DBConnection.databaseDriver = driverClassName;
		DBConnection.databaseUserName = userName;
		DBConnection.databasePassword = passWord;
		DBConnection.databaseURL = connectURI;
	}
	private static DataSource setupDataSource(String driverClassName, String userName, String passWord, String connectURI) {
		BasicDataSource ds = new BasicDataSource();

		ds.setDriverClassName(driverClassName);

		ds.setUsername(userName);

		ds.setPassword(passWord);

		ds.setUrl(connectURI);

		ds.setMaxActive(25); // was 100 op de scomp1270

		ds.setMaxIdle(25); // was 100 op de scomp1270

		return ds;
	}

	public static void logDataSourceStats() {
		BasicDataSource bds = (BasicDataSource) dataSource;
                
//		System.out.println("NumActive: " + bds.getNumActive());
//
//		System.out.println("NumIdle: " + bds.getNumIdle());
	}

	public static String getHostInfo() {
		BasicDataSource bds = (BasicDataSource) dataSource;
                
                return bds.getUrl();
	}

	private static void shutdownDataSource(DataSource ds) throws SQLException {
		BasicDataSource bds = (BasicDataSource) ds;

		bds.close();
	}

	public Connection getConnection() throws Exception {
		Connection con = dataSource.getConnection(); 
		// Check with a simple statement of connection is alive; if not reinitialize connection cache
		// con.isValid(5) doesn't work: raises a java.lang.AbstractMethodError:

		ResultSet rset = null ;
		try {
			try {
	    		Statement s = null;
	    		s = con.createStatement();
	    		// simple standard Oracle statement rset = s.executeQuery("SELECT sysdate FROM DUAL");
	    		// take an existing table: information_schema.tables; spatial_ref_sys comes with postgis
	    		rset = s.executeQuery("SELECT count(*) from DB.DBA.RDF_language"); // "SELECT count(*) FROM spatial_ref_sys where srid <1"
	
	    		if (rset.next()) {
	    			
	    			if(rset.getString(1) == null) {
	    				initConnectionCache();
	    				con = dataSource.getConnection();
	    			}
	    		}
	    		
	    		rset.close();
	    	}		
	    	catch(Exception e) {
	    		
				initConnectionCache();
				con = dataSource.getConnection(); 
	    	}
		} finally {
			if(rset != null ) {
				rset.close() ;
			}
		}
    	return con ;
	}

	public long executeLongResultStatement(Connection con, String statement, Object[] parameters)
			throws Exception {
		long result = 0;
		PreparedStatement ps = null;
		ResultSet rset = null;
		try {
			ps = con.prepareStatement(statement);

			for (int i = 0; i < parameters.length; i++) {
				// parameter binden
				bindParameter(ps, parameters[i], i);
			}

			rset = ps.executeQuery();

			if (rset.next()) {
				result = rset.getLong(1);
			}
		} finally {
			rset.close();
		}
		return result;
	}
	public String executeStringResultStatement(Connection con, String statement, Object[] parameters)
			throws Exception {
		String result = "";
		PreparedStatement ps = null;
		ResultSet rset = null;
		try {
			ps = con.prepareStatement(statement);

			for (int i = 0; i < parameters.length; i++) {
				// parameter binden
				bindParameter(ps, parameters[i], i);
			}

			rset = ps.executeQuery();

			if (rset.next()) {
				result = rset.getString(1);
			}
		} finally {
			rset.close();
		}
		return result;
	}

	public void executeVoid(Connection con, String aSQLStatement, Object[] parameters)
			throws Exception {
		PreparedStatement ps = null;
			try {
				ps = con.prepareStatement(aSQLStatement);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bindParameter(ps, parameters[i], i);
				}

				ps.executeUpdate();
				ps.close();

			}
			catch (SQLException se) {
				System.out.println("Error executing SQL statement: "
						+ se.getMessage());
				System.out.println("Error excuting SQL statement: "
						+ aSQLStatement + ".");
				throw new Exception("Database Error");
			}
		}

	public void executeUpdate(String aSQLStatement, Object[] parameters)
			throws Exception {
		PreparedStatement ps = null;
		Connection con = null;
		try {
			con = getConnection();
			try {
				ps = con.prepareStatement(aSQLStatement);			

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bindParameter(ps, parameters[i], i);
				}
				
                                ps.executeUpdate();
				
                                if ( !con.getAutoCommit() ) {
					con.commit();
				}
				ps.close();

			} 
			catch (SQLException se) {
				if ((con != null) && (!con.isClosed())) {
					if ( !con.getAutoCommit() ) {
						con.rollback();
					}
					con.close();
				}
                                System.out.println("Error executing SQL statement: "
                                                + se.getMessage());
                                System.out.println("Error excuting SQL statement: "
                                                + aSQLStatement + ".");
                                throw new Exception("Database Error");
			}
		} 
		finally {

			if ((con != null) && (!con.isClosed())) {
				con.close() ;
			}
		}
	}

	public void finalize() {
		// If garbage collected close any open connection
		try {
			if (dataSource != null) {
				shutdownDataSource(dataSource);
			}
		} catch (Exception e) {
			// Do nothing
		}
	}
	public WrapResultSet executeQuery(Connection con, String statement, Object[] parameters) throws Exception {
		PreparedStatement ps = null;
		ResultSet rset = null;
		WrapResultSet result = new WrapResultSet();
		try {
			ps = con.prepareStatement(statement);

			for (int i = 0; i < parameters.length; i++) {
				// parameter binden
				bindParameter(ps, parameters[i], i);
			}

			rset = ps.executeQuery();
			result.setConnection(con);
			result.setResultset(rset);

		} catch (SQLException se) {
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing statement " + statement + ".");
			throw new Exception("Database Error");
		}
		return result;
	}

	protected void bindParameter(PreparedStatement ps, Object parameter, int i) throws Exception {
		if (parameter == null) {
			ps.setNull(1 + i, Types.NULL);
		} else if (parameter.getClass() == String.class) {
			ps.setString(1 + i, (String) parameter);
		} else if (parameter.getClass() == Byte.class) {
			ps.setByte(1 + i, Byte.parseByte(parameter.toString()));
		} else if (parameter.getClass() == Integer.class) {
			ps.setInt(1 + i, Integer.parseInt(parameter.toString()));
		} else if (parameter.getClass() == Long.class) {
			ps.setLong(1 + i, Long.parseLong(parameter.toString()));
		} else if (parameter.getClass() == Float.class) {
			ps.setFloat(1 + i, Float.parseFloat(parameter.toString()));
		} else if (parameter.getClass() == Double.class) {
			ps.setDouble(1 + i, Double.parseDouble(parameter.toString()));
		} else if (parameter.getClass() == Timestamp.class) {
			ps.setTimestamp(1 + i, (Timestamp) parameter);
		} else { // assuming byte[]
			ps.setBytes(1 + i, (byte[]) parameter);
		}
	}

	protected void bind2Parameter(CallableStatement cs, Object parameter, int i)	throws Exception {
	// The first parameter is the output parameter; it has already been assigned
		if (parameter == null) {
			cs.setNull(2 + i, Types.NULL);
		} else if (parameter.getClass() == String.class) {
			cs.setString(2 + i, (String) parameter);
		} else if (parameter.getClass() == Byte.class) {
			cs.setByte(2 + i, Byte.parseByte(parameter.toString()));
		} else if (parameter.getClass() == Integer.class) {
			cs.setInt(2 + i, Integer.parseInt(parameter.toString()));
		} else if (parameter.getClass() == Long.class) {
			cs.setLong(2 + i, Long.parseLong(parameter.toString()));
		} else if (parameter.getClass() == Float.class) {
			cs.setFloat(2 + i, Float.parseFloat(parameter.toString()));
		} else if (parameter.getClass() == Double.class) {
			cs.setDouble(2 + i, Double.parseDouble(parameter.toString()));
		} else if (parameter.getClass() == Timestamp.class) {
			cs.setTimestamp(2 + i, (Timestamp) parameter);
		} else { // assuming byte[]
			cs.setBytes(2 + i, (byte[]) parameter);
		}
	}

	public String executeProcedure(String procedurename, Object[] parameters)
			throws Exception {
		String resultString = "";
		Connection con = null;
		String stmt = "{? = call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			try {
				CallableStatement cs = con.prepareCall(stmt);
				cs.registerOutParameter(1, Types.VARCHAR);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bind2Parameter(cs, parameters[i], i);
				}

				cs.execute();

				resultString = cs.getString(1);
				cs.close();
				// DEBUG: System.out.println(resultString);
			} finally {
				con.close();
			}
		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return resultString;
	}

	public void executeVoidProcedure(String procedurename, Object[] parameters)
			throws Exception {
		Connection con = null;
		String stmt = "{call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			try {
				CallableStatement cs = con.prepareCall(stmt);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bindParameter(cs, parameters[i], i);
				}

				cs.execute();
				
				cs.close();
				// DEBUG: System.out.println(resultString);
			} finally {
				con.close();
			}
		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return ;
	}

	public long executeLongProcedure(String procedurename, Object[] parameters)
			throws Exception {
		long result = 0l;
		Connection con = null;
		String stmt = "{? = call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			try {
				CallableStatement cs = con.prepareCall(stmt);
				cs.registerOutParameter(1, Types.BIGINT);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bind2Parameter(cs, parameters[i], i);
				}

				cs.execute();

				result = cs.getLong(1);
				cs.close();
				// DEBUG: System.out.println(resultString);
			} finally {
				con.close();
			}
		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return result;
	}

public int executeIntProcedure(String procedurename, Object[] parameters)
			throws Exception {
		int result = 0;
		Connection con = null;
		String stmt = "{? = call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			try {
				CallableStatement cs = con.prepareCall(stmt);
				cs.registerOutParameter(1, Types.INTEGER);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bind2Parameter(cs, parameters[i], i);
				}

				cs.execute();

				result = cs.getInt(1);
				cs.close();
				// DEBUG: System.out.println(resultString);
			} finally {
				con.close();
			}
		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return result;
	}

	public String executeClobProcedure(String procedurename, Object[] parameters)
			throws Exception {
		String resultString = "";
		Clob clob = null;
		Connection con = null;
		String stmt = "{? = call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			try {
				CallableStatement cs = con.prepareCall(stmt);
				cs.registerOutParameter(1, Types.CLOB);

				for (int i = 0; i < parameters.length; i++) {
					// parameter binden
					bind2Parameter(cs, parameters[i], i);
				}

				cs.execute();

				clob = cs.getClob(1);
				resultString = clob.getSubString((long) 1, (int) clob.length());
				// resultString = cs.getString(1);
				cs.close();
				// DEBUG: System.out.println(resultString);
			} finally {
				con.close();
			}
		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return resultString;
	}

	public WrapResultSet executeProcedureRSet(String procedurename,
			Object[] parameters) throws Exception {
		/*
		 * De Oracle Stored Procedure moet een refCursor teruggeven. B.v.:
		 * 
		 * function loaddata (par1 varchar2 ,par2 varchar2) return refCursor is
		 * rc refCursor ; begin open rc for 'select * FROM SomeTable where
		 * var1=''' || pvar1 || ''' AND var2=''' || pvar2 || ''''; return rc ;
		 * end;
		 */
		ResultSet rset = null;
		WrapResultSet result = new WrapResultSet();
		Connection con = null;
		String stmt = "{? = call " + procedurename + "(";
		for (int i = 0; i < parameters.length; i++) {
			stmt += (i == 0 ? "" : ",") + "?";
		}
		stmt += ")}";
		try {
			con = getConnection();
			CallableStatement cs = con.prepareCall(stmt);
			cs.registerOutParameter(1, Types.REF);
			// cs.registerOutParameter(1, OracleTypes.CURSOR);

			for (int i = 0; i < parameters.length; i++) {
				// parameter binden
				bind2Parameter(cs, parameters[i], i);
			}
			cs.execute();

			rset = (ResultSet) cs.getObject(1);
			result.setConnection(con);
			result.setResultset(rset);
			cs.close();
			// DEBUG: System.out.println(resultString);

		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing Stored Procedure "
					+ procedurename + ".");
			throw new Exception("Database Error");
		}
		return result;
	}

	public String executeSingleResultStatement(String statement, Object[] parameters)
			throws Exception {
		String resultString = "";
		WrapResultSet rset = null;
		try {
			rset = executeQuery(statement, parameters);

			if (rset.next()) {
				resultString = rset.getString(1);
			}
		} finally {
			rset.close();
		}
		return (resultString == null ? "" : resultString);
	}

	public long executeLongResultStatement(String statement, Object[] parameters)
			throws Exception {
		long result = 0;
		WrapResultSet rset = null;
		try {
			rset = executeQuery(statement, parameters);

			if (rset.next()) {
				result = rset.getLong(1);
			}
		} finally {
			rset.close();
		}
		return result;
	}

	public double executeDoubleResultStatement(String statement, Object[] parameters)
			throws Exception {
		double result = 0;
		WrapResultSet rset = null;
		try {
			rset = executeQuery(statement, parameters);

			if (rset.next()) {
				result = rset.getDouble(1);
			}
		} finally {
			rset.close();
		}
		return result;
	}

	public String executeSingleCLOBResultStatement(String statement, Object[] parameters)
			throws Exception {
		String resultString = "";

		Clob clob = null;

		WrapResultSet rset = null;
		try {
			rset = executeQuery(statement, parameters);

			if (rset.next()) {
				clob = rset.getClob(1);
				resultString = clob.getSubString((long) 1, (int) clob.length());
			}
		} finally {
			rset.close();
		}
		return (resultString == null ? "" : resultString);
	}

	public WrapResultSet createResultSet(String statement, Object[] parameters) throws Exception {
		return executeQuery(statement, parameters) ;
	}
	
	public WrapResultSet executeQuery(String statement, Object[] parameters) throws Exception {
		PreparedStatement ps = null;
		ResultSet rset = null;
		Connection con = null;
		WrapResultSet result = new WrapResultSet();
		try {
			con = getConnection();

			ps = con.prepareStatement(statement);

			for (int i = 0; i < parameters.length; i++) {
				// parameter binden
				bindParameter(ps, parameters[i], i);
			}
			
			rset = ps.executeQuery();
			result.setConnection(con);
			result.setResultset(rset);

		} catch (SQLException se) {
			if ((con != null) && (!con.isClosed())) {
				con.close();
			}
			System.out.println("ERROR: " + se.getMessage());
			System.out.println("Error executing statement " + statement + ".");
			throw new Exception("Database Error");
		}
		return result;
	}

	
	public String getDatabaseDriver() {
		return databaseDriver;
	}

	public void setDatabaseDriver(String databaseDriver) {
		this.databaseDriver = databaseDriver;
	}

	public String getDatabaseURL() {
		return databaseURL;
	}

	public void setDatabaseURL(String databaseURL) {
		this.databaseURL = databaseURL;
	}

	public String getDatabasePassword() {
		return databasePassword;
	}

	public void setDatabasePassword(String databasePassword) {
		this.databasePassword = databasePassword;
	}

	public String getDatabaseUserName() {
		return databaseUserName;
	}

	public void setDatabaseUserName(String databaseUserName) {
		this.databaseUserName = databaseUserName;
	}

}
