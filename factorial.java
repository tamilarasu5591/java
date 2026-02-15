import java.util.Scanner;
class factorial{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int n;
        System.out.println("enter number:" );
    n=in.nextInt();
    n=(n*(n-1)*(n-2)*(n-3)*1);
    System.out.println(n);
    }
}