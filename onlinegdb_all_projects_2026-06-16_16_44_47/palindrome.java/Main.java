/******************************************************************************

Welcome to GDB Online.
GDB online is an online compiler and debugger tool for C, C++, Python, Java, PHP, Ruby, Perl,
C#, OCaml, VB, Swift, Pascal, Fortran, Haskell, Objective-C, Assembly, HTML, CSS, JS, SQLite, Prolog.
Code, Compile, Run and Debug online from anywhere in world.

*******************************************************************************/
import java.util.Scanner;
class main {
    public static void main(String[] args){
    Scanner in = new Scanner(System.in);
    int num=in.nextInt();
    int original=num;
    int digit;
    int reverse=0;
    if(num!=0){
        digit=num%10;
        reverse = reverse*10+digit;
        num=num/10;
    }
    if(original==reverse){
        System.out.println("palindrome");
    }
    else{
        System.out.println("not palindrome");
    }
    }
}