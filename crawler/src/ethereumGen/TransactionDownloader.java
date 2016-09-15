package ethereumGen;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.Scanner;
import java.util.logging.FileHandler;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class TransactionDownloader {
	private final static String USER_AGENT = "Mozilla/5.0";
	private static Logger logger;
	private static Scanner sc = new Scanner(System.in);
	
	private String sendHttpGet(String url) throws IOException{	
    	
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		// optional default is GET
		con.setRequestMethod("GET");

		//add request header
		con.setRequestProperty("User-Agent", USER_AGENT);
		
		int responseCode = con.getResponseCode();
		logger.info("\nSending 'GET' request to URL : " + url);
		logger.info("Response Code : " + responseCode);

		if (responseCode!=200) return null;
		
		BufferedReader in = new BufferedReader(
		        new InputStreamReader(con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();

		return response.toString();
    }
	
    public static void main(String[] args) throws Exception {
    	TransactionDownloader td = new TransactionDownloader();
    	
    	logger = Logger.getLogger("MyLog");  
        FileHandler fh;  

        try {  

            // This block configure the logger with handler and formatter  
            fh = new FileHandler("D:/EthereumLogFile.log");  
            logger.addHandler(fh);
            SimpleFormatter formatter = new SimpleFormatter();  
            fh.setFormatter(formatter);  

            // the following statement is used to log any messages  
            logger.info("My first log");  

        } catch (SecurityException e) {  
            e.printStackTrace();  
        } catch (IOException e) {  
            e.printStackTrace();  
        }  
        ///*
    	int start = 46669;
    	while (start < 146403){
    		String str = td.getBlockFromWeb(start);
    		td.parseBlock(start++);
    		if (str==null){
    			break;
    		}
    		Thread.sleep(100);
    	}
    	//*/
        /*
        int blockNum = 2037812;
        td.getBlockFromWeb(blockNum);
        td.parseBlock(blockNum);
    	*/
    }
    
    public boolean parseBlock(int blockNum) throws IOException{
    	File infile = new File("./blockdata/" + blockNum);
    	File outfile = new File("./parsed/" + blockNum);
    	outfile.createNewFile();
    	BlockParser bp = new BlockParser(sc);
    	return bp.parseHTML(infile, outfile);
    }
    
    public String getBlockFromWeb(int blockNum){
    	try{
        	String url = "https://etherscan.io/txs?block=" + blockNum;
        	String result = sendHttpGet(url);
        	
        	if (result==null) return null;
        	
        	File file = new File("./blockdata/" + blockNum);
        	if (!file.exists()){
        		file.getParentFile().mkdirs();
        		file.createNewFile();
        	}
        	
        	OutputStreamWriter writer = new OutputStreamWriter(new FileOutputStream(file));
        	writer.write(result);
        	writer.close();
        	return result;
    	}catch(IOException e) {
    		e.printStackTrace();
    		return null;
    	}
    }
}
