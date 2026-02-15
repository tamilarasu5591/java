import java.util.Scanner;
class tamil1{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int n;
        String m = "";
        System.out.println("enter number:");
        n=in.nextInt();
        while(n>0){
            m=(n%2)+m;
            n=n/2;
        }
        System.out.println(m);
    }
}