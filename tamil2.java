import java.util.Scanner;
class tamil2{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int a,b;
        int lcm ;
        System.out.println("enter a:" );
        a=in.nextInt();
        System.out.println("enter b:" );
        b=in.nextInt();
        while(b!=0){
            int temp=b;
            b=a%b;
            a=temp;
        }
        int gcd=b;
        lcm=(a*b)/gcd;
        System.out.println("lcm:" +lcm);
    }
}