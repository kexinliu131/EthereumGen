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

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class TransactionDownloader {
	private final static String USER_AGENT = "Mozilla/5.0";
	
	private String sendHttpGet(String url) throws IOException{	
    	
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		// optional default is GET
		con.setRequestMethod("GET");

		//add request header
		con.setRequestProperty("User-Agent", USER_AGENT);
		
		//int responseCode = con.getResponseCode();
		//System.out.println("\nSending 'GET' request to URL : " + url);
		//System.out.println("Response Code : " + responseCode);

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
    	System.out.println(td.getBlockFromWeb(1901832));
    }
    
    public List<Transaction> getBlockFromWeb(int blockNum){
    	try{
        	String url = "https://etherchain.org/api/block/" + blockNum + "/tx";
        	String result = sendHttpGet(url);
        	//System.out.println(result);
        	Gson gson = new GsonBuilder().setPrettyPrinting().create();
        	ResponseGetBlock rgb = gson.fromJson(result, ResponseGetBlock.class);
        	//System.out.println(rgb.toString());
        	
        	if (rgb.getStatus()!=1){
        		System.out.println(rgb.getStatus());
        		return null;
        	}
        	
        	File file = new File("./blockdata/" + blockNum);
        	if (!file.exists()){
        		file.getParentFile().mkdirs();
        		file.createNewFile();
        	}
        	
        	OutputStreamWriter writer = new OutputStreamWriter(new FileOutputStream(file));
        	writer.write(gson.toJson(rgb.getData()));
        	writer.close();
        	return rgb.getData();
    	}catch(IOException e) {
    		e.printStackTrace();
    		return null;
    	}
    }
}
