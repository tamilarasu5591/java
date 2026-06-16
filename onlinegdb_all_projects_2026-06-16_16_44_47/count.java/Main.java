/******************************************************************************

                            Online Java Compiler.
                Code, Compile, Run and Debug java program online.
Write your code in this editor and press "Run" button to execute it.

*******************************************************************************/
import java.util.Scanner;
class main{
    public static void main(String[] args){
        Scanner in= new Scanner(System.in);
        int count=0;
        System.out.println("enter number:" );
        int n=in.nextInt();
        if(n!=0){
            count++;
            n=n/10;
        }
        System.out.println(" ");
    }
}