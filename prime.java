import java.util.Scanner;
class prime{
    public static void main(String[] args){
        int a;
        Scanner in = new Scanner(System.in);
        System.out.println("enter number:");
        a=in.nextInt();
        if(a > 1 && 
            (a % 2 != 0 && a % 3 != 0 && a % 5 != 0 && a % 7 != 0 && a % 11 != 0))21{
                       System.out.println("prime");
            }
        else{
               System.out.println("not a prime");
        }
        }
    }
