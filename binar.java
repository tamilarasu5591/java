import java.util.Scanner;
class binar{
    public static void main(String[] args){
    Scanner in = new Scanner(System.in);
    int n;
    int num;
    System.out.println("enter number:");
    n=in.nextInt();
    num=n;
    System.out.println(Integer.toBinaryString(num));
}
}
