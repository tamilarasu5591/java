import java.util.Scanner;
class print{
    public static void main(String[] args){
        Scanner in = new Scanner(System.in);
        int n;
        System.out.println("enter the number:");
        n=in.nextInt();
        for(int i =n;i<=n;i--)
        {
            for(int j=i;j<=n;j++)
            {
                System.out.print(" ");
            }
            for(int k=1;k<=(2*i)-1;k++)
            {
                System.out.print(k);
            }
            System.out.println(" ");
        }
    }
}