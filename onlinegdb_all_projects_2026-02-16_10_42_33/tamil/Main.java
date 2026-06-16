/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
import java.util.Scanner;
public class Main
{
	public static void main(String[] args) {
		Scanner in = new Scanner(System.in);
		int a,b;
		System.out.println("enter number:");
		a=in.nextInt();
		System.out.println("enter number 2:");
		b=in.nextInt();
		int [] [] c=new int[a][b];
		for(int i=0;i<a;i++){
		
		    for(int j=0;j<b;j++){
		    c[i][j]=in.nextInt();
		    }
		}
		for(int i=0;i<a;i++){
		    for(int j=0;j<b;j++){
		        System.out.print(c[i][j]);
		    }
		}
	}
}