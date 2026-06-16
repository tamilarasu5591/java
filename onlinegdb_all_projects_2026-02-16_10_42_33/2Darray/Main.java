/******************************************************************************

Welcome to GDB Online.
  GDB online is an online compiler and debugger tool for C, C++, Python, PHP, Ruby, 
  C#, OCaml, VB, Perl, Swift, Prolog, Javascript, Pascal, COBOL, HTML, CSS, JS
  Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
import java.util.Scanner;
class Main{
    public static void main(String[] args){
        int r;
        int c;
        Scanner in =new Scanner(System.in);
        r=in.nextInt();
        int[][]a=new int[r][];
        for(int i=0;i<r;i++)
        {
            System.out.println("enter c:");
            c=in.nextInt();
            a[i]=new int[c];
            for(int j=0;j<c;j++)
            {
                a[i][j]=in.nextInt();
            }
        }
        System.out.println("matrix:");
        for(int i=0;i<a.length;i++)
        {
            for(int j=0;j<a[i].length;j++)
            {
                System.out.print(a[i][j]+" ");
            }
            System.out.println();
        }
    }
}