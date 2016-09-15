package ethereumGen;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

public class BlockParser {
	
	Scanner sc;
	
	public BlockParser(Scanner sc){
		this.sc = sc;
	}
	
	public boolean parseHTML(File inputFile, File outputFile) throws IOException{

		BufferedReader br = new BufferedReader(new FileReader(inputFile));
		
		BufferedWriter bw = new BufferedWriter(new FileWriter(outputFile));
		
		StringBuilder sb = new StringBuilder();
		
		String line = br.readLine();
		while (line!=null){
			sb.append(line);
			line = br.readLine();
		}
		
		br.close();
		ArrayList<Transaction> txs = new ArrayList<Transaction>();
		
		String str = sb.toString();
		System.out.println(str.length());
		Gson gson = new GsonBuilder().setPrettyPrinting().create();
		
		int index = str.indexOf("There are no matching entries");
		if (index!=-1){
			bw.write(gson.toJson(txs));
			bw.close();
			return true;
		}
		
		else {
			index = str.indexOf("<table class=\"table table-hover");
			//System.out.println("index = " + index);
			if (index == -1){
				bw.close();
				return false;
			}
			
			int index2 = str.indexOf("</table>",index);
			int index3 = str.indexOf(">",index);
			str = str.substring(index3+1,index2);
		}
		
		int startRow = str.indexOf("<tr>");
		int endRow = str.indexOf("</tr>");
		
		startRow = str.indexOf("<tr>", endRow);
		endRow = str.indexOf("</tr>", startRow);
		
		//System.out.println(startRow + "    " + endRow);
		
		while (startRow!=-1&&endRow!=-1){
			Transaction tx = parseTx(str.substring(startRow+4, endRow));
			if (tx!=null){
				txs.add(tx);
			}
			else {
				System.out.println("transaction parse error in block " + inputFile.getName());
				System.out.println("press enter to continue....");
				sc.nextLine();
			} 
			startRow = str.indexOf("<tr>", endRow);
			endRow = str.indexOf("</tr>", startRow);
		}
		
		bw.write(gson.toJson(txs));
		bw.close();
		return true;
	}
	
	 
	
	public static Transaction parseTx(String str){
		
		//System.out.println(str);
		
		Transaction tx = new Transaction();
		int startIndex = str.indexOf("<td>");
		int endIndex = str.indexOf("</td>", startIndex);
		//System.out.println("startIndex and endIndex:");
		//System.out.println(startIndex + "    " + endIndex);
		if (startIndex == -1 || endIndex == -1){
			return null;
		}
		
		//TxHash
		String portion = str.substring(startIndex + 4, endIndex);
		if (portion.indexOf("fa-exclamation-circle")!=-1){
			tx.isSuccess = false;
		}
		
		int hashStart = portion.indexOf("href='/tx/");
		if (hashStart==-1) return null;
		int i=hashStart+12;
		while (true){
			if (!isHex(portion.charAt(i++))){
				break;
			}
		}
		
		tx.hash = portion.substring(hashStart+10, i-1);
		System.out.println("hash:");
		System.out.println(tx.hash);
		//block
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		
		int blockStart = portion.indexOf("href='/block/");
		if (blockStart==-1) return null;
		i=blockStart+13;
		while (true){
			if (!isHex(portion.charAt(i++))){
				break;
			}
		}
		tx.block=Integer.valueOf(portion.substring(blockStart+13,i-1));
		System.out.println("block:");
		System.out.println(tx.block);
		// age
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		
		int ageStart = portion.indexOf("title='");
		if (ageStart==-1) return null;
		int ageEnd = portion.indexOf("'",ageStart+7);
		if (ageEnd==-1) return null;
		tx.age = portion.substring(ageStart+7,ageEnd);
		// from
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		
		int fromStart = portion.indexOf("href='/address/");
		if (fromStart == -1) return null;
		fromStart += 15;
		int fromEnd = portion.indexOf("'",fromStart);
		if (fromEnd == -1) return null;
		String hrefFrom = portion.substring(fromStart,fromEnd);
		int fromStart2 = portion.indexOf(">",fromEnd);
		int fromEnd2 = portion.indexOf("<",fromStart2);
		String textFrom = portion.substring(fromStart2+1,fromEnd2);
		
		if (textFrom.equals(hrefFrom)){
			tx.from = textFrom;
		}
		else tx.from = textFrom + "-" + hrefFrom;
		System.out.println("from:");
		System.out.println(tx.from);
		// to
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		
		if (portion.indexOf("fa-file-text-o")!=-1){
			tx.toContract = true;
		}
		
		int toStart = portion.indexOf("href='/address/");
		if (toStart == -1) return null;
		toStart += 15;
		int toEnd = portion.indexOf("'",toStart);
		if (toEnd == -1) return null;
		String hrefTo = portion.substring(toStart,toEnd);
		int toStart2 = portion.indexOf(">",toEnd);
		int toEnd2 = portion.indexOf("<",toStart2);
		String textTo = portion.substring(toStart2+1,toEnd2);
		
		if (textTo.equals(hrefTo)){
			tx.to = textTo;
		}
		else tx.to = textTo + "-" + hrefTo;
		System.out.println("to:");
		System.out.println(tx.to);
		// value
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		portion = portion.replaceAll("<b>.</b>", ".");
		
		tx.value = portion;
		
		System.out.println("value");
		System.out.println(tx.value);
		// txfee
		startIndex = str.indexOf("<td>",endIndex);
		endIndex = str.indexOf("</td>", startIndex);
		portion = str.substring(startIndex + 4, endIndex);
		portion = portion.replaceAll("<b>.</b>", ".");
		
		int txfeeStart = portion.indexOf(">");
		int txfeeEnd = portion.indexOf("<",txfeeStart);
		
		tx.txFee = portion.substring(txfeeStart + 1, txfeeEnd);
		System.out.println("txfee:");
		System.out.println(tx.txFee);
		return tx;
	}
	
	public static boolean isHex(char c){
		return (c>='0'&&c<='9')||(c>='a'&&c<='f');
	}
}
